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
from datetime import datetime
from typing import List, Optional, Union

from rdflib import URIRef, Graph, BNode, RDF, XSD
from rdflib.term import Node, Literal

from i2fhirb2.fhir.fhirspecific import concept_code, FHIR, composite_modifier
from i2fhirb2.i2b2model.i2b2observationfact import ObservationFact, ObservationFactKey, valuetype_blob, valuetype_text, \
    valuetype_date, valuetype_number, valuetype_novalue
from i2fhirb2.sqlsupport.dynobject import DynElements


def literal_val(val: Literal) -> str:
    # TODO: Escape line feeds, tabs and the like
    return '"{}"'.format(str(val).replace('\n', '\\n').replace(r'\t', '\\t'))


def boolean_val(val: Literal) -> str:
    return val.value


def date_val(val: Literal) -> datetime:
    return val.value


def datetime_val(val: Literal) -> datetime:
    return datetime.strptime(val.value,'%Y-%m-%dT%H:%M:%SZ')


def decimal_val(val: Literal) -> float:
    return float(val.value)


def gyear_val(val: Literal) -> datetime:
    return datetime.strptime(val.value, '%Y')


def gYearMonth_val(val: Literal) -> datetime:
    return datetime.strptime(val.value, '%Y-%m')


def time_val(val: Literal) -> datetime:
    return datetime.strptime(val.value, '%H:%M:%S')


literal_conversions = {
    XSD.base64Binary: (literal_val, valuetype_blob),
    XSD.boolean: (boolean_val, valuetype_text),
    XSD.date: (date_val, valuetype_date),
    XSD.dateTime: (datetime_val, valuetype_date),
    XSD.decimal: (decimal_val, valuetype_number),
    XSD.gYear: (gyear_val, valuetype_date),
    XSD.gYearMonth: (gYearMonth_val, valuetype_date),
    XSD.integer: (decimal_val, valuetype_number),
    XSD.nonNegativeInteger: (decimal_val, valuetype_number),
    XSD.positiveInteger: (decimal_val, valuetype_number),
    XSD.time: (time_val, valuetype_date)}


class FHIRObservationFact(ObservationFact):
    _t = DynElements(ObservationFact)

    def __init__(self, g: Graph, ofk: ObservationFactKey, subject: URIRef, predicate: URIRef, object: Node):
        """
        Construct an o
        :param g:
        :param ofk:
        :param subject:
        :param predicate:
        :param object:
        """
        super().__init__(ofk, concept_code(predicate))
        self.fhir_primitive(g, object)

    @staticmethod
    def is_primitive(g: Graph, obj:Optional[Node]) -> bool:
        if obj is None or not isinstance(obj, BNode):
            return False
        obj_val = g.value(obj, FHIR.value)
        return obj_val is not None and isinstance(obj_val, Literal)

    def fhir_primitive(self, g: Graph, obj: Optional[Node]) -> None:
        assert(self.is_primitive(g, obj))
        val = g.value(obj, FHIR.value)
        if val.datatype in literal_conversions:
            f, t = literal_conversions[val.datatype]
            if t == valuetype_text:
                self._tval_char = f(val)
            elif t == valuetype_number:
                self._nval_num = f(val)
            elif t == valuetype_blob:
                self._observation_blob = f(val)
            elif t == valuetype_date:
                dt = f(val)
                self._tval_char = dt.strftime('%Y-%m-%d %H:%M')
                self._nval_num = (dt.year * 10000) + (dt.month * 100) + dt.day + \
                                 ( ((dt.hour / 100.0) + (dt.minute / 10000.0)) if isinstance(dt, datetime) else 0)
            else:
                self._tval_char = f(val)
            self._valtype_cd = t.code
        else:
            self._tval_char = str(val.value)
            self._valtype_cd = valuetype_text.code


class FHIRObservationFactFactory:

    special_processing_list = {RDF.type: None, FHIR.nodeRole: None}

    def __init__(self, g: Graph, ofk: ObservationFactKey, subject: Optional[URIRef]):
        self.g = g
        self.ofk = ofk
        self.facts = []                                             # type: List[FHIRObservationFact]
        for s in {subject} if subject else self.g.subjects(FHIR.nodeRole, FHIR.treeRoot):
            self.facts += self.generate_facts(s)

    def generate_facts(self, subject: URIRef) -> List[FHIRObservationFact]:
        rval = []               # type: List[FHIRObservationFact]
        for conc, obj in self.g.predicate_objects(subject):
            if conc not in self.special_processing_list:
                if FHIRObservationFact.is_primitive(self.g, obj):
                    rval.append(FHIRObservationFact(self.g, self.ofk, subject, conc, obj))
                else:
                    for mod, modobj in self.g.predicate_objects(obj):
                        if FHIRObservationFact.is_primitive(self.g, modobj):
                            obsfact = FHIRObservationFact(self.g, self.ofk, subject, conc, modobj)
                            obsfact._modifier_cd = concept_code(mod)
                            rval.append(obsfact)
                        else:
                            for emod, emodobj in self.g.predicate_objects(modobj):
                                if FHIRObservationFact.is_primitive(self.g, emodobj):
                                    modfact = FHIRObservationFact(self.g, self.ofk, subject, conc, emodobj)
                                    modfact._modifier_cd = concept_code(composite_modifier(mod, emod))
                                    rval.append(modfact)
                                else:
                                    print("RECURSE YOU {} {}".format(mod, emod))
        return rval