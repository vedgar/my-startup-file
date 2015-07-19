
try:
    from collections import namedtuple
except ImportError:
    from backports.nt import namedtuple

from operator import attrgetter


try:
    unichr
except NameError:
    # Python 3.x
    unichr = chr


if __debug__:
    # This is only used to validate the codes when in debug mode.
    def _code(num):
        if 0 <= num <= 31:
            return '^%c' % (ord('@') + num)
        elif 128 <= num <= 159:
            return 'ESC-%c' % (ord('@') + num - 128)
        elif num == 127:
            return '^?'
        else:
            return ''


# Descriptions are mostly taken from the UnicodeData.txt file:
#   http://www.unicode.org/Public/UNIDATA/UnicodeData.txt
#
# and the Wikipedia page:
#   http://en.wikipedia.org/wiki/C0_and_C1_control_codes
#
# with a few minor adjustments. Acronyms are taken from the Wikipedia page.

class CtrlCode(namedtuple('CtrlCode', 'acronym ordinal code description')):
    __slots__ = ()

    @property
    def symbol(self):
        if 0 <= self.ordinal <= 32:
            return unichr(0x2400 + self.ordinal)
        elif self.ordinal == 127:
            return unichr(0x2421)
        return ''

    @property
    def char(self):
        return chr(self.ordinal)


# === C0 control codes ===

C0 = [
      # fields:  acronym, ordinal, code, description
      CtrlCode('NUL', 0,   '^@',  'Null'),
      CtrlCode('SOH', 1,   '^A',  'Start of Heading'),
      CtrlCode('STX', 2,   '^B',  'Start of Text'),
      CtrlCode('ETX', 3,   '^C',  'End of Text'),
      CtrlCode('EOT', 4,   '^D',  'End of Transmission'),
      CtrlCode('ENQ', 5,   '^E',  'Enquiry'),
      CtrlCode('ACK', 6,   '^F',  'Acknowledge'),
      CtrlCode('BEL', 7,   '^G',  'Bell'),
      CtrlCode('BS',  8,   '^H',  'Backspace'),
      CtrlCode('HT',  9,   '^I',  'Horizontal Tab (Character Tabulation)'),
      CtrlCode('LF',  10,  '^J',  'Linefeed (LF) (Newline)'),
      CtrlCode('VT',  11,  '^K',  'Vertical Tab (Line Tabulation)'),
      CtrlCode('FF',  12,  '^L',  'Formfeed (FF)'),
      CtrlCode('CR',  13,  '^M',  'Carriage Return (CR)'),
      CtrlCode('SO',  14,  '^N',  'Shift Out'),
      CtrlCode('SI',  15,  '^O',  'Shift In'),
      CtrlCode('DLE', 16,  '^P',  'Data Link Escape'),
      CtrlCode('DC1', 17,  '^Q',  'Device Control 1 (XON)'),
      CtrlCode('DC2', 18,  '^R',  'Device Control 2'),
      CtrlCode('DC3', 19,  '^S',  'Device Control 3 (XOFF)'),
      CtrlCode('DC4', 20,  '^T',  'Device Control 4'),
      CtrlCode('NAK', 21,  '^U',  'Negative Acknowledge'),
      CtrlCode('SYN', 22,  '^V',  'Synchronous Idle'),
      CtrlCode('ETB', 23,  '^W',  'End of Transmission Block'),
      CtrlCode('CAN', 24,  '^X',  'Cancel'),
      CtrlCode('EM',  25,  '^Y',  'End of Medium'),
      CtrlCode('SUB', 26,  '^Z',  'Substitute'),
      CtrlCode('ESC', 27,  '^[',  'Escape'),
      CtrlCode('FS',  28,  '^\\', 'File Separator'),
      CtrlCode('GS',  29,  '^]',  'Group Separator'),
      CtrlCode('RS',  30,  '^^',  'Record Separator'),
      CtrlCode('US',  31,  '^_',  'Unit Separator'),
      # The next two codes are not strictly part of the C0 standard,
      # but are commonly included, particularly Delete.
      CtrlCode('SP',  32,  '',    'Space'),
      CtrlCode('DEL', 127, '^?',  'Delete (Rubout)'),
      ]

C0 = dict((cc.acronym, cc) for cc in C0)
assert len(C0) == 34


# === C1 control codes ===

C1 = [
      # fields:  acronym, ordinal, code, description
      CtrlCode('PAD',  128, 'ESC-@',  'Padding Character'),
      CtrlCode('HOP',  129, 'ESC-A',  'High Octet Preset'),
      CtrlCode('BPH',  130, 'ESC-B',  'Break Permitted Here'),
      CtrlCode('NBH',  131, 'ESC-C',  'No Break Here'),
      CtrlCode('IND',  132, 'ESC-D',  'Index'),
      CtrlCode('NEL',  133, 'ESC-E',  'Next Line (NEL)'),
      CtrlCode('SSA',  134, 'ESC-F',  'Start of Selected Area'),
      CtrlCode('ESA',  135, 'ESC-G',  'End of Selected Area'),
      CtrlCode('HTS',  136, 'ESC-H',  'Character Tabulation Set'),
      CtrlCode('HTJ',  137, 'ESC-I',
               'Horizontal (Character) Tabulation With Justification'),
      CtrlCode('VTS',  138, 'ESC-J',  'Vertical (Line) Tabulation Set'),
      CtrlCode('PLD',  139, 'ESC-K',  'Partial Line Down (Forward)'),
      CtrlCode('PLU',  140, 'ESC-L',  'Partial Line Up (Backward)'),
      CtrlCode('RI',   141, 'ESC-M',  'Reverse Line Feed'),
      CtrlCode('SS2',  142, 'ESC-N',  'Single-Shift 2'),
      CtrlCode('SS3',  143, 'ESC-O',  'Single-Shift 3'),
      CtrlCode('DCS',  144, 'ESC-P',  'Device Control String'),
      CtrlCode('PU1',  145, 'ESC-Q',  'Private Use 1'),
      CtrlCode('PU2',  146, 'ESC-R',  'Private Use 2'),
      CtrlCode('STS',  147, 'ESC-S',  'Set Transmit State'),
      CtrlCode('CCH',  148, 'ESC-T',  'Cancel Character'),
      CtrlCode('MW',   149, 'ESC-U',  'Message Waiting'),
      CtrlCode('SPA',  150, 'ESC-V',  'Start of Protected Area'),
      CtrlCode('EPA',  151, 'ESC-W',  'End of Protected Area'),
      CtrlCode('SOS',  152, 'ESC-X',  'Start of String'),
      # SGCI is the only four-character acronym.
      CtrlCode('SGCI', 153, 'ESC-Y',  'Single Graphic Character Introducer'),
      CtrlCode('SCI',  154, 'ESC-Z',  'Single Character Introducer'),
      CtrlCode('CSI',  155, 'ESC-[',  'Control Sequence Introducer'),
      CtrlCode('ST',   156, 'ESC-\\', 'String Terminator'),
      CtrlCode('OSC',  157, 'ESC-]',  'Operating System Command'),
      CtrlCode('PM',   158, 'ESC-^',  'Privacy Message'),
      CtrlCode('APC',  159, 'ESC-_',  'Application Program Command'),
      ]

C1 = dict((cc.acronym, cc) for cc in C1)
assert len(C1) == 32

if __debug__:
    # Check for duplicates. That's an error.
    tmp = set(C0.keys()) & set(C1.keys())
    assert not tmp, 'duplicate control code acronyms: %s' % tmp
    # Special check for SCG abbreviated acronym.
    assert 'SGC' not in C0
    assert 'SGC' not in C1
    # Validate that the ^ and ESC codes are correct.
    for C in (C0, C1):
        for cc in C.values():
            assert cc.code == _code(cc.ordinal), 'failed check: %s' % cc
    del C, cc, tmp


def lookup(obj):
    if isinstance(obj, int):
        f = attrgetter('ordinal')
    elif isinstance(obj, str):
        if obj == '':
            return SP
        obj = obj.upper()
        if obj.startswith('^') or obj.startswith('ESC'):
            f = attrgetter('code')
        else:
            f = attrgetter('acronym')
    else:
        raise TypeError('expected int or str, not %s' % type(obj).__name__)
    for C in (C0, C1):
        for c in C.values():
            if f(c) == obj:
                return c
    raise LookupError


__all__ = ['lookup', 'C0', 'C1']
__all__.extend(C0.keys())
__all__.extend(C1.keys())


assert 'lookup' not in C0 and 'lookup' not in C1
globals().update(C0)
globals().update(C1)

