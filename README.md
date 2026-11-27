# CapScan 5x5

Bench readout board that scans a 5 TX x 5 RX printed skin sensor (reSkin / Skin-On) and returns the mutual capacitance of each taxel in pF. Sibling of [Muca_board](../Muca_board) (MUCA2), which returns raw FocalTech counts.

Status: rev 0.1. Schematic complete (ERC 0 errors). Board placed and fully routed (35/35 nets, KiCadRoutingTools checker: 0 violations, all nets connected). Still to do in KiCad: fill the B.Cu GND zone (press B), run KiCad's own DRC, silkscreen. Not fabricated.

## How it measures

One taxel at a time: the selected TX line is connected to the AD7746 excitation output (EXCA), the selected RX line to its input (CIN1+), and the 8 other lines are grounded. The AD7746 measures the floating capacitance between EXC and CIN; capacitance to ground is rejected (up to its 60 pF limit), so the grounded neighbours do not add to the reading.

| Block | Part | Notes |
|---|---|---|
| CDC | AD7746ARUZ (TSSOP-16) | 24-bit, +/-4.096 pF span around a CAPDAC offset of 0 to 17 pF, 11 to 109 ms per conversion, I2C 0x48. Internal reference; REFIN, VIN, CIN1-, CIN2, EXCB unused. |
| Line switches | 10x 74LVC1G3157 (SC-70-6) | One SPDT per line: B0 -> bus (EXC or CIN), B1 -> GND. |
| Reference | C8 2.2 pF C0G +/-0.05 pF (0402) + U14 74LVC1G3157 | C8 sits between EXC and CIN through its own switch, selected by IO1_5 (active low). Same bus and switch type as a taxel, so it checks gain including the CIN loading. |
| Select | PCA9555PW (TSSOP-24) | I2C 0x20. IO0_0-4 = TX1-5, IO1_0-4 = RX1-5, IO1_5 = reference. Select is active LOW. Power-up state is input with internal pull-up, so all lines are grounded until the firmware selects one. |
| Host | Seeed XIAO ESP32S3 (SMD) | USB-C and 3.3 V regulator on the module. |
| Power | XIAO 3V3 -> ferrite -> +3.3VA | +3.3VA feeds the AD7746 and the switches. |
| Sensor I/O | 2x 2.54 mm right-angle socket, 1x5 | J1 TX1-5, J2 RX1-5, same Clincher tail as MUCA2. |
| Grounding | H4 | Plated M3 hole on GND for a shield or the test fixture. H1-H3 are unplated. |
| Debug | PWR, HB, SENSE LEDs, 4-pin I2C header | J3: 3V3, GND, SDA, SCL. |

## XIAO pin map

| XIAO pin | GPIO | Function |
|---|---|---|
| D0 | GPIO1 | CDC_RDY (low when a conversion is ready) |
| D4 / D5 | GPIO5 / GPIO6 | SDA / SCL (default `Wire` pins), 2.2 kohm pull-ups |
| D8 / D9 | GPIO7 / GPIO8 | LED_HB / LED_SENSE (active high) |

## Scan sequence (firmware)

1. PCA9555: write output registers to 0xFF, then configure IO0_0-4 and IO1_0-5 as outputs.
2. For each taxel: clear the TX bit and the RX bit, wait about 1 ms, start a single conversion, wait for CDC_RDY, read 24 bits, set the two bits again.
3. C[pF] = (code - 0x800000) / 0x800000 * 4.096 + CAPDAC offset.

4. Calibration: with nothing selected, read the zero (board stray). Then clear only IO1_5 and read the reference: gain = C8 / (reference - zero). Repeat at the start of each session and when temperature changes.

A full 25-taxel frame takes about 0.3 s at the fastest setting and about 2.7 s at the lowest-noise one.

## Layout

48 x 47 mm, 2 layers, all parts on top, symmetric about the centre line. Top to bottom: sensor sockets (RX left, TX right), one switch directly under each socket pin with its row decoupling at both ends, AD7746 on the centre line between the two rows (CIN and EXC buses a few mm long), PCA9555 under the TX row, XIAO on the bottom edge with USB facing out, LEDs left of it and the I2C header right. The area under the RX row is left empty on purpose: it is the quiet zone around CIN.

## Open points

- Routing: sensor lines, GND vias, CIN/EXC buses and the reference branch are hand-laid (`tools/prelay.py`); the rest is autorouted with KiCadRoutingTools 0.24 (track 0.2 mm, power 0.3 mm, via 0.6/0.3 mm, clearance 0.15 mm requested, 0.144 mm minimum delivered, no via-in-pad). The autorouted part is functional, not pretty: the RX select lines cross the empty zone under the RX row on F.Cu, and select lines and +3.3VA cut the B.Cu plane in places.
- Rebuild order if the placement changes: `tools/place.py`, strip copper, `tools/prelay.py`, then route_planes.py (GND on B.Cu) and route.py with --keep-input-copper.
- CIN node capacitance to ground: about 18 pF (one switch on) + 5 x 6 pF (switches off) + traces + the sensor RX line to the grounded TX lines. The AD7746 limit is 60 pF. The switch values are from memory of the Nexperia datasheet: check them, and measure the gain error with a known C0G capacitor on a socket.
- C8 gives a repeatable reference, not a traceable one: its tolerance is 0.05 pF but the pads and the switch add stray of the same order. For absolute values, measure C8 in place once with an LCR meter (or compare with a known external C0G on a socket) and store that number.
- Taxel capacitance above 21 pF (17 pF CAPDAC + 4 pF) is out of range without the range-extension circuit of ADI CN-0552.
- No CAN (bench instrument). Add the MUCA2 CAN sheet if it has to go on a prosthesis.
- Silkscreen, 3D check of socket direction.

## Files

- `CapScan5x5.kicad_pro` - project (single A3 sheet)
- `CapScan.kicad_sym`, `CapScan.pretty/` - XIAO ESP32S3 symbol and footprint (copied from MUCA2)
- `tools/build_sch.py` - regenerates the schematic wiring and layout from `tools/base.placed` (run from this folder). Delete `tools/` once the schematic is edited by hand.
