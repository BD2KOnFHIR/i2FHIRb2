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
from fhirtordf.rdfsupport.namespaces import namespace_for
from rdflib import URIRef
from rdflib.namespace import split_uri

from i2fhirb2.fhir.fhirspecific import concept_path, concept_code, concept_name
from i2fhirb2.i2b2model.shared.i2b2core import I2B2CoreWithUploadId
from i2fhirb2.sqlsupport.dynobject import DynElements


class CommonDimension(I2B2CoreWithUploadId):
    """ Common base class of all dimensions """
    _t = DynElements(I2B2CoreWithUploadId)
    graph = None

    def __init__(self, subject: URIRef, base_path: str = '\\', **kwargs) -> None:
        """
        Constructor
        :param subject: URI of the subject
        :param base_path: base path of items
        :param kwargs: additional arguments for i2b2 core
        """
        super().__init__(**kwargs)
        assert(base_path.endswith('\\'))
        self._subject = subject
        self._base_path = base_path
        self._name_prefix = namespace_for(split_uri(subject)[0]).upper()

    def path(self) -> str:
        return self._base_path + concept_path(self._subject)

    def cd(self) -> str:
        return concept_code(self._subject)

    def name_char_(self) -> str:
        return self._name_prefix + ' ' + concept_name(self.graph, self._subject)

    @staticmethod
    def blob() -> str:
        return ''
