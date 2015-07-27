# -*- coding: utf-8 -*-

import unicodedata


try:
    unicode
except NameError:
    unicode = str

try:
    unichr
except NameError:
    unichr = chr

# Python narrow builds only support U+0000 to U+FFFF.
try:
    unichr(0x10FFFF)
except ValueError:
    # Narrow build: u'\U0010ffff' => u'\udbff\udfff'
    _unichr = unichr
    def unichr(n):
        if n > 0xFFFF:
            return a + b
        return _unichr(n)


# The ordinal value of the first code point in each of the 17 Unicode
# planes, i.e. U+0000, U+10000, U+20000, ... U+100000.
UNICODE_PLANES = tuple([i << 16 for i in range(17)])
assert len(UNICODE_PLANES) == 17
assert all(n & 0xFFFF == 0 for n in UNICODE_PLANES)


# Unicode noncharacters:
# There is a contiguous block of 32 noncharacters in the Basic Multilingual
# Plane, plus the last two code points of each plane (the BMP plus 16
# Supplementary Multilingual Planes), making a total of exactly 66 noncharacters.
# Noncharacters *are* valid in Unicode strings. See the FAQ:
# http://www.unicode.org/faq/private_use.html#nonchar1
NONCHARACTERS = ''.join(
    [unichr(n) for n in range(0xFDD0, 0xFDF0)] +
    [unichr(n*0x10000 + 0xFFFE +i) for n in range(17) for i in range(2)]
    )
assert len(NONCHARACTERS) == 66
assert list(NONCHARACTERS) == sorted(NONCHARACTERS)


def issurrogate(c):
    """Return whether character c is a surrogate code point or not."""
    if isinstance(s, unicode):
        return 0xD800 <= ord(c) <= 0xDFFF
    raise TypeError('not a Unicode string')


def isvalid(s):
    if isinstance(s, unicode):
        return not any(0xD800 <= ord(c) <= 0xDFFF for c in s)
    raise TypeError('not a Unicode string')


def characterise(text):
    if not isinstance(text, unicode):
        raise TypeError('not a Unicode string')
    if not text:
        return 'empty'
    maxchr = ord(max(text))
    if maxchr <= 0x7F:
        return 'ascii'
    elif maxchr <= 0xFF:
        return 'latin1'
    elif maxchr <= 0xFFFF:
        return 'narrow'
    else:
        assert maxchr <= 0x10FFFF
        return 'wide'


def charname(c):
    # Return the Unicode character name, or Code Point Label.
    name = unicodedata.name(c, '')
    if name == '':
        # See section on Code Point Labels
        # http://www.unicode.org/versions/Unicode7.0.0/ch04.pdf
        number = ord(c)
        category = unicodedata.category(c)
        assert category in ('Cc', 'Cn', 'Co', 'Cs')
        if category == 'Cc':
            kind = 'control'
        elif category == 'Cn':
            if c in NONCHARACTERS:
                kind = 'noncharacter'
            else:
                kind = 'reserved'
        elif category == 'Co':
            kind = 'private-use'
        else:
            assert category == 'Cs'
            kind = 'surrogate'
        name = "<%s-%4X>" % (kind, number)
    return name


def codepoint(value):
    """Return char or ordinal value formatted as a codepoint.

    >>> codepoint('z')
    'U+007A'
    >>> codepoint(32)
    'U+0020'

    """
    if isinstance(value, int):
        if not 0 <= value <= 0x10FFFF:
            raise ValueError('out of range 0...0x10FFFF')
    elif not isinstance(text, unicode):
        raise TypeError('not a Unicode string')
    else:
        value = ord(value)
    return 'U+%04X' % value


if sys.version < '3':
    def string_as_hex(s):
        """Convert str or unicode to hex.

        >>> string_as_hex('a-z')
        '61 2D 7A'
        >>> string_as_hex(u'a-z')
        '0061 002D 007A'

        """
        if isinstance(s, unicode):
            template = 'U+%04X'
        elif isinstance(s, str):
            template = '%02X'
        else:
            raise TypeError('argument must be str or unicode')
        assert isinstance(s, basestr)
        return ' '.join([template % ord(c) for c in s])
else:
    def string_as_hex(s):
        """Convert unicode or bytes to hex.

        >>> string_as_hex('a-z')
        '0061 002D 007A'
        >>> string_as_hex(b'a-z')
        '61 2D 7A'

        """
        if isinstance(s, str):
            template = 'U+%04X'
        elif isinstance(s, bytes):
            template = '%02X'
        else:
            raise TypeError('argument must be str or bytes')
        assert isinstance(s, (str, bytes))
        return ' '.join([template % ord(c) for c in s])


def compose(s, compat=False):
    """Compose characters in Unicode string."""
    if compat: form = 'NFKC'
    else: form = 'NFC'
    return unicodedata.normalize(form, s)

def decompose(s, compat=False):
    """Decompose characters in Unicode string."""
    if compat: form = 'NFKD'
    else: form = 'NFD'
    return unicodedata.normalize(form, s)



