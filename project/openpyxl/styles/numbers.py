from __future__ import absolute_import
# Copyright (c) 2010-2014 openpyxl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# @license: http://www.opensource.org/licenses/mit-license.php
# @author: see AUTHORS file

import re

from .hashable import HashableObject

BUILTIN_FORMATS = {
    0: 'General',
    1: '0',
    2: '0.00',
    3: '#,##0',
    4: '#,##0.00',
    5: '"$"#,##0_);("$"#,##0)',
    6: '"$"#,##0_);[Red]("$"#,##0)',
    7: '"$"#,##0.00_);("$"#,##0.00)',
    8: '"$"#,##0.00_);[Red]("$"#,##0.00)',
    9: '0%',
    10: '0.00%',
    11: '0.00E+00',
    12: '# ?/?',
    13: '# ??/??',
    14: 'mm-dd-yy',
    15: 'd-mmm-yy',
    16: 'd-mmm',
    17: 'mmm-yy',
    18: 'h:mm AM/PM',
    19: 'h:mm:ss AM/PM',
    20: 'h:mm',
    21: 'h:mm:ss',
    22: 'm/d/yy h:mm',

    37: '#,##0_);(#,##0)',
    38: '#,##0_);[Red](#,##0)',
    39: '#,##0.00_);(#,##0.00)',
    40: '#,##0.00_);[Red](#,##0.00)',

    41: '_(* #,##0_);_(* \(#,##0\);_(* "-"_);_(@_)',
    42: '_("$"* #,##0_);_("$"* \(#,##0\);_("$"* "-"_);_(@_)',
    43: '_(* #,##0.00_);_(* \(#,##0.00\);_(* "-"??_);_(@_)',

    44: '_("$"* #,##0.00_)_("$"* \(#,##0.00\)_("$"* "-"??_)_(@_)',
    45: 'mm:ss',
    46: '[h]:mm:ss',
    47: 'mmss.0',
    48: '##0.0E+0',
    49: '@', }

BUILTIN_FORMATS_REVERSE = dict(
        [(value, key) for key, value in BUILTIN_FORMATS.items()])

FORMAT_GENERAL = BUILTIN_FORMATS[0]
FORMAT_TEXT = BUILTIN_FORMATS[49]
FORMAT_NUMBER = BUILTIN_FORMATS[1]
FORMAT_NUMBER_00 = BUILTIN_FORMATS[2]
FORMAT_NUMBER_COMMA_SEPARATED1 = BUILTIN_FORMATS[4]
FORMAT_NUMBER_COMMA_SEPARATED2 = '#,##0.00_-'
FORMAT_PERCENTAGE = BUILTIN_FORMATS[9]
FORMAT_PERCENTAGE_00 = BUILTIN_FORMATS[10]
FORMAT_DATE_YYYYMMDD2 = 'yyyy-mm-dd'
FORMAT_DATE_YYYYMMDD = 'yy-mm-dd'
FORMAT_DATE_DDMMYYYY = 'dd/mm/yy'
FORMAT_DATE_DMYSLASH = 'd/m/y'
FORMAT_DATE_DMYMINUS = 'd-m-y'
FORMAT_DATE_DMMINUS = 'd-m'
FORMAT_DATE_MYMINUS = 'm-y'
FORMAT_DATE_XLSX14 = BUILTIN_FORMATS[14]
FORMAT_DATE_XLSX15 = BUILTIN_FORMATS[15]
FORMAT_DATE_XLSX16 = BUILTIN_FORMATS[16]
FORMAT_DATE_XLSX17 = BUILTIN_FORMATS[17]
FORMAT_DATE_XLSX22 = BUILTIN_FORMATS[22]
FORMAT_DATE_DATETIME = 'd/m/y h:mm'
FORMAT_DATE_TIME1 = BUILTIN_FORMATS[18]
FORMAT_DATE_TIME2 = BUILTIN_FORMATS[19]
FORMAT_DATE_TIME3 = BUILTIN_FORMATS[20]
FORMAT_DATE_TIME4 = BUILTIN_FORMATS[21]
FORMAT_DATE_TIME5 = BUILTIN_FORMATS[45]
FORMAT_DATE_TIME6 = BUILTIN_FORMATS[21]
FORMAT_DATE_TIME7 = 'i:s.S'
FORMAT_DATE_TIME8 = 'h:mm:ss@'
FORMAT_DATE_TIMEDELTA = '[hh]:mm:ss'
FORMAT_DATE_YYYYMMDDSLASH = 'yy/mm/dd@'
FORMAT_CURRENCY_USD_SIMPLE = '"$"#,##0.00_-'
FORMAT_CURRENCY_USD = '$#,##0_-'
FORMAT_CURRENCY_EUR_SIMPLE = '[$EUR ]#,##0.00_-'

class NumberFormat(HashableObject):
    """Numer formatting for use in styles."""

    FORMAT_GENERAL = FORMAT_GENERAL
    FORMAT_TEXT = FORMAT_TEXT
    FORMAT_NUMBER = FORMAT_NUMBER
    FORMAT_NUMBER_00 = FORMAT_NUMBER_00
    FORMAT_NUMBER_COMMA_SEPARATED1 = FORMAT_NUMBER_COMMA_SEPARATED1
    FORMAT_NUMBER_COMMA_SEPARATED2 = FORMAT_NUMBER_COMMA_SEPARATED2
    FORMAT_PERCENTAGE = FORMAT_PERCENTAGE
    FORMAT_PERCENTAGE_00 = FORMAT_PERCENTAGE_00
    FORMAT_DATE_YYYYMMDD2 = FORMAT_DATE_YYYYMMDD2
    FORMAT_DATE_YYYYMMDD = FORMAT_DATE_YYYYMMDD
    FORMAT_DATE_DDMMYYYY = FORMAT_DATE_DDMMYYYY
    FORMAT_DATE_DMYSLASH = FORMAT_DATE_DMYSLASH
    FORMAT_DATE_DMYMINUS = FORMAT_DATE_DMYMINUS
    FORMAT_DATE_DMMINUS = FORMAT_DATE_DMMINUS
    FORMAT_DATE_MYMINUS = FORMAT_DATE_MYMINUS
    FORMAT_DATE_XLSX14 = FORMAT_DATE_XLSX14
    FORMAT_DATE_XLSX14 = FORMAT_DATE_XLSX14
    FORMAT_DATE_XLSX14 = FORMAT_DATE_XLSX14
    FORMAT_DATE_XLSX14 = FORMAT_DATE_XLSX14
    FORMAT_DATE_XLSX22 = FORMAT_DATE_XLSX22
    FORMAT_DATE_DATETIME = FORMAT_DATE_DATETIME
    FORMAT_DATE_TIME1 = FORMAT_DATE_TIME1
    FORMAT_DATE_TIME2 = FORMAT_DATE_TIME2
    FORMAT_DATE_TIME3 = FORMAT_DATE_TIME3
    FORMAT_DATE_TIME4 = FORMAT_DATE_TIME4
    FORMAT_DATE_TIME5 = FORMAT_DATE_TIME5
    FORMAT_DATE_TIME6 = FORMAT_DATE_TIME6
    FORMAT_DATE_TIME7 = FORMAT_DATE_TIME7
    FORMAT_DATE_TIME8 = FORMAT_DATE_TIME8
    FORMAT_DATE_TIMEDELTA = FORMAT_DATE_TIMEDELTA
    FORMAT_DATE_YYYYMMDDSLASH = FORMAT_DATE_YYYYMMDDSLASH
    FORMAT_CURRENCY_USD_SIMPLE = FORMAT_CURRENCY_USD_SIMPLE
    FORMAT_CURRENCY_USD = FORMAT_CURRENCY_USD
    FORMAT_CURRENCY_EUR_SIMPLE = FORMAT_CURRENCY_EUR_SIMPLE

    _BUILTIN_FORMATS = BUILTIN_FORMATS

    __fields__ = ('format_code',)
    __slots__ = __fields__

    def __init__(self, format_code=FORMAT_GENERAL):
        self.format_code = format_code

    def __eq__(self, other):
        if isinstance(other, NumberFormat):
            return self.format_code == other.format_code
        return self.format_code == other

    def __hash__(self):
        return super(NumberFormat, self).__hash__()

    def builtin_format_code(self, index):
        """Return one of the standard format codes by index."""
        return builtin_format_code(index)

    def is_builtin(self):
        """Check if a format code is a standard format code."""
        return is_builtin(self.format_code)

    def builtin_format_id(self, fmt):
        """Return the id of a standard style."""
        return builtin_format_id(fmt)

    def is_date_format(self):
        """Check if the number format is actually representing a date."""
        return is_date_format(self.format_code)


DATE_INDICATORS = 'dmyhs'
BAD_DATE_RE = re.compile(r'(\[|").*[dmhys].*(\]|")')

def is_date_format(fmt):
    if fmt is None:
        return False
    if any([x in fmt for x in DATE_INDICATORS]):
        return not BAD_DATE_RE.search(fmt)
    return False


def is_builtin(fmt):
    return fmt in BUILTIN_FORMATS.values()


def builtin_format_code(index):
    """Return one of the standard format codes by index."""
    return BUILTIN_FORMATS[index]


def builtin_format_id(fmt):
    """Return the id of a standard style."""
    return BUILTIN_FORMATS_REVERSE.get(fmt)
