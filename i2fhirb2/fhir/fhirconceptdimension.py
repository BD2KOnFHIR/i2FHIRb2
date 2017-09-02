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
from typing import Optional, List, cast

from rdflib import URIRef

from i2fhirb2.fhir.fhirmetadata import FHIRMetadata
from i2fhirb2.i2b2model.metadata.i2b2conceptdimension import ConceptDimension, ConceptDimensionRoot


class FHIRConceptDimension(FHIRMetadata):
    """ A list of all FHIR resources, as identified by the DomainResource tag """
    def dimension_list(self, subject: Optional[URIRef]=None) -> List[ConceptDimension]:
        """
        Generate the complete set of FHIR concept entries -- the first level deep in all FHIR definitions.
        :param subject: Specific target subject.  (Debugging -- not used in production)
        :return: A list of FHIR concept dimension entries for loading into i2b2 tables
        """
        return [cast(ConceptDimension, ConceptDimensionRoot('FHIR'))] + \
               [ConceptDimension(subj, self._name_base) for subj in self.fhir_concepts(subject).keys()]

    @staticmethod
    def tsv_header() -> str:
        return ConceptDimension._header()
