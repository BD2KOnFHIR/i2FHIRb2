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
from typing import Optional, Tuple, List


from i2fhirb2.i2b2model.shared.i2b2core import I2B2CoreWithUploadId
from i2fhirb2.sqlsupport.dynobject import DynElements, DynObject
from i2fhirb2.sqlsupport.dbconnection import I2B2Tables


class ObservationFactKey:
    def __init__(self, patient_num: int, encounter_num: int, provider_id: str,
                 start_date: Optional[datetime] = None) -> None:
        """
        A partial key to the observation fact table.  These three or four elements identify a collection of facts
        that can be added or replaced as a block
        :param patient_num: Patient number -- key to the patient_dimension table
        :param encounter_num: Encounter number -- key to the visit_dimension table
        :param provider_id: Provider identifier -- key to the provider_dimension table
        :param start_date: If provided, separates multiple entries w/ different dates of occurrence
        """
        self.patient_num = patient_num
        self.encounter_num = encounter_num
        self.provider_id = provider_id
        self.key_includes_start_date = start_date is not None
        self.start_date = start_date if start_date is not None else datetime.now()


class ValueTypeCd:
    def __init__(self, code: str) -> None:
        self.code = code


valuetype_text = ValueTypeCd('T')
valuetype_number = ValueTypeCd('N')
valuetype_blob = ValueTypeCd('B')
valuetype_nlp = ValueTypeCd('NLP')
valuetype_date = ValueTypeCd('D')
valuetype_novalue = ValueTypeCd('@')


# create table i2b2demodata.observation_fact
# (
#     encounter_num integer not null,
#     patient_num integer not null,
#     concept_cd varchar(50) not null,
#     provider_id varchar(50) not null,
#     start_date timestamp not null,
#     modifier_cd varchar(100) default '@'::character varying not null,
#     instance_num integer default 1 not null,
#     valtype_cd varchar(50),
#     tval_char varchar(255),
#     nval_num numeric(18,5),
#     valueflag_cd varchar(50),
#     quantity_num numeric(18,5),
#     units_cd varchar(50),
#     end_date timestamp,
#     location_cd varchar(50),
#     observation_blob text,
#     confidence_num numeric(18,5),
#     update_date timestamp,
#     download_date timestamp,
#     import_date timestamp,
#     sourcesystem_cd varchar(50),
#     upload_id integer,
#     text_search_index serial not null,
#     constraint observation_fact_pk
#         primary key (patient_num, concept_cd, modifier_cd, start_date, encounter_num, instance_num, provider_id)
# )

class ObservationFact(I2B2CoreWithUploadId):
    _t = DynElements(I2B2CoreWithUploadId)

    key_fields = ["patient_num", "concept_cd", "modifier_cd", "start_date",
                  "encounter_num", "instance_num", "provider_id"]

    def __init__(self, fact_key: ObservationFactKey, concept_cd: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._patient_num = fact_key.patient_num
        self._encounter_num = fact_key.encounter_num
        self._provider_id = fact_key.provider_id
        self._concept_cd = concept_cd
        self._start_date = fact_key.start_date
        self._modifier_cd = None
        self._instance_num = None
        self._valtype_cd = None
        self._tval_char = None
        self._nval_num = None
        self._valueflag_cd = None
        self._quantity_num = None
        self._units_cd = None
        self._end_date = None
        self._location_cd = None
        self._observation_blob = None
        self._confidence_num = None

    @DynObject.entry(_t)
    def encounter_num(self) -> int:
        """
        Encoded i2b2 patient visit number
        """
        return self._encounter_num

    @DynObject.entry(_t)
    def patient_num(self) -> int:
        """
        Encoded i2b2 patient number
        """
        return self._patient_num

    @DynObject.entry(_t)
    def concept_cd(self) -> str:
        """ Code for the observation of interest (i.e. diagnoses, procedures, medications, lab tests"""
        return self._concept_cd

    @DynObject.entry(_t)
    def provider_id(self) -> str:
        """
        Practitioner or provider id
        :return:
        """
        return self._provider_id

    @DynObject.entry(_t)
    def start_date(self) -> datetime:
        """ Starting date-time of the observation. (mm/dd/yy)"""
        return self._start_date

    @DynObject.entry(_t)
    def modifier_cd(self) -> str:
        """
        Code for modifier of interest (i.e. "Route", "DOSE").
        Note that the value columns are often used to hold the amounts such as "100" (mg) for the modifier of DOSE or
        "PO" for the modifier of ROUTE.
        :return:
        """
        return self._modifier_cd if self._modifier_cd else '@'

    @DynObject.entry(_t)
    def instance_num(self) -> int:
        """
        Encoded instance number that allows more than one modifier to be provided for each CONCEPT_CD.
        Each row will have a different MODIFIER_CD but a similar INSTANCE_NUM
        """
        return self._instance_num if self._instance_num is not None else 0

    @DynObject.entry(_t)
    def valtype_cd(self) -> str:
        """ The place where the value is stored
         'T' -- tval_char (Text (enums / short messages)
         'N' -- nval_num has number, tval_char has optional G, E, L (or other stuff where needed)
         'B' -- Raw text (notes / reports) observation_blob
         'NLP' -- NLP result text
         '@' -- no value
         'D' -- tval_char has a date in text and nval has a floating point representation (
                1996-10-13 00:00 = 19961013.0000
         ''  -- pure nval_num (?) - no tval_char?
         Note that the spec says that this is optional, but it is never null
          """
        return self._valtype_cd.code if isinstance(self._valtype_cd, ValueTypeCd) else \
            self._valtype_cd if self._valtype_cd is not None else '@'

    @DynObject.entry(_t)
    def tval_char(self) -> Optional[str]:
        """
        Used in conjunction with VALTYPE_CD = "T" or "N"
        When "T"
            Stores the text value
        When "N"
            'E' - Equals, 'NE' - Not equal, 'L' - Less than, 'LE' - LE, 'G' - Greater than, 'GE
        :return:
        """
        return self._tval_char

    @DynObject.entry(_t)
    def nval_num(self) -> Optional[float]:
        """
        Used in conjunction with VALTYPE_CD = "N" to store a numeric value
        """
        return self._nval_num

    @DynObject.entry(_t)
    def valueflag_cd(self) -> Optional[str]:
        """
        A code that represents the type of value present in the NVAL_NUM, the TVAL_CHAR or OBSERVATION_BLOB columns
        'X' - Encrypted text in the blob column (B)
        'H' - High      (N or T)
        'L' - Low
        'A' - Abnormal
        """
        return self._valueflag_cd

    @DynObject.entry(_t)
    def quantity_num(self) -> Optional[float]:
        """
        The number of observations represented by this fact (no known examples)
        """
        return self._quantity_num

    @DynObject.entry(_t)
    def units_cd(self) -> Optional[str]:
        """
        A textual description of the units associated with a value
        :return:
        """
        return self._units_cd

    @DynObject.entry(_t)
    def end_date(self) -> Optional[datetime]:
        """
        The date that the observation ended. If the date is derived or calculated from another observation (like a
        report) then the end date is the same as the observation it was derived or calculated from
        WARNING: two meanings for same field
        """
        return self._end_date

    @DynObject.entry(_t)
    def location_cd(self) -> Optional[str]:
        """
        A code representing the hospital associated with this visit
        """
        return self._location_cd

    @DynObject.entry(_t)
    def observation_blob(self) -> Optional[str]:
        """
        XML data that includes partially structured and unstructured data about an observation
        """
        return self._observation_blob

    @DynObject.entry(_t)
    def confidence_num(self) -> Optional[float]:
        """
        A code or number representing the confidence in the accuracy of the data. (No known examples)
        Q: 'code' in a numeric situation?
        """
        return None

    DynObject._after_root(_t)

    # text_search_index is auto-generated (?)
    # @DynObject.entry(_t)
    # def text_search_index(self) -> float:
    #     return None
    @property
    def pk(self) -> Tuple:
        return self.patient_num, self.encounter_num, self.instance_num,  self.concept_cd, self.modifier_cd

    def __lt__(self, other: "ObservationFact") -> bool:
        return self.pk < other.pk

    @classmethod
    def delete_upload_id(cls, tables: I2B2Tables, upload_id: int) -> int:
        """
        Delete all observation_fact records with the supplied upload_id
        :param tables: i2b2 sql connection
        :param upload_id: upload identifier to remove
        :return: number or records that were deleted
        """
        return cls._delete_upload_id(tables.crc_connection, tables.observation_fact, upload_id)

    @classmethod
    def delete_sourcesystem_cd(cls, tables: I2B2Tables, sourcesystem_cd: str) -> int:
        """
        Delete all records with the supplied sourcesystem_cd
        :param tables: i2b2 sql connection
        :param sourcesystem_cd: sourcesystem_cd to remove
        :return: number or records that were deleted
        """
        return cls._delete_sourcesystem_cd(tables.crc_connection, tables.observation_fact, sourcesystem_cd)

    @classmethod
    def add_or_update_records(cls, tables: I2B2Tables, records: List["ObservationFact"]) -> Tuple[int, int]:
        """
        Add or update the observation_fact table as needed to reflect the contents of records
        :param tables: i2b2 sql connection
        :param records: records to apply
        :return: number of records added / modified
        """
        return cls._add_or_update_records(tables.crc_connection, tables.observation_fact, records)

    def _date_val(self, dt: datetime) -> None:
        """
        Add a date value
        :param dt: datetime to add
        """
        self._tval_char = dt.strftime('%Y-%m-%d %H:%M')
        self._nval_num = (dt.year * 10000) + (dt.month * 100) + dt.day + \
                         (((dt.hour / 100.0) + (dt.minute / 10000.0)) if isinstance(dt, datetime) else 0)
