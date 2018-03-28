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
from fhirtordf.rdfsupport.namespaces import namespace_for
from i2b2model.metadata.i2b2conceptdimension import ConceptDimension
from rdflib import Graph, URIRef
from rdflib.namespace import split_uri

from i2fhirb2.fhir.fhirspecific import concept_path, concept_code


class FHIRConceptDimension(ConceptDimension):
    graph: Graph = None

    def __init__(self, subject: URIRef, subject_name: str, base_path: str = '\\') -> None:
        """ FHIR wrapper for CommonDimension

        :param subject: URI of the subject
        :param subject_name: name of subject
        :param base_path: base path of items
        """
        ns, code = split_uri(subject)
        ns_prefix = namespace_for(ns).upper()
        super().__init__(ns_prefix, code, subject_name, concept_path(subject)[:-1].split('\\'), base_path)

    def path(self) -> str:
        return self._base_path + self._subject_path

    def name_char_(self) -> str:
        return self._name
