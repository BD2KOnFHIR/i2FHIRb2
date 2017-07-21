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
from typing import Tuple, Dict, Optional, List

from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientMapping, PatientIDEStatus


class PatientNumberGenerator:
    """
    i2b2 patient number generator.
    """
    # TODO: This needs to be tied into the patient_dimension table and the next number should be retrieved via a SQL query
    def __init__(self, next_number: int):
        self._next_number = next_number

    def new_number(self) -> int:
        rval = self._next_number
        self._next_number += 1
        return rval


class PatientNumberMap:
    """
    Static image of i2b2 patient_mapping.
    """
    def __init__(self):
        # TODO: This needs to execute queries against patient_mapping table
        self.numbergenerator = PatientNumberGenerator(100000001)
        # key = patient ide, patient_ide_source, project_id
        self._map = dict()          # type: Dict[Tuple(str, str, str), int]

    def number_for(self, patient_id: str, patient_ide_source: str, project_id: str) -> Tuple[int, bool]:
        exists = self.has_key(patient_id, patient_ide_source, project_id)
        key = (patient_id, patient_ide_source, project_id)
        if not exists:
            self._map[key] = self.numbergenerator.new_number()
        return self._map[key], exists

    def has_key(self, patient_id: str, patient_ide_source: str, project_id: str) -> bool:
        return (patient_id, patient_ide_source, project_id) in self._map


class FHIRPatientMapping:
    project_id = 'fhir'                     # Default project identifier
    identity_source_id = 'HIVE'             # source_id for identity mapping
    numbermap = PatientNumberMap()

    def __init__(self, patient_id: str, patient_ide_source: str):
        """
        Create a new patient mapping entry in the FHIR context
        :param patient_id: identifier
        :param patient_ide_source: source -- currently the base URI
        """
        self.patient_mapping_entries = []
        self.patient_num, exists = self.numbermap.number_for(patient_id, patient_ide_source, self.project_id)
        if not exists:
            self.patient_mapping_entries.append(
                PatientMapping(self.patient_num,
                               patient_id,
                               PatientIDEStatus.active,
                               patient_ide_source,
                               self.project_id))
        self._add_identity_element()

    def _add_identity_element(self):
        if not self.numbermap.has_key(str(self.patient_num), self.identity_source_id, self.project_id):
            self.patient_mapping_entries.append(
                PatientMapping(self.patient_num,
                               str(self.patient_num),
                               PatientIDEStatus.active,
                               self.identity_source_id,
                               self.project_id))