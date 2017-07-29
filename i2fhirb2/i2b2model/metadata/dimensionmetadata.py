# Copyright (c) 2017, Mayo Clinic
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


# TODO: Convert metadata_xml to json and update the clients
# TODO: Formal schema vs. template
from datetime import datetime
from typing import Optional, List, Tuple

from rdflib import URIRef

from i2fhirb2.fhir.fhirspecific import FHIR

xml_template = """<?xml version="1.0"?>
<ValueMetadata>
    <Version>3.02</Version>
    <CreationDateTime>{creation_date_time}</CreationDateTime>
    <TestID>{c_basecode}</TestID>
    <TestName>{c_name}</TestName>
    <DataType>{datatype}</DataType>
    <Flagstouse/>
    <Oktousevalues>Y</Oktousevalues>
    <EnumValues>{enum_list}</EnumValues>
    <UnitValues/>
</ValueMetadata>"""

enum_entry_template = '<Val description="{}">{}</Val>'

# <CreationDateTime>03/31/2011 11:15:00</CreationDateTime>
# TODO: find the correct mapping for these
# TODO: What to do with link?
time_type = "String"
date_type = "String"
datetime_type = "String"
instant_type = "String"
id_type = "String"
bool_type = "Bool"
value_type = "String"

# TODO: implement enum
fhir_type_map = {
    FHIR.decimal: "Float",
    FHIR.nodeRole: None,
    FHIR.time: time_type,
    FHIR.positiveInt: "PosInteger",
    FHIR.dateTime: datetime_type,
    FHIR.boolean: bool_type,
    # TODO: merge these once we add value set access
    # FHIR.code: "Enum",
    FHIR.realcode: "Enum",
    FHIR.code: "String",
    FHIR.base64Binary: None,
    FHIR.markdown: "largestring",
    FHIR.date: date_type,
    FHIR.treeRoot: None,
    FHIR.link: None,
    FHIR.integer: "Integer",
    FHIR.xhtml: "largestring",
    FHIR.instant: instant_type,
    FHIR.id: id_type,
    FHIR.string: "String",
    FHIR.uri: "String",
    FHIR.value: value_type,
    FHIR.unsignedInt: "Integer",
    FHIR.index: None,
    FHIR.oid: "String",
    FHIR.Reference: "String"
}

enum_bool_values = [("True value", "True"), ("False value", "False")]


def metadata_xml(typ: URIRef, c_basecode: str, c_name: str, creation_date: datetime,
                 pos_values: Optional[List[Tuple[str, str]]] = None) -> \
        Optional[str]:
    """
    Return the metadata xml for the given data type
    :param typ: FHIR primitive type
    :param c_basecode: i2b2 code
    :param c_name: i2b2 name
    :param creation_date: date to put into the metaxml field
    :param pos_values: list of possible values if code type
    :return: XML representation of element or None if the type is not to be realized
    """
    datatype = fhir_type_map.get(typ)
    if datatype is None:
        return None

    creation_date_time = creation_date
    if datatype == "Bool":
        pos_values = enum_bool_values
        datatype = "Enum"
    if datatype == "Enum" and pos_values is not None:
        enum_list = '\n        ' + \
                    '\n        '.join(enum_entry_template.format(desc, val) for desc, val in pos_values) + "\n    "
    else:
        enum_list = ""
    return xml_template.format(**locals())
