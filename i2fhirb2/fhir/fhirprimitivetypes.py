# Copyright (c) 2018, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the Mayo Clinic nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
from datetime import datetime
from typing import Optional, Dict, Callable

from rdflib import Literal, URIRef, XSD

from i2fhirb2.i2b2model.data.i2b2observationfact import ValueTypeCd, valuetype_text, valuetype_blob, valuetype_date, \
    valuetype_number


class I2B2Value:
    """ Representation of th Value portion of an I2B2 Observation Fact"""
    def __init__(self, tval_char: str, valtype: ValueTypeCd= valuetype_text, nval_num: Optional[float]=None,
                 observation_blob: Optional[str]=None) -> None:
        self.tval_char = tval_char
        self.valtype = valtype
        self.nval_num = nval_num
        self.observation_blob = observation_blob

    def __repr__(self) -> str:
        bval = f"{self.observation_blob[:10]}...{self.observation_blob[-10:]}" \
            if self.observation_blob and len(self.observation_blob) > 20 \
            else self.observation_blob
        return f'I2B2Value("{self.tval_char}", ValueTypeCd("{self.valtype.code}"), {self.nval_num}, {bval})'

    def __eq__(self, other: "I2B2Value"):
        return repr(self) == repr(other)


def filter_literal(val: Literal) -> str:
    return format(str(val).replace('\n', '\\n').replace(r'\t', '\\t'))


def blob_val(val: Literal) -> I2B2Value:
    return I2B2Value("", valuetype_blob, observation_blob='"' + filter_literal(val) + '"')


def text_val(val: Literal) -> I2B2Value:
    return I2B2Value(filter_literal(val))


def date_val(val: Literal) -> I2B2Value:
    dt = val.value
    nval_num = (dt.year * 10000) + (dt.month * 100) + dt.day + \
               (((dt.hour / 100.0) + (dt.minute / 10000.0)) if isinstance(dt, datetime) else 0)
    return I2B2Value(dt.strftime('%Y-%m-%d %H:%M'), valuetype_date, nval_num)


def decimal_val(val: Literal) -> I2B2Value:
    return I2B2Value("E", valuetype_number, float(val.value))


def time_val(val: Literal) -> I2B2Value:
    # TODO: Proposed format.  Verify w/ i2b2 community
    tv = val.value
    nval_num = (tv.hour / 100.0) + (tv.minute / 10000.0) + (tv.second / 1000000.0)
    return I2B2Value(str(val.value), valuetype_date, nval_num)


# Conversion table from XSD data type to corresponding i2b2 field
# TODO: time has no analog in i2b2 - should it?
literal_conversions: Dict[URIRef, Callable[[Literal], I2B2Value]] = {
    XSD.base64Binary: blob_val,
    XSD.boolean: text_val,
    XSD.date: date_val,
    XSD.dateTime: date_val,
    XSD.decimal: decimal_val,
    XSD.gYear: date_val,
    XSD.gYearMonth: date_val,
    XSD.integer: decimal_val,
    XSD.nonNegativeInteger: decimal_val,
    XSD.positiveInteger: decimal_val,
    XSD.time: time_val
}


def i2b2_primitive(val: Literal) -> I2B2Value:
    return literal_conversions[val.datatype](val) if val.datatype and val.datatype in literal_conversions \
        else text_val(val)
