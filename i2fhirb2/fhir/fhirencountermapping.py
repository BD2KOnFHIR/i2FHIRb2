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
from typing import Dict, Tuple, Optional

from fhirtordf.rdfsupport.uriutils import uri_to_ide_and_source
from rdflib import URIRef
from sqlalchemy import func, or_
from sqlalchemy.orm import sessionmaker

from i2fhirb2.common_cli_parameters import DEFAULT_PROJECT_ID, DEFAULT_ENCOUNTER_NUMBER_START, IDE_SOURCE_HIVE
from i2fhirb2.i2b2model.data.i2b2encountermapping import EncounterMapping, EncounterIDEStatus
from i2fhirb2.sqlsupport.dbconnection import I2B2Tables


class EncounterNumberGenerator:
    """
    i2b2 encounter number generator.
    """
    def __init__(self, next_number: int) -> None:
        """
        Create the number generator
        :param next_number: First encounter number to assign
        """
        self._next_number = next_number

    def new_number(self) -> int:
        """
        Return a new encounter number
        :return:
        """
        rval = self._next_number
        self._next_number += 1
        return rval

    def refresh(self, tables: I2B2Tables, ignore_upload_id: Optional[int]) -> int:
        """
        Determine the greatest encounter number that is currently in use and set the next number to one greater
        :param tables: i2b2 SQL tables
        :param ignore_upload_id: If present, encounters with this upload id are ignored.  This is used in cases when
        an upload is being replaced.
        :return: next number
        """
        session = sessionmaker(bind=tables.crc_engine)()
        q = func.max(tables.visit_dimension.c.encounter_num)
        if ignore_upload_id is not None:
            q = q.filter(or_(tables.visit_dimension.c.upload_id.is_(None),
                         tables.visit_dimension.c.upload_id != ignore_upload_id))
        qr = session.query(q).all()
        self._next_number = qr[0][0] + 1
        session.close()
        return self._next_number


class FHIREncounterMapping:
    project_id = DEFAULT_PROJECT_ID         # Project identifier
    identity_source_id = IDE_SOURCE_HIVE    # source_id for identity mapping
    number_generator = EncounterNumberGenerator(DEFAULT_ENCOUNTER_NUMBER_START)
    number_map = dict()                     # type: Dict[Tuple[str, str, str, str, str], int]

    @classmethod
    def _clear(cls) -> None:
        """
        Reset the mapping table to its default. (Primarily used for testing)
        """
        cls.project_id = DEFAULT_PROJECT_ID
        cls.identity_source_id = IDE_SOURCE_HIVE
        cls.number_generator = EncounterNumberGenerator(DEFAULT_ENCOUNTER_NUMBER_START)
        cls.number_map.clear()

    @classmethod
    def refresh_encounter_number_generator(cls, tables: I2B2Tables, ignore_upload_id: Optional[int]) -> int:
        """
        Reset the generator
        :param tables: i2b2 tables
        :param ignore_upload_id: if present, do not look at the encounter numbers from this upload
        :return: starting encounter number
        """
        return cls.number_generator.refresh(tables, ignore_upload_id)

    def __init__(self, encounterURI: URIRef, patient_id: str, patient_ide_source: str) -> None:
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
