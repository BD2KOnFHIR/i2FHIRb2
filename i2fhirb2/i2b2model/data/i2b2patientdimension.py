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

# create table i2b2demodata.patient_dimension
# (
# 	patient_num integer not null
# 		constraint patient_dimension_pk
# 			primary key,
# 	vital_status_cd varchar(50),
# 	birth_date timestamp,
# 	death_date timestamp,
# 	sex_cd varchar(50),
# 	age_in_years_num integer,
# 	language_cd varchar(50),
# 	race_cd varchar(50),
# 	marital_status_cd varchar(50),
# 	religion_cd varchar(50),
# 	zip_cd varchar(10),
# 	statecityzip_path varchar(700),
# 	income_cd varchar(50),
# 	patient_blob text,
# 	update_date timestamp,
# 	download_date timestamp,
# 	import_date timestamp,
# 	sourcesystem_cd varchar(50),
# 	upload_id integer
# )
from datetime import datetime
from typing import Optional, Tuple, List

from i2fhirb2.i2b2model.shared.i2b2core import I2B2CoreWithUploadId
from i2fhirb2.sqlsupport.dynobject import DynElements, DynObject
from i2fhirb2.sqlsupport.dbconnection import I2B2Tables


class VitalStatusCd:
    def __setattr__(self, key, value):
        if key not in ["birthcode", "deathcode"]:
            raise ValueError("New elements not allowed")
        super().__setattr__(key, value)

    class BirthDateCode:
        def __init__(self, code: str) -> None:
            self.code = code

    bd_unknown = BirthDateCode('L')
    bd_day = BirthDateCode('D')
    bd_month = BirthDateCode('B')
    bd_year = BirthDateCode('F')
    bd_hour = BirthDateCode('H')
    bd_minute = BirthDateCode('M')
    bd_second = BirthDateCode('C')

    class DeathDateCode:
        def __init__(self, code: str) -> None:
            self.code = code
    dd_living = DeathDateCode('N')
    dd_unknown = DeathDateCode('U')
    dd_deceased = DeathDateCode('Z')
    dd_day = DeathDateCode('Y')
    dd_month = DeathDateCode('M')
    dd_year = DeathDateCode('X')
    dd_hour = DeathDateCode('R')
    dd_minute = DeathDateCode('T')
    dd_second = DeathDateCode('S')

    def __init__(self, birth: BirthDateCode, death: DeathDateCode) -> None:
        self.birthcode = birth
        self.deathcode = death

    @property
    def code(self):
        return self.deathcode.code + self.birthcode.code


# TODO: should age be computed from birthdate / deathdate
# TODO: language code -- what do we do with this?

class PatientDimension(I2B2CoreWithUploadId):
    _t = DynElements(I2B2CoreWithUploadId)

    key_fields = ["patient_num"]

    def __init__(self, patient_num, vital_status_cd: VitalStatusCd, **kwargs) -> None:
        self._patient_num = patient_num
        self._vital_status_code = vital_status_cd
        self._birth_date = None
        self._death_date = None
        self._sex_cd = None
        self._age_in_years_num = None
        self._language_cd = None
        self._race_cd = None
        self._marital_status_cd = None
        self._religion_cd = None
        self._zip_cd = None
        self._statecityzip_path = None
        self._income_cd = None
        self._patient_blob = None
        super().__init__(**kwargs)

    @DynObject.entry(_t)
    def patient_num(self) -> int:
        """
        Reference number for the patient
        """
        return self._patient_num

    @DynObject.entry(_t)
    def vital_status_cd(self) -> Optional[str]:
        """
        Encoded i2b2 patient visit number
        """
        return self._vital_status_code.code

    @DynObject.entry(_t)
    def birth_date(self) -> Optional[datetime]:
        """
        Encoded i2b2 patient visit number
        """
        return self._birth_date

    @DynObject.entry(_t)
    def death_date(self) -> Optional[datetime]:
        """
        Encoded i2b2 patient visit number
        """
        return self._death_date

    @DynObject.entry(_t)
    def sex_cd(self) -> Optional[str]:
        """
        Encoded i2b2 patient visit number
        """
        return self._sex_cd

    @DynObject.entry(_t)
    def age_in_years_num(self) -> Optional[int]:
        """
        Encoded i2b2 patient visit number
        """
        return self._age_in_years_num
    
    @DynObject.entry(_t)
    def language_cd(self) -> Optional[str]:
        return self._language_cd

    @DynObject.entry(_t)
    def race_cd(self) -> Optional[str]:
        """
        Encoded i2b2 patient visit number
        """
        return self._race_cd

    @DynObject.entry(_t)
    def marital_status_cd(self) -> Optional[str]:
        return self._marital_status_cd
    
    @DynObject.entry(_t)
    def religion_cd(self) -> Optional[str]:
        return self._religion_cd
    
    @DynObject.entry(_t)
    def zip_cd(self) -> Optional[str]:
        return self._zip_cd
    
    @DynObject.entry(_t)
    def statecityzip_path(self) -> Optional[str]:
        return self._statecityzip_path
    
    @DynObject.entry(_t)
    def income_cd(self) -> Optional[str]:
        return self._income_cd
    
    @DynObject.entry(_t)
    def patient_blob(self) -> Optional[str]:
        return self._patient_blob

    @classmethod
    def delete_upload_id(cls, tables: I2B2Tables, upload_id: int) -> int:
        """
        Delete all patient_dimension records with the supplied upload_id
        :param tables: i2b2 sql connection
        :param upload_id: upload identifier to remove
        :return: number or records that were deleted
        """
        return cls._delete_upload_id(tables.crc_connection, tables.patient_dimension, upload_id)

    @classmethod
    def delete_sourcesystem_cd(cls, tables: I2B2Tables, sourcesystem_cd: str) -> int:
        """
        Delete all records with the supplied sourcesystem_cd
        :param tables: i2b2 sql connection
        :param sourcesystem_cd: sourcesystem_cd to remove
        :return: number or records that were deleted
        """
        return cls._delete_sourcesystem_cd(tables.crc_connection, tables.patient_dimension, sourcesystem_cd)

    @classmethod
    def add_or_update_records(cls, tables: I2B2Tables, records: List["PatientDimension"]) -> Tuple[int, int]:
        """
        Add or update the patient_dimension table as needed to reflect the contents of records
        :param tables: i2b2 sql connection
        :param records: records to apply
        :return: number of records added / modified
        """
        return cls._add_or_update_records(tables.crc_connection, tables.patient_dimension, records)
