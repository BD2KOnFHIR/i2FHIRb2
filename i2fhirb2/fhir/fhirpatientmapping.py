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
from typing import Tuple, Dict, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import sessionmaker

from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientMapping, PatientIDEStatus
from i2fhirb2.sqlsupport.dbconnection import I2B2Tables


class PatientNumberGenerator:
    """
    i2b2 patient number generator.
    """
    def __init__(self, next_number: int):
        self._next_number = next_number

    def new_number(self) -> int:
        rval = self._next_number
        self._next_number += 1
        return rval

    def refresh(self, tables: I2B2Tables, ignore_upload_id: Optional[int]) -> int:
        session = sessionmaker(bind=tables.crc_engine)()
        q = func.max(tables.patient_dimension.c.patient_num)
        if ignore_upload_id is not None:
            q = q.filter(or_(tables.patient_dimension.c.upload_id.is_(None),
                         tables.patient_dimension.c.upload_id != ignore_upload_id))
        qr = session.query(q).all()
        self._next_number = qr[0][0] + 1
        session.close()
        return self._next_number


class FHIRPatientMapping:
    project_id = 'fhir'                     # Default project identifier
    identity_source_id = 'HIVE'             # source_id for identity mapping
    number_generator = PatientNumberGenerator(100000001)
    number_map = dict()                     # type: Dict[Tuple[str, str, str], int]

    @classmethod
    def _clear(cls):
        cls.project_id = 'fhir'
        cls.identity_source_id = 'HIVE'
        cls.number_generator = PatientNumberGenerator(100000001)
        cls.number_map.clear()

    @classmethod
    def refresh_patient_number_generator(cls, tables: I2B2Tables, ignore_upload_id: Optional[int]) -> int:
        return cls.number_generator.refresh(tables, ignore_upload_id)

    def __init__(self, patient_id: str, patient_ide_source: str):
        """
        Create a new patient mapping entry in https://www.dropbox.com/s/zynyact6uowhdgi/Screenshot%202017-09-25%2014.58.44.png?dl=0the FHIR context
        :param patient_id: identifier
        :param patient_ide_source: source -- currently the base URI
        """
        self.patient_mapping_entries = []
        key = (patient_id, patient_ide_source, self.project_id)
        if key in self.number_map:
            self.patient_num = self.number_map[key]
        else:
            self.patient_num = self.number_generator.new_number()
            pm = PatientMapping(self.patient_num,
                                patient_id,
                                PatientIDEStatus.active,
                                patient_ide_source,
                                self.project_id)
            self.number_map[key] = self.patient_num
            self.patient_mapping_entries.append(pm)

        identity_id = str(self.patient_num)
        ikey = (identity_id, self.identity_source_id, self.project_id)
        if ikey not in self.number_map:
            ipm = PatientMapping(self.patient_num,
                                 identity_id,
                                 PatientIDEStatus.active,
                                 self.identity_source_id,
                                 self.project_id)
            self.number_map[ikey] = ipm
            self.patient_mapping_entries.append(ipm)
