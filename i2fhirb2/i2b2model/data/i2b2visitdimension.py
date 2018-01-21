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
from typing import Optional, List, Tuple

from i2fhirb2.i2b2model.shared.i2b2core import I2B2CoreWithUploadId
from i2fhirb2.sqlsupport.dynobject import DynElements, DynObject
from i2fhirb2.sqlsupport.dbconnection import I2B2Tables


class ActiveStatusCd:
    def __setattr__(self, key, value):
        if key not in ["startcode", "endcode"]:
            raise ValueError("New elements not allowed")
        super().__setattr__(key, value)

    class EndDateCode:
        def __init__(self, code: str) -> None:
            self.code = code

    ed_unknown = EndDateCode('U')
    ed_ongoing = EndDateCode('O')
    ed_day = EndDateCode('Y')
    ed_month = EndDateCode('M')
    ed_year = EndDateCode('X')
    ed_hour = EndDateCode('R')
    ed_minute = EndDateCode('T')
    ed_second = EndDateCode('S')

    class StartDateCode:
        def __init__(self, code: str) -> None:
            self.code = code

    sd_unknown = StartDateCode('L')
    sd_ongoing = StartDateCode('A')
    sd_day = StartDateCode('D')
    sd_month = StartDateCode('B')
    sd_year = StartDateCode('F')
    sd_hour = StartDateCode('H')
    sd_minute = StartDateCode('I')
    sd_second = StartDateCode('C')

    def __init__(self, start: StartDateCode, end: EndDateCode) -> None:
        self.startcode = start
        self.endcode = end

    @property
    def code(self):
        return self.endcode.code + self.startcode.code


class VisitDimension(I2B2CoreWithUploadId):
    _t = DynElements(I2B2CoreWithUploadId)

    key_fields = ["encounter_num", "patient_num"]

    def __init__(self,
                 encounter_num: int,
                 patient_num: int,
                 active_status_cd: Optional[ActiveStatusCd] = None,
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None,
                 inout_cd: Optional[str] = None,
                 location_cd: Optional[str] = None,
                 location_path: Optional[str] = None,
                 length_of_stay: Optional[int] = None,
                 visit_blob: Optional[str] = None,
                 **kwargs):
        self._encounter_num = encounter_num
        self._patient_num = patient_num
        self._active_status_cd = active_status_cd
        self._start_date = start_date
        self._end_date = end_date
        self._inout_cd = inout_cd
        self._location_cd = location_cd
        self._location_path = location_path
        self._length_of_stay = length_of_stay
        self._visit_blob = visit_blob
        super().__init__(**kwargs)

    @DynObject.entry(_t)
    def encounter_num(self) -> int:
        """
        Reference number for the encounter/visit
        """
        return self._encounter_num

    @DynObject.entry(_t)
    def patient_num(self) -> int:
        """
        Reference number for the patient
        """
        return self._patient_num

    @DynObject.entry(_t)
    def active_status_cd(self) -> Optional[str]:
        """
        Reference number for the patient
        """
        return self._active_status_cd.code if self._active_status_cd else None

    @DynObject.entry(_t)
    def start_date(self) -> Optional[datetime]:
        """
        The date the event began
        """
        return self._start_date

    @DynObject.entry(_t)
    def end_date(self) -> Optional[datetime]:
        """
        The date the event ended
        """
        return self._end_date

    @DynObject.entry(_t)
    def inout_cd(self) -> Optional[str]:
        """
        The date the event ended
        """
        return self._inout_cd

    @DynObject.entry(_t)
    def location_cd(self) -> Optional[str]:
        return self._location_cd

    @DynObject.entry(_t)
    def location_path(self) -> Optional[str]:
        return self._location_path

    @DynObject.entry(_t)
    def length_of_stay(self) -> Optional[int]:
        return self._length_of_stay

    @DynObject.entry(_t)
    def visit_blob(self) -> Optional[str]:
        return self._visit_blob

    @classmethod
    def delete_upload_id(cls, tables: I2B2Tables, upload_id: int) -> int:
        """
        Delete all patient_dimension records with the supplied upload_id
        :param tables: i2b2 sql connection
        :param upload_id: upload identifier to remove
        :return: number or records that were deleted
        """
        return cls._delete_upload_id(tables.crc_connection, tables.visit_dimension, upload_id)

    @classmethod
    def delete_sourcesystem_cd(cls, tables: I2B2Tables, sourcesystem_cd: str) -> int:
        """
        Delete all records with the supplied sourcesystem_cd
        :param tables: i2b2 sql connection
        :param sourcesystem_cd: sourcesystem_cd to remove
        :return: number or records that were deleted
        """
        return cls._delete_sourcesystem_cd(tables.crc_connection, tables.visit_dimension, sourcesystem_cd)

    @classmethod
    def add_or_update_records(cls, tables: I2B2Tables, records: List["VisitDimension"]) -> Tuple[int, int]:
        """
        Add or update the patient_dimension table as needed to reflect the contents of records
        :param tables: i2b2 sql connection
        :param records: records to apply
        :return: number of records added / modified
        """
        return cls._add_or_update_records(tables.crc_connection, tables.visit_dimension, records)
