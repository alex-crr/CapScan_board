## KiCad 10 ERC & DRC Report — `CapScan5x5`

> [!WARNING]
> **0 errors**, but **532 warning(s)** detected (156 ERC, 376 DRC).

- **KiCad Version:** `10.0.8`
- **Gate Policy:** Non-blocking — errors are highlighted via alerts & GitHub annotations without stopping the build.

| Check | Status | Errors | Warnings | Exclusions |
| :--- | :---: | :---: | :---: | :---: |
| **ERC** (`CapScan5x5.kicad_sch`) | ✅ PASS | **0** | 156 | 0 |
| **DRC** (`CapScan5x5.kicad_pcb`) | ✅ PASS | **0** | 376 | 0 |
| ↳ PCB Rules | — | 0 | 226 | — |
| ↳ Unconnected Items | — | 0 | 0 | — |
| ↳ Schematic Parity | — | 0 | 150 | — |

<details><summary>⚠️ ERC Warnings</summary>

- `lib_symbol_issues`: **97**
- `footprint_link_issues`: **48**
- `pin_to_pin`: **11**

1. **`lib_symbol_issues`** [/]: The current configuration does not include the symbol library 'power' (Symbol #PWR15 [+3V3] @ (40.64, 139.70 mm))
2. **`footprint_link_issues`** [/]: The current configuration does not include the footprint library 'Resistor_SMD' (Symbol R1 [R] @ (40.64, 143.51 mm))
3. **`lib_symbol_issues`** [/]: The current configuration does not include the symbol library 'Device' (Symbol R1 [R] @ (40.64, 143.51 mm))
4. **`footprint_link_issues`** [/]: The current configuration does not include the footprint library 'LED_SMD' (Symbol D1 [LED] @ (40.64, 153.67 mm))
5. **`lib_symbol_issues`** [/]: The current configuration does not include the symbol library 'Device' (Symbol D1 [LED] @ (40.64, 153.67 mm))
6. **`lib_symbol_issues`** [/]: The current configuration does not include the symbol library 'power' (Symbol #PWR16 [GND] @ (40.64, 162.56 mm))
7. **`footprint_link_issues`** [/]: The current configuration does not include the footprint library 'Package_TO_SOT_SMD' (Symbol U4 [74LVC1G3157] @ (40.64, 187.96 mm))
8. **`lib_symbol_issues`** [/]: The current configuration does not include the symbol library '74xGxx' (Symbol U4 [74LVC1G3157] @ (40.64, 187.96 mm))
9. **`footprint_link_issues`** [/]: The current configuration does not include the footprint library 'Package_TO_SOT_SMD' (Symbol U9 [74LVC1G3157] @ (40.64, 236.22 mm))
10. **`lib_symbol_issues`** [/]: The current configuration does not include the symbol library '74xGxx' (Symbol U9 [74LVC1G3157] @ (40.64, 236.22 mm))
11. **`lib_symbol_issues`** [/]: The current configuration does not include the symbol library 'power' (Symbol #PWR04 [GND] @ (50.80, 182.88 mm))
12. **`pin_to_pin`** [/]: Pins of type Bidirectional and Power output are connected (Symbol U4 Pin 1 [Bidirectional, Line] @ (50.80, 182.88 mm) — Symbol #FLG03 Pin 1 [Power output, Line] @ (152.40, 121.92 mm))
13. **`lib_symbol_issues`** [/]: The current configuration does not include the symbol library 'power' (Symbol #PWR09 [GND] @ (50.80, 231.14 mm))
14. **`pin_to_pin`** [/]: Pins of type Bidirectional and Power output are connected (Symbol U9 Pin 1 [Bidirectional, Line] @ (50.80, 231.14 mm) — Symbol #FLG03 Pin 1 [Power output, Line] @ (152.40, 121.92 mm))
15. **`footprint_link_issues`** [/]: The current configuration does not include the footprint library 'Resistor_SMD' (Symbol R2 [R] @ (60.96, 143.51 mm))

_...and 141 more (see full JSON report artifact)._

</details>

<details><summary>⚠️ DRC Warnings</summary>

- `net_conflict`: **109**
- `silk_over_copper`: **80**
- `silk_edge_clearance`: **62**
- `silk_overlap`: **46**
- `lib_footprint_issues`: **37**
- `footprint_symbol_field_mismatch`: **37**
- `footprint_symbol_mismatch`: **4**
- `text_height`: **1**

1. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Reference field of H2 @ (144.50, 100.35 mm))
2. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (109.43, 96.91 mm))
3. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (112.03, 96.91 mm))
4. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (114.57, 96.91 mm))
5. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (117.11, 96.91 mm))
6. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (119.65, 96.91 mm))
7. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (119.77, 96.91 mm))
8. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (119.89, 96.91 mm))
9. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (120.00, 96.91 mm))
10. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (120.12, 96.91 mm))
11. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (120.24, 96.91 mm))
12. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (120.36, 96.91 mm))
13. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (120.48, 96.91 mm))
14. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (120.59, 96.91 mm))
15. **`silk_edge_clearance`**: Silkscreen clipped by board edge (Segment on Edge.Cuts @ (103.00, 100.00 mm) — Segment of J2 on F.Silkscreen @ (120.71, 96.91 mm))

_...and 361 more (see full JSON report artifact)._

</details>
