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

from rdflib import URIRef

from i2fhirb2.fhir.fhirencountermapping import FHIREncounterMapping
from i2fhirb2.i2b2model.data.i2b2visitdimension import VisitDimension, ActiveStatusCd


class FHIRVisitDimension:
    """
    For the short term, we are using the FHIR resource instance URI to uniquely identify a 'visit'
    """
    def __init__(self, resourceURI: URIRef, patient_num: int, patient_ide: str,
                 patient_ide_source: str, start_date: datetime) -> None:
        self.encounter_mappings = FHIREncounterMapping(resourceURI, patient_ide, patient_ide_source)
        self.visit_dimension_entry = \
            VisitDimension(self.encounter_mappings.encounter_num, patient_num,
                           ActiveStatusCd(ActiveStatusCd.sd_ongoing, ActiveStatusCd.ed_ongoing), start_date)
