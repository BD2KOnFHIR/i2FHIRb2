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


# create table i2b2demodata.patient_mapping
# (
# 	patient_ide varchar(200) not null,
# 	patient_ide_source varchar(50) not null,
# 	patient_num integer not null,
# 	patient_ide_status varchar(50),
# 	project_id varchar(50) not null,
# 	upload_date timestamp,
# 	update_date timestamp,
# 	download_date timestamp,
# 	import_date timestamp,
# 	sourcesystem_cd varchar(50),
# 	upload_id integer,
# 	constraint patient_mapping_pk
# 		primary key (patient_ide, patient_ide_source, project_id)
# )
# ;
from typing import List, Tuple


from i2fhirb2.i2b2model.shared.i2b2core import I2B2CoreWithUploadId
from i2fhirb2.sqlsupport.dynobject import DynElements, DynObject
from i2fhirb2.sqlsupport.dbconnection import I2B2Tables


class PatientIDEStatus:
    class PatientIDEStatusCode:
        def __init__(self, code: str) -> None:
            self.code = code
    active = PatientIDEStatusCode("A")
    inactive = PatientIDEStatusCode("I")
    deleted = PatientIDEStatusCode("D")
    merged = PatientIDEStatusCode("M")


class PatientMapping(I2B2CoreWithUploadId):
    _t = DynElements(I2B2CoreWithUploadId)

    key_fields = ["patient_ide", "patient_ide_source", "project_id"]

    def __init__(self, patient_num: int, patient_id: str, patient_ide_status: PatientIDEStatus.PatientIDEStatusCode,
                 patient_ide_source: str, project_id: str, **kwargs):
        """
        Construct a patient mapping entry
        :param patient_num: patient number
        :param patient_id: clear text patient identifier
        :param patient_ide_status: status code
        :param patient_ide_source: clear text patient identifier source
        :param project_id: project identifier
        :param kwargs:

        The patient number is the key to the patient dimension file.  The patient_mapping file has, at a minimum,
        one entry
        """
        self._patient_num = patient_num
        self._patient_ide = patient_id
        self._patient_ide_status = patient_ide_status
        self._patient_ide_source = patient_ide_source
        self._project_id = project_id

        super().__init__(**kwargs)

    @DynObject.entry(_t)
    def patient_ide(self) -> str:
        """
        The encrypted patient identifier
        """
        return self._patient_ide

    @DynObject.entry(_t)
    def patient_ide_source(self) -> str:
        """
        The source system (source of what I don't really know)
        """
        return self._patient_ide_source

    @DynObject.entry(_t)
    def patient_num(self) -> int:
        """
        Patient number in the patient dimension file
        """
        return self._patient_num

    @DynObject.entry(_t)
    def patient_ide_status(self) -> str:
        """
        Patient number in the patient dimension file
        """
        return self._patient_ide_status.code

    @DynObject.entry(_t)
    def project_id(self) -> str:
        """
        Project identifier
        """
        return self._project_id

    @classmethod
    def delete_upload_id(cls, tables: I2B2Tables, upload_id: int) -> int:
        """
        Delete all patient_mapping records with the supplied upload_id
        :param tables: i2b2 sql connection
        :param upload_id: upload identifier to remove
        :return: number or records that were deleted
        """
        return cls._delete_upload_id(tables.crc_connection, tables.patient_mapping, upload_id)

    @classmethod
    def delete_sourcesystem_cd(cls, tables: I2B2Tables, sourcesystem_cd: str) -> int:
        """
        Delete all records with the supplied sourcesystem_cd
        :param tables: i2b2 sql connection
        :param sourcesystem_cd: sourcesystem_cd to remove
        :return: number or records that were deleted
        """
        return cls._delete_sourcesystem_cd(tables.crc_connection, tables.patient_mapping, sourcesystem_cd)

    @classmethod
    def add_or_update_records(cls, tables: I2B2Tables, records: List["PatientMapping"]) -> Tuple[int, int]:
        """
        Add or update the patient_mapping table as needed to reflect the contents of records
        :param tables: i2b2 sql connection
        :param records: records to apply
        :return: number of records added / modified
        """
        return cls._add_or_update_records(tables.crc_connection, tables.patient_mapping, records)
