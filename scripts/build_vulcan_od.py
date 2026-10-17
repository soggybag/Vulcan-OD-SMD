"""Vulcan OD SMD - single Vulcan stage overdrive: input gain -> DRIVE -> one diode-coupled Vulcan stage (collector trimmer)
-> active Baxandall BASS/TREBLE (from The Sultan) -> VOLUME.  usage: build_vulcan_od.py <out.kicad_sch>"""
from sch import *
import sys
OUT = sys.argv[1]
g = lambda n: round(n * 2.54, 3)
s = Sheet('VulcanOD', 'A3')
FR = 'Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
FC = 'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
FC12 = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
FPOT = 'UglyFace:Potentiometer_Alpha_16mm_Vertical'
FPAD = 'Connector_Wire:SolderWire-0.5sqmm_1x01_D0.9mm_OD2.1mm'
RL = {'4M7': 'C17674', '1k': 'C17513', '4k7': 'C17673', '1M': 'C17514', '100k': 'C149504', '27k': 'C17593', '22k': 'C17560', '20k': 'C4328', '47k': 'C17713', '15k': 'C17475', '12k': 'C17444', '100': 'C17408', '10k': 'C17414', '5k1': 'C27834',
      '4k7': 'C17673', '2k2': 'C17520', '1k': 'C17513', '560': 'C28636'}
CL = {'100n': 'C49678', '47n': 'C53134', '22n': 'C1729', '100p': 'C1790', '4u7': 'C1779', '220n': 'C5378', '470p': 'C1743', '47p': 'C14857', '10n': 'C1710', '4n7': 'C1744', '1u': 'C28323', '10u': 'C15850', '22u': 'C12891'}
W = lambda *p: s.wire(*p)
P = s.P
def GND(p): s.power('GND', p)
def V9(p): s.power('+9V', p)
def lab(n, p, side='r'): s.label(n, p, side)
def Rh(ref, v, cx, y, desc=None): s.part(ref, 'Device', 'R', v, cx, y, 90, fp=FR, lcsc=RL[v], desc=desc or f'Resistor {v} 1% 0805', text='t')
def Rv(ref, v, x, cy, side='r', desc=None): s.part(ref, 'Device', 'R', v, x, cy, 0, fp=FR, lcsc=RL[v], desc=desc or f'Resistor {v} 1% 0805', text=side)
def cd(v): return {'47n': 'X7R', '22n': 'X7R 50V', '100p': 'C0G 50V', '4u7': 'X5R 25V', '220n': 'X7R 50V', '470p': 'X7R 50V', '47p': 'C0G 50V', '10n': 'X7R 50V', '4n7': 'X7R 50V', '100n': 'X7R', '1u': 'X7R 50V', '10u': 'X5R 25V', '22u': 'X5R 25V 1206'}[v]
def Ch(ref, v, cx, y, desc=None): s.part(ref, 'Device', 'C', v, cx, y, 90, fp=FC12 if v == '22u' else FC, lcsc=CL[v], desc=desc or f'Ceramic {v} {cd(v)}', text='t')
def Cv(ref, v, x, cy, side='r', desc=None): s.part(ref, 'Device', 'C', v, x, cy, 0, fp=FC12 if v == '22u' else FC, lcsc=CL[v], desc=desc or f'Ceramic {v} {cd(v)}', text=side)
Eh, Ev = Ch, Cv
def OPA(u, unit, x, y, mirror=None):
    s.part(u, 'Amplifier_Operational', 'TL072', 'TL072', x, y, 0, unit=unit, mirror=mirror, fp='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
           lcsc='C6961', desc='Dual JFET op-amp (TL072CDT)', text='ic')
def PAD(ref, name, x, y, right=False):
    s.part(ref, 'Connector_Generic', 'Conn_01x01', name, x, y, 0 if right else 180, fp=FPAD, desc=f'Wire pad: {name}', bom=False,
           text=((x + 2.54, y - 1.27), (x + 2.54, y + 1.27), 'left') if right else ((x - 2.54, y - 1.27), (x - 2.54, y + 1.27), 'right'))
    return P(ref, '1')
def POT(ref, v, name, x, y, rot=0, mirror=None, text='r'):
    if text == 'r': text = ((x + 4.445, y - 1.27), (x + 4.445, y + 1.27), 'left')
    elif text == 'l': text = ((x - 4.445, y - 1.27), (x - 4.445, y + 1.27), 'right')
    s.part(ref, 'Device', 'R_Potentiometer', v, x, y, rot, mirror=mirror, fp=FPOT, desc=f'{name} pot, 16mm, hand-soldered', text=text, extra={'Panel': name}, bom=False)
def DS(ref, x, y, rot, desc):
    s.part(ref, 'Diode', '1N4148W', '1N4148W', x, y, rot, fp='Diode_SMD:D_SOD-123', lcsc='C81598', desc=desc, text='t')
def D4148(ref, x, y, rot):
    s.part(ref, 'Diode', '1N4148W', '1N4148W', x, y, rot, fp='Diode_SMD:D_SOD-123', lcsc='C81598', desc='Output clipping diode', text='t')

def Q(ref, x, y, desc):
    s.part(ref, 'Transistor_BJT', 'BC847', 'BC847A', x, y, 0, fp='SuperFreq:SOT-23_TO-92_Combo', lcsc='C8574', desc=desc, text='r')
def VFF(p): lab('VFF', p, 'l')

def TRIM(ref, v, name, x, y, rot=0, mirror=None, text='r'):
    if text == 'r': text = ((x + 4.445, y - 1.27), (x + 4.445, y + 1.27), 'left')
    s.part(ref, 'Device', 'R_Potentiometer_Trim', v, x, y, rot, mirror=mirror, fp='Potentiometer_THT:Potentiometer_Bourns_3296W_Vertical',
           desc=f'{name} trimmer, Bourns 3296W, hand-soldered', text=text, bom=False)

# ================================================================ INPUT GAIN + DRIVE + ONE VULCAN STAGE
s.box('INPUT GAIN (U1A)  +  DRIVE  +  ONE VULCAN STAGE (Q1)', g(3), g(5), g(78), g(62))
yi = g(30)
lab('IN', (g(5), yi), 'l'); W((g(5), yi), (g(8), yi))
Rv('R1', '1M', g(8), yi + 3.81, side='l', desc='Input pull-down'); GND(P('R1', '2'))
Ch('C1', '100n', g(12.5), yi, desc='Input coupling'); W((g(8), yi), P('C1', '1'))
OPA('U1', 1, g(22), yi + g(1))
W(P('C1', '2'), (g(16), yi), P('U1', '3'))
Rv('R2', '1M', g(16), yi + 3.81, side='l', desc='Input bias to VREF (Zin ~500k)'); W(P('R2', '2'), (g(16), yi + g(4))); lab('VREF', (g(16), yi + g(4)), 'l')
W(P('U1', '2'), (g(18), yi + g(2)), (g(18), yi + g(6)))
Rh('R3', '22k', g(22.5), yi + g(6), desc='Input gain 1 + 22k/10k = 3.2 (clean)'); W((g(18), yi + g(6)), P('R3', '1'))
W(P('R3', '2'), (g(27), yi + g(6)), (g(27), yi + g(1)))
Rv('R4', '10k', g(18), yi + g(7.5) + 3.81 - g(1.5), side='l', desc='Input gain set (to VREF: DC gain stays at VREF)')
W((g(18), yi + g(6)), P('R4', '1')); W(P('R4', '2'), (g(18), yi + g(10))); lab('VREF', (g(18), yi + g(10)), 'l')
W(P('U1', '1'), (g(27), yi + g(1)), (g(29), yi + g(1)))
POT('RV1', 'A10k', 'DRIVE', g(30), yi + g(1) + 3.81, mirror='x', text=((g(27), yi + g(5.5)), (g(27), yi + g(7)), None))
W((g(29), yi + g(1)), P('RV1', '3')); GND(P('RV1', '1'))
yw = P('RV1', '2')[1]
Ch('C2', '100n', g(35), yw, desc='DRIVE into the Vulcan stage'); W(P('RV1', '2'), P('C2', '1'))
x = g(39)
W(P('C2', '2'), (x, yw))
Rv('R5', '1M', x, yw + 3.81, side='l', desc='Vulcan node to ground (keeps the diode lightly on)'); GND(P('R5', '2'))
s.part('D1', 'Diode', '1N4148W', '1N4148W', x + g(3.5), yw, 0, fp='Diode_SMD:D_SOD-123', lcsc='C81598',
       desc='Vulcan series base diode: cathode to the node, anode to the base', text='t')
W((x, yw), P('D1', '1'))
s.part('Q1', 'Transistor_BJT', 'MMBT3904', '2N5089', x + g(10), yw, 0, fp='SuperFreq:SOT-23_TO-92_Combo',
       desc='2N5089 TO-92 (E-B-C row), hand-soldered from stock; SOT-23 pads = optional MMBT5089 (C116160). Fit ONE.', text='r', bom=False)
W(P('D1', '2'), (x + g(7), yw), P('Q1', '1'))
Rv('R6', '4M7', x + g(7), yw - g(4.5), side='l', desc='Base bias from +9V'); V9(P('R6', '1')); W(P('R6', '2'), (x + g(7), yw))
xc = P('Q1', '3')[0]
Rv('R7', '4k7', xc, yw - g(6.5), side='l', desc='Collector load, fixed part (with RV2 = 4.7k-24.7k)')
W(P('Q1', '3'), (xc, yw - g(4)), P('R7', '2'))
TRIM('RV2', '20k', 'BIAS', xc, yw - g(11), text=((xc + g(2.5), yw - g(12)), (xc + g(2.5), yw - g(10.5)), 'left'))
W(P('RV2', '3'), P('R7', '1'))
W(P('RV2', '2'), (P('RV2', '2')[0], P('RV2', '1')[1]), P('RV2', '1')); V9(P('RV2', '1'))
W(P('Q1', '2'), (xc, yw + g(3)), (xc + g(3), yw + g(3)))
Rv('R8', '1k', xc, yw + g(4.5), side='l', desc='Emitter resistor'); GND(P('R8', '2'))
Cv('C3', '22u', xc + g(3), yw + g(4.5), side='r', desc='Emitter bypass'); GND(P('C3', '2'))
s.part('TP1', 'Connector', 'TestPoint', 'COLLECTOR', xc + g(4), yw - g(6), 0, fp='TestPoint:TestPoint_Pad_D1.5mm',
       desc='Set RV2 for 4.5 V here', text='r', bom=False)
W((xc, yw - g(4)), (xc + g(4), yw - g(4)), P('TP1', '1'))
Ch('C4', '1u', xc + g(11), yw - g(4), desc='Stage output coupling'); W((xc + g(4), yw - g(4)), P('C4', '1'))
W(P('C4', '2'), (g(74), yw - g(4))); lab('VUL_OUT', (g(74), yw - g(4)))
s.text('Set RV2 (BIAS) for 4.5 V at TP1 (Q1 collector), per the original Vulcan designer.', g(5), g(56))
s.text('DRIVE = 0 to x3.2 of the guitar into the stage: even-harmonic warmth at low settings, hard clipping at full.', g(5), g(58))

# ================================================================ PAD + BUFFER + ACTIVE BAXANDALL + VOLUME (from The Sultan)
s.box('PAD + BUFFER (U1B)  +  ACTIVE BAXANDALL BASS / TREBLE (U2A)  +  VOLUME', g(80), g(5), g(160), g(62))
lab('VUL_OUT', (g(83), g(20)), 'l')
Rh('R9', '100k', g(91.5), g(20), desc='Pad: 100k/15k = -18 dB (stage output up to ~7 Vpp -> <1 Vpp)'); W((g(83), g(20)), (g(88), g(20)), P('R9', '1'))
W(P('R9', '2'), (g(96), g(20)))
Rv('R10', '15k', g(96), g(20) + 3.81, side='l', desc='Pad to VREF (also biases U1B)')
W(P('R10', '2'), (g(96), g(24))); lab('VREF', (g(96), g(24)), 'l')
OPA('U1', 2, g(103), g(21))
W((g(96), g(20)), P('U1', '5'))
W(P('U1', '6'), (g(99), g(22)), (g(99), g(25)), (g(108), g(25)), (g(108), g(21)))
W(P('U1', '7'), (g(108), g(21)), (g(112), g(21)), (g(112), g(28)), (g(112), g(54)))
Rh('R11', '15k', g(115.5), g(28), desc='Bass (sets +-12 dB range)'); W((g(112), g(28)), P('R11', '1'))
POT('RV3', 'B100k', 'BASS', g(121), g(28), rot=270, text=((g(118), g(24)), (g(118), g(25.5)), None))
W(P('R11', '2'), (g(118), g(28)), P('RV3', '3'))
W(P('RV3', '1'), (g(124), g(28)), (g(126), g(28)))
Rh('R12', '15k', g(127.5), g(28), desc='Bass (keep equal to R11)'); W(P('R12', '2'), (g(146), g(28)))
Ch('C5', '10n', g(119.5), g(31), desc='Bass turnover'); Ch('C6', '10n', g(122.5), g(31), desc='Bass turnover')
W((g(118), g(28)), (g(118), g(31)), P('C5', '1')); W((g(124), g(28)), (g(124), g(31)), P('C6', '2'))
W(P('RV3', '2'), (g(121), g(31)), (g(121), g(32)))
Rv('R13', '10k', g(121), g(33.5), side='l', desc='Bass wiper to the virtual earth')
W(P('R13', '2'), (g(121), g(42)), (g(121), g(48.5)))
Ch('C7', '4n7', g(115.5), g(54), desc='Treble turnover'); W((g(112), g(54)), P('C7', '1'))
POT('RV4', 'B100k', 'TREBLE', g(121), g(54), rot=90, mirror='y', text=((g(118), g(57)), (g(118), g(58.5)), None))
W(P('C7', '2'), P('RV4', '3'))
Ch('C8', '4n7', g(126.5), g(54), desc='Treble turnover (keep equal to C7)'); W(P('RV4', '1'), P('C8', '1'))
W(P('C8', '2'), (g(146), g(54)))
Rv('R14', '4k7', g(121), g(50), side='l', desc='Treble wiper to the virtual earth')
W(P('R14', '2'), P('RV4', '2'))
W((g(121), g(48.5)), P('R14', '1'))
OPA('U2', 1, g(128), g(41))
W((g(121), g(42)), P('U2', '2'))
W(P('U2', '3'), (g(124), g(40)), (g(124), g(37))); lab('VREF', (g(124), g(37)), 'r')
W(P('U2', '1'), (g(146), g(41)))
W((g(146), g(28)), (g(146), g(41)), (g(146), g(54)))
W((g(146), g(41)), (g(148), g(41)))
Ch('C9', '1u', g(149.5), g(41), desc='Output coupling')
POT('RV5', 'A100k', 'VOLUME', g(153), g(41) + 3.81, mirror='x', text=((g(151), g(49)), (g(151), g(50.5)), None))
W(P('C9', '2'), P('RV5', '3')); GND(P('RV5', '1'))
W(P('RV5', '2'), (g(158), P('RV5', '2')[1])); lab('OUT', (g(158), P('RV5', '2')[1]))
s.text('Flat at noon (unity).  BASS +-14 dB @ 100 Hz, TREBLE +-12 dB @ 5 kHz.  Pot pin 3 (CW) = boost.', g(82), g(60.5))

# ================================================================ POWER, VREF (buffered), LED, PADS
s.box('POWER, VREF (U2B buffer), LED & PADS', g(3), g(66), g(160), g(112))
ry = g(74)
PAD('J3', '9V', g(8), ry)
s.part('D2', 'Diode', 'SS14', 'SS14', g(15), ry, 180, fp='Diode_SMD:D_SMA_Handsoldering', lcsc='C2480', desc='Series polarity protection', text='t')
W(P('J3', '1'), P('D2', '2'))
W(P('D2', '1'), (g(20), ry), (g(24), ry), (g(28), ry))
V9((g(20), ry)); s.power('PWR_FLAG', (g(24), ry))
Cv('C10', '22u', g(28), ry + 3.81, desc='+9V bulk'); GND(P('C10', '2'))
V9((g(40), ry))
Rv('R15', '100k', g(40), ry + 3.81, desc='VREF divider')
Rv('R16', '100k', g(40), ry + g(6) + 3.81, desc='VREF divider'); GND(P('R16', '2'))
W(P('R15', '2'), P('R16', '1'))
Cv('C11', '10u', g(44), ry + g(6) + 3.81, desc='VREF filter'); GND(P('C11', '2'))
OPA('U2', 2, g(54), ry + g(7))
W((g(40), ry + g(6)), (g(44), ry + g(6)), P('U2', '5'))
W(P('U2', '6'), (g(50), ry + g(8)), (g(50), ry + g(11)), (g(59), ry + g(11)), (g(59), ry + g(7)))
W(P('U2', '7'), (g(59), ry + g(7)), (g(63), ry + g(7))); lab('VREF', (g(63), ry + g(7)))
V9((g(80), ry))
Rv('R17', '4k7', g(80), ry + 3.81 + g(1), side='l', desc='LED current')
W((g(80), ry), P('R17', '1'))
s.part('D3', 'Device', 'LED', 'LED', g(80), ry + g(10), 90, fp='LED_THT:LED_D3.0mm', desc='3mm status LED, hand-soldered', text='r', bom=False)
W(P('R17', '2'), P('D3', '2'))
W(P('D3', '1'), (g(80), ry + g(14))); lab('LED_K', (g(80), ry + g(14)), 'r')
for i_, u in enumerate(('U1', 'U2')):
    xx = g(96) + i_ * g(12)
    OPA(u, 3, xx, g(84)); V9(P(u, '8')); GND(P(u, '4'))
    Cv(f'C{12 + i_}', '100n', xx + g(3), g(84), desc=f'{u} decoupling - place at the chip'); V9(P(f'C{12 + i_}', '1')); GND(P(f'C{12 + i_}', '2'))
s.part('J9', 'Connector_Generic', 'Conn_01x04', 'IN/LED/GND/OUT', g(140), g(80), 0, fp='Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',
       desc='Ribbon header 0.1": IN, LED-, GND, OUT (hand-soldered)', text=((g(142), g(79)), (g(142), g(80.5)), 'left'), bom=False)
for pn, nm in (('1', 'IN'), ('2', 'LED_K'), ('4', 'OUT')):
    q = P('J9', pn); W(q, (q[0] - g(4), q[1])); lab(nm, (q[0] - g(4), q[1]), 'l')
q = P('J9', '3'); W(q, (q[0] - g(2), q[1]))
s.power('GND', (q[0] - g(2), q[1])); sym = s.syms[-1]; find1(sym, 'at')[3] = 270
for pr in find(sym, 'property'):
    if pr[1] == 'Value':
        find1(pr, 'at')[1:4] = [q[0] - g(2) - 2.6, q[1], 90]; find1(pr, 'effects').append([Sym('justify'), Sym('left')])
for i_, (ref, name) in enumerate((('J4', 'G'), ('J5', 'IG'), ('J6', 'OG'))):
    y = g(90) + i_ * g(3)
    j = PAD(ref, name, g(124), y); W(j, (g(128), y)); GND((g(128), y))
    if ref == 'J4': s.power('PWR_FLAG', (g(127), y))

s.write(OUT, {'title': 'Vulcan OD SMD', 'date': '2026-09-29', 'rev': '1.0 draft',
              'company': 'Super-Freq',
              'comments': ['Single Vulcan stage overdrive (Vulcan roadmap spin-off)',
                           'Input gain x3.2 > DRIVE > one diode-coupled 2N5089 stage (BIAS trim) > active Baxandall > VOLUME',
                           'DRAFT for review']})
print('ok', len(s.syms), 'symbols')
