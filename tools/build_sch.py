# Rebuilds CapScan5x5.kicad_sch from tools/base.placed (one MCP-placed instance per symbol type).
# Run from the project folder: python3 tools/build_sch.py
import sys, re, shutil, uuid, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import sch

OUT = 'CapScan5x5.kicad_sch'
shutil.copy('tools/base.placed', OUT)
txt = open(OUT, encoding='utf-8').read()

def inst_block(t, ref):
    for m in re.finditer(r'\n\s*\(symbol \(lib_id "[^"]+"\) \(at ', t):
        st = t.index('(symbol', m.start()); en = sch.block_end(t, st)
        if re.search(r'\(property "Reference" "%s"' % re.escape(ref), t[st:en]):
            return m.start(), en
    raise KeyError(ref)

new_blocks = []
def clone(tref, ref, x, y, rot=0, value=None, unit=1, pins=None):
    st, en = inst_block(txt, tref); b = txt[st:en]
    b = re.sub(r'\(at [\d.\-]+ [\d.\-]+ \d+\) \(unit \d+\)', f'(at {x} {y} {rot}) (unit {unit})', b, 1)
    b = b.replace(f'(property "Reference" "{tref}"', f'(property "Reference" "{ref}"')
    b = b.replace(f'(reference "{tref}")', f'(reference "{ref}")')
    b = re.sub(r'\(unit \d+\)(\s*\)\s*\)\s*\)\s*\)\s*)$', f'(unit {unit})\\1', b)
    if value is not None:
        b = re.sub(r'(\(property "Value" )"[^"]*"', lambda m: m.group(1) + f'"{value}"', b, 1)
    if pins is not None:
        b = re.sub(r'\s*\(pin "[^"]+" \(uuid "[^"]+"\)\)', '', b)
        i = b.index('(instances')
        b = b[:i] + ''.join(f'(pin "{p}" (uuid "{uuid.uuid4()}"))\n    ' for p in pins) + b[i:]
        b = re.sub(r'(\(property "Reference" "[^"]*"\s*)\(at [\d.\- ]+\)', lambda m: m.group(1) + f'(at {x} {y - 12.7} 90)', b)
        b = re.sub(r'(\(property "Value" "[^"]*"\s*)\(at [\d.\- ]+\)', lambda m: m.group(1) + f'(at {x} {y} 0)\n      (hide yes)', b)
    b = re.sub(r'\(uuid "[^"]+"\)', lambda m: f'(uuid "{uuid.uuid4()}")', b)
    new_blocks.append(b)

npwr = [3]; nflg = [1]
def pwr(kind, x, y, rot=0):
    t = {'GND': '#PWR01', '+3V3': '#PWR02', '+3.3VA': '#PWR03'}[kind]
    npwr[0] += 1; clone(t, '#PWR%02d' % npwr[0], x, y, rot)
def flag(x, y):
    nflg[0] += 1; clone('#FLG01', '#FLG%02d' % nflg[0], x, y)

XS = [40.64, 83.82, 127.0, 170.18, 213.36]
YTX, YRX = 187.96, 236.22
PX0, PY, PP = 304.8, 157.48, 7.62   # switch power-unit row
cells = []   # (ref, x, y, line label, select label, bus label)
n = 4
for row, y, bus in (('TX', YTX, 'EXC'), ('RX', YRX, 'CIN')):
    for k, x in enumerate(XS, 1):
        ref = 'U%d' % n; n += 1
        if ref != 'U4': clone('U4', ref, x, y)
        clone('U4', ref, PX0 + PP * (n - 5), PY, unit=2, pins=['2', '5'])   # power units: separate row
        pwr('GND', x + 10.16, y - 5.08, 90)
        cells.append((ref, x, y, f'{row}{k}', '~{%s_SEL%d}' % (row, k), bus))

# Reference capacitor branch: EXC - C8 - U14 - CIN (or GND when not selected)
clone('U4', 'U14', 350.52, 96.52); clone('U4', 'U14', PX0 + PP * 10, PY, unit=2, pins=['2', '5'])
pwr('GND', 360.68, 91.44, 90)
clone('C1', 'C8', 332.74, 96.52, 90, '2.2pF C0G')
# LEDs
clone('R1', 'R2', 60.96, 143.51); clone('R1', 'R3', 81.28, 143.51)
clone('D1', 'D2', 60.96, 153.67, 90, 'HB'); clone('D1', 'D3', 81.28, 153.67, 90, 'SENSE')
pwr('+3V3', 40.64, 139.7)
for x in (40.64, 60.96, 81.28): pwr('GND', x, 162.56)
# I2C pull-ups + debug header
clone('R1', 'R4', 106.68, 60.96, value='2.2k'); clone('R1', 'R5', 121.92, 60.96, value='2.2k')
pwr('+3V3', 106.68, 57.15); pwr('+3V3', 121.92, 57.15)
# J3 was placed at (127,101.6) in base; move it
pwr('+3V3', 121.92, 93.98); pwr('GND', 111.76, 101.6)
# XIAO
pwr('GND', 90.17, 93.98, 90); pwr('+3V3', 102.87, 85.09); pwr('GND', 62.23, 73.66, 180); pwr('GND', 66.04, 128.27)
# Analog supply
clone('C1', 'C2', 160.02, 74.93, value='10uF')
pwr('GND', 170.18, 78.74); pwr('GND', 160.02, 78.74)
pwr('+3V3', 129.54, 121.92); flag(139.7, 121.92)   # +3V3 flag (XIAO pins are passive)
pwr('+3.3VA', 297.18, PY - 10.16); pwr('GND', 297.18, PY + 10.16)
pwr('GND', 152.4, 121.92); flag(152.4, 121.92)
# Expander
clone('C1', 'C3', 226.06, 104.14); pwr('+3V3', 226.06, 100.33); pwr('GND', 226.06, 107.95)
pwr('+3V3', 256.54, 78.74); pwr('GND', 256.54, 129.54); pwr('GND', 238.76, 127.0)
# Switch decoupling
for i, (x, y) in enumerate(((238.76, YTX), (248.92, YTX), (238.76, YRX), (248.92, YRX)), 4):
    clone('C1', 'C%d' % i, x, y); pwr('+3.3VA', x, y - 3.81); pwr('GND', x, y + 3.81)
# Connectors, holes
clone('J1', 'J2', 279.4, YRX, value='SENSOR_RX (2.54mm socket)')
for i, x in enumerate((330.2, 340.36), 2): clone('H1', 'H%d' % i, x, 215.9)
pwr('GND', 350.52, 218.44)   # H4 is the plated, grounded hole (instance lives in base.placed)

i = txt.index('(sheet_instances')
txt = txt[:i] + '\n  '.join(b.strip() for b in new_blocks) + '\n  ' + txt[i:]
# fix template positions that differ from base
txt, n1 = re.subn(r'(\(symbol \(lib_id "Connector_Generic:Conn_01x04"\) )\(at 127(\.0)? 101\.6 0\)', r'\1(at 132.08 101.6 0)', txt)
txt, n2 = re.subn(r'(\(symbol \(lib_id "power:\+3V3"\) )\(at 139\.7 71\.12 0\)', r'\1(at 134.62 71.12 0)', txt)
txt, n3 = re.subn(r'(\(symbol \(lib_id "power:\+3\.3VA"\) )\(at 180\.34 71\.12 0\)', r'\1(at 190.5 71.12 0)', txt)
txt, n4 = re.subn(r'(\(symbol \(lib_id "power:PWR_FLAG"\) )\(at 185\.42 71\.12 0\)', r'\1(at 180.34 71.12 0)', txt)
assert n1 == 1 and n2 == 1 and n3 == 1 and n4 == 1, (n1, n2, n3, n4)
C3FP = 'Capacitor_SMD:C_0603_1608Metric'
open(OUT, 'w', encoding='utf-8').write(txt)

s = sch.Sheet(OUT)
s.setval('C2', 'Footprint', C3FP)
s.hide_misc()

def pwr_fields():
    for r, d in s.inst.items():
        if r.startswith('#PWR'):
            if d['rot'] == 90: s.field(r, 'Reference', d['x'], d['y'], hide=True); s.field(r, 'Value', d['x'] + 3.81, d['y'], 'right', ang=90)
            elif d['rot'] == 180: s.field(r, 'Reference', d['x'], d['y'], hide=True); s.field(r, 'Value', d['x'], d['y'] - 3.81)
            else: s.auto_fields(r, 'gnd' if d['lib'] == 'power:GND' else 'pwr')
        elif r.startswith('#FLG'): s.auto_fields(r, 'flag')
pwr_fields()
for r in ('R1', 'R2', 'R3', 'R4', 'R5', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7'): s.auto_fields(r, 'v2')
for r in ('D1', 'D2', 'D3'): s.auto_fields(r, 'v2r')
s.field('U1', 'Reference', 71.12, 71.12, 'left'); s.field('U1', 'Value', 71.12, 73.66, 'left')
s.field('U2', 'Reference', 198.12, 72.39, 'left'); s.field('U2', 'Value', 198.12, 74.93, 'left')
s.field('U3', 'Reference', 261.62, 76.2, 'left'); s.field('U3', 'Value', 261.62, 78.74, 'left')
s.field('FB1', 'Reference', 147.32, 68.58, ang=90); s.field('FB1', 'Value', 147.32, 74.93, ang=90)
s.field('J1', 'Reference', 279.4, YTX - 8.89); s.field('J1', 'Value', 279.4, YTX + 8.89)
s.field('J2', 'Reference', 279.4, YRX - 8.89); s.field('J2', 'Value', 279.4, YRX + 8.89)
s.field('J3', 'Reference', 132.08, 95.25); s.field('J3', 'Value', 132.08, 111.76)
for r in ('H1', 'H2', 'H3', 'H4'):
    d = s.inst[r]; s.field(r, 'Reference', d['x'], d['y'] - 3.81); s.field(r, 'Value', d['x'], d['y'] + 3.81)
s.field('H4', 'Value', 354.33, 215.9, 'left')

# ---- switch cells: labels straight on the pins, power symbols straight on the pins
for ref, x, y, line, sel, bus in cells:
    s.field(ref, 'Reference', x, y - 10.16); s.field(ref, 'Value', x + 2.54, y + 13.97)
    s.label(line, x - 10.16, y, 180); s.label(sel, x - 10.16, y + 10.16, 180); s.label(bus, x + 10.16, y + 5.08, 0)
for k in range(5):
    s.label('TX%d' % (k + 1), 274.32, YTX - 5.08 + 2.54 * k, 180)
    s.label('RX%d' % (k + 1), 274.32, YRX - 5.08 + 2.54 * k, 180)

# ---- XIAO
XL, XR = 41.91, 85.09
for y, nm in ((90.17, 'CDC_RDY'), (105.41, 'SDA'), (109.22, 'SCL')):
    s.wire((XL, y), (30.48, y)); s.label(nm, 30.48, y, 180)
for y in (93.98, 97.79, 101.6, 113.03): s.ncf(XL, y)
for y, nm in ((109.22, 'LED_HB'), (105.41, 'LED_SENSE')):
    s.wire((XR, y), (92.71, y)); s.label(nm, 92.71, y, 0)
for y in (113.03, 101.6, 90.17): s.ncf(XR, y)
s.wire((XR, 97.79), (102.87, 97.79), (102.87, 85.09))
s.wire((XR, 93.98), (90.17, 93.98))
s.wire((62.23, 78.74), (62.23, 73.66)); s.wire((66.04, 123.19), (66.04, 128.27))
for x in (50.8, 54.61, 58.42, 66.04, 69.85, 73.66, 77.47): s.ncf(x, 78.74)
for x in (60.96, 71.12): s.ncf(x, 123.19)
# ---- LEDs
for x in (40.64, 60.96, 81.28):
    s.wire((x, 147.32), (x, 149.86)); s.wire((x, 157.48), (x, 162.56))
s.wire((48.26, 139.7), (60.96, 139.7)); s.label('LED_HB', 48.26, 139.7, 0)
s.wire((68.58, 139.7), (81.28, 139.7)); s.label('LED_SENSE', 68.58, 139.7, 0)
# ---- I2C pull-ups, debug header
s.wire((106.68, 64.77), (106.68, 68.58)); s.label('SDA', 106.68, 68.58, 0)
s.wire((121.92, 64.77), (121.92, 68.58)); s.label('SCL', 121.92, 68.58, 0)
s.wire((127.0, 99.06), (121.92, 99.06), (121.92, 93.98))
s.wire((127.0, 101.6), (111.76, 101.6))
s.wire((127.0, 104.14), (121.92, 104.14)); s.label('SDA', 121.92, 104.14, 180)
s.wire((127.0, 106.68), (121.92, 106.68)); s.label('SCL', 121.92, 106.68, 180)
# ---- analog supply
s.wire((134.62, 71.12), (144.78, 71.12)); s.wire((129.54, 121.92), (139.7, 121.92))
s.wire((297.18, PY - 10.16), (PX0 + PP * 10, PY - 10.16)); s.wire((297.18, PY + 10.16), (PX0 + PP * 10, PY + 10.16))
s.text('Switch supply pins (U4-U14 unit B)', 297.18, PY - 22.86)
s.wire((149.86, 71.12), (190.5, 71.12), (190.5, 76.2))
# ---- AD7746
for y in (81.28, 83.82, 88.9, 91.44, 99.06, 101.6, 104.14, 111.76): s.ncf(177.8, y)
s.wire((177.8, 96.52), (167.64, 96.52)); s.label('CIN', 167.64, 96.52, 180)
s.wire((177.8, 109.22), (167.64, 109.22)); s.label('EXC', 167.64, 109.22, 180)
for y, nm in ((81.28, 'SCL'), (83.82, 'SDA'), (86.36, 'CDC_RDY')):
    s.wire((203.2, y), (213.36, y)); s.label(nm, 213.36, y, 0)
# ---- PCA9555
s.wire((243.84, 83.82), (236.22, 83.82)); s.label('SCL', 236.22, 83.82, 180)
s.wire((243.84, 86.36), (236.22, 86.36)); s.label('SDA', 236.22, 86.36, 180)
s.ncf(243.84, 91.44)
for y in (119.38, 121.92, 124.46): s.wire((243.84, y), (238.76, y))
s.wire((238.76, 119.38), (238.76, 127.0))
for k in range(5):
    y = 83.82 + 2.54 * k; s.wire((269.24, y), (276.86, y)); s.label('~{TX_SEL%d}' % (k + 1), 276.86, y, 0)
    y = 106.68 + 2.54 * k; s.wire((269.24, y), (276.86, y)); s.label('~{RX_SEL%d}' % (k + 1), 276.86, y, 0)
for y in (96.52, 99.06, 101.6, 121.92, 124.46): s.ncf(269.24, y)
s.wire((269.24, 119.38), (276.86, 119.38)); s.label('~{REF_SEL}', 276.86, 119.38, 0)
# ---- reference branch
s.field('U14', 'Reference', 350.52, 86.36); s.field('U14', 'Value', 353.06, 110.49)
s.field('C8', 'Reference', 332.74, 91.44, ang=90); s.field('C8', 'Value', 332.74, 101.6, ang=90)
s.label('EXC', 328.93, 96.52, 180); s.wire((336.55, 96.52), (340.36, 96.52))
s.label('~{REF_SEL}', 340.36, 106.68, 180); s.label('CIN', 360.68, 101.6, 0)
s.text('Reference capacitor: C8 (C0G, +/-0.05 pF) between EXC and CIN through U14.\\nSelect it with IO1_5 low and every TX/RX line deselected:\\nthe reading is C8 plus board stray. With nothing selected the reading is the zero.\\nTwo points = offset and gain check, through the same bus and switch type as a taxel.', 302.26, 63.5)

s.text('TX switches: selected line -> EXC (AD7746 excitation), all others -> GND', 20.32, 168.91)
s.text('RX switches: selected line -> CIN (AD7746 input), all others -> GND', 20.32, 215.9)
s.text('CapScan 5x5: absolute mutual-capacitance scanner for 5 TX x 5 RX printed skin sensors (characterization bench board).\n'
 'U2 AD7746 measures the floating capacitance between EXCA and CIN1+: +/-4.096 pF span, CAPDAC offset up to 17 pF, 11-109 ms per conversion, I2C 0x48.\n'
 'One taxel = one TX on EXC, one RX on CIN, the 8 other lines at GND (guarded measurement: the neighbours do not add to the reading).\n'
 'U3 PCA9555 (I2C 0x20) drives the 10 select lines. Select is ACTIVE LOW: write 0 to connect a line to its bus. At power-up the PCA9555 pins are inputs\n'
 'with internal 100k pull-ups, so every line sits at GND until the firmware selects one. IO0_0-4 = TX1-5, IO1_0-4 = RX1-5, IO1_5 = reference.\n'
 'CIN node budget: about 18 pF (one switch on) + 5 x 6 pF (switches off) + traces + sensor RX-to-GND. AD7746 limit is 60 pF to GND: keep the CIN trace short.\n'
 'XIAO: D0 CDC_RDY (low when a conversion is ready), D4 SDA, D5 SCL (default Wire pins), D8 LED_HB, D9 LED_SENSE. USB-C and 3.3 V regulator on the module.\n'
 'Unused AD7746 pins (REFIN, VIN, CIN1-, CIN2, EXCB) are left open as allowed by the datasheet (internal reference).', 20.32, 20.32)

s.txt = re.sub(r'\(paper "[^"]+"\)', '(paper "A3")\n\t(title_block (title "CapScan 5x5 - capacitance scanning readout") (date "2026-11-14") (rev "0.1") (company "IFT / DVHE - reSkin") (comment 1 "AD7746 CDC + 10 SPDT analog switches, 5 TX x 5 RX, values in pF") (comment 2 "Host: Seeed XIAO ESP32S3 (USB)"))', s.txt, 1)
p, nj = s.finish(); s.save()
print('junctions', nj); print('\n'.join(p) or 'connectivity ok')
