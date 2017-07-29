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
from typing import Dict, Tuple

from rdflib import URIRef

from i2fhirb2.i2b2model.data.i2b2encountermapping import EncounterMapping, EncounterIDEStatus
from i2fhirb2.rdfsupport.uriutils import uri_to_ide_and_source


class EncounterNumberGenerator:
    """
    i2b2 encounter number generator.
    """
    # TODO: This needs to be tied into the visit_dimension table
    # and the next number should be retrieved via a SQL query
    def __init__(self, next_number: int):
        self._next_number = next_number

    def new_number(self) -> int:
        rval = self._next_number
        self._next_number += 1
        return rval


class FHIREncounterMapping:
    project_id = 'fhir'                     # Default project identifier
    identity_source_id = 'HIVE'             # source_id for identity mapping
    number_generator = EncounterNumberGenerator(500000)
    number_map = dict()                     # type: Dict[Tuple[str, str, str, str, str], int]

    @classmethod
    def _clear(cls):
        cls.project_id = 'fhir'
        cls.identity_source_id = 'HIVE'
        cls.number_generator = EncounterNumberGenerator(500000)
        cls.number_map.clear()

    def __init__(self, encounterURI: URIRef, patient_id: str, patient_ide_source: str):
        """
        Create a new encounter mapping entry
        :param encounterURI: URI of the encounter
        :param patient_id: Associated patient identifier
        :param patient_ide_source: Associated patient identifier source
        """

        self.encounter_mapping_entries = []
        encounter_id, encounter_ide_source = uri_to_ide_and_source(encounterURI, include_resource=True)
        key = (encounter_id, encounter_ide_source, self.project_id, patient_id, patient_ide_source)
        if key in self.number_map:
            self.encounter_num = self.number_map[key]
        else:
            self.encounter_num = self.number_generator.new_number()
            pm = EncounterMapping(encounter_id, encounter_ide_source, self.project_id, self.encounter_num,
                                  patient_id, patient_ide_source, EncounterIDEStatus.active)
            self.number_map[key] = self.encounter_num
            self.encounter_mapping_entries.append(pm)

        identity_id = str(self.encounter_num)
        ikey = (identity_id, self.identity_source_id, self.project_id)
        if ikey not in self.number_map:
            ipm = EncounterMapping(identity_id,
                                   self.identity_source_id,
                                   self.project_id,
                                   self.encounter_num,
                                   patient_id,
                                   patient_ide_source,
                                   EncounterIDEStatus.active)
            self.encounter_mapping_entries.append(ipm)
