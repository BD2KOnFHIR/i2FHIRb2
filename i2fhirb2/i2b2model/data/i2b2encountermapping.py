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
from typing import Optional, List, Tuple

from i2fhirb2.i2b2model.shared.i2b2core import I2B2CoreWithUploadId
from i2fhirb2.sqlsupport.dynobject import DynElements, DynObject
from i2fhirb2.sqlsupport.dbconnection import I2B2Tables


class EncounterIDEStatus:
    class EncounterIDEStatusCode:
        def __init__(self, code: str) -> None:
            self.code = code
    active = EncounterIDEStatusCode("A")
    inactive = EncounterIDEStatusCode("I")
    deleted = EncounterIDEStatusCode("D")
    merged = EncounterIDEStatusCode("M")


class EncounterMapping(I2B2CoreWithUploadId):
    _t = DynElements(I2B2CoreWithUploadId)

    key_fields = ["encounter_ide", "encounter_ide_source", "project_id", "patient_ide", "patient_ide_source"]

    def __init__(self,
                 encounter_ide: str,
                 encounter_ide_source: str,
                 project_id: str,
                 encounter_num: int,
                 patient_ide: str,
                 patient_ide_source: str,
                 encounter_ide_status: Optional[EncounterIDEStatus.EncounterIDEStatusCode],
                 **kwargs):
        self._encounter_ide = encounter_ide
        self._encounter_ide_source = encounter_ide_source
        self._project_id = project_id
        self._encounter_num = encounter_num
        self._patient_ide = patient_ide
        self._patient_ide_source = patient_ide_source
        self._encounter_ide_status = encounter_ide_status

        super().__init__(**kwargs)

    @DynObject.entry(_t)
    def encounter_ide(self) -> str:
        return self._encounter_ide

    @DynObject.entry(_t)
    def encounter_ide_source(self) -> str:
        return self._encounter_ide_source

    @DynObject.entry(_t)
    def project_id(self) -> Optional[str]:
        return self._project_id

    @DynObject.entry(_t)
    def encounter_num(self) -> int:
        return self._encounter_num

    @DynObject.entry(_t)
    def patient_ide(self) -> str:
        return self._patient_ide

    @DynObject.entry(_t)
    def patient_ide_source(self) -> str:
        return self._patient_ide_source

    @DynObject.entry(_t)
    def encounter_ide_status(self) -> Optional[str]:
        return self._encounter_ide_status.code if self._encounter_ide_status else None

    @classmethod
    def delete_upload_id(cls, tables: I2B2Tables, upload_id: int) -> int:
        """
        Delete all patient_dimension records with the supplied upload_id
        :param tables: i2b2 sql connection
        :param upload_id: upload identifier to remove
        :return: number or records that were deleted
        """
        return cls._delete_upload_id(tables.crc_connection, tables.encounter_mapping, upload_id)

    @classmethod
    def delete_sourcesystem_cd(cls, tables: I2B2Tables, sourcesystem_cd: str) -> int:
        """
        Delete all records with the supplied sourcesystem_cd
        :param tables: i2b2 sql connection
        :param sourcesystem_cd: sourcesystem_cd to remove
        :return: number or records that were deleted
        """
        return cls._delete_sourcesystem_cd(tables.crc_connection, tables.encounter_mapping, sourcesystem_cd)

    @classmethod
    def add_or_update_records(cls, tables: I2B2Tables, records: List["EncounterMapping"]) -> Tuple[int, int]:
        """
        Add or update the patient_dimension table as needed to reflect the contents of records
        :param tables: i2b2 sql connection
        :param records: records to apply
        :return: number of records added / modified
        """
        return cls._add_or_update_records(tables.crc_connection, tables.encounter_mapping, records)
