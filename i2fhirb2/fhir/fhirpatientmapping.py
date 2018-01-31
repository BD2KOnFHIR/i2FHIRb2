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
from operator import or_
from typing import Dict, Optional, NamedTuple

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from i2fhirb2.common_cli_parameters import DEFAULT_PROJECT_ID, DEFAULT_PATIENT_NUMBER_START, IDE_SOURCE_HIVE
from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientMapping, PatientIDEStatus
from i2fhirb2.sqlsupport.dbconnection import I2B2Tables


class PatientNumberGenerator:
    """
    i2b2 patient number generator.
    """
    def __init__(self, next_number: Optional[int]=None) -> None:
        """ Create a number generator with a starting patient number

        :param next_number: Patient number to start with.  Can be updated with the refresh method
        """
        self._next_number = next_number

    def new_number(self, tables: Optional[I2B2Tables]=None, check_db: bool=True) -> int:
        """ Get a new patient number.  If check_db is false, caller takes responsibility
        that the number generator is returning unused numbers -- which typically occurs
        in a single user situation where ``refresh()`` has been called

        :param tables: database tables link.  If None, we are generating TSV files.
        :param check_db: True means validate the number before return.
        :return: Available patient number
        """
        if tables and check_db:
            session = sessionmaker(bind=tables.crc_engine)()
            rval = None
            while rval is None:
                qr = session.query(tables.patient_dimension)\
                    .filter(tables.patient_dimension.c.patient_num == self._next_number)
                if not qr.all():
                    rval = self._next_number
                    break
                else:
                    self._next_number += 1
        else:
            rval = self._next_number

        self._next_number += 1
        return rval

    def refresh(self, tables: I2B2Tables, ignore_upload_id: Optional[int]) -> int:
        """ Update the next number to the last used number plus one

        :param tables: database tables link
        :param ignore_upload_id: If present, ignore this id as it will be deleted
        :return: next available number
        """
        session = sessionmaker(bind=tables.crc_engine)()
        q = func.max(tables.patient_dimension.c.patient_num)
        if ignore_upload_id is not None:
            q = q.filter(or_(tables.patient_dimension.c.upload_id.is_(None),
                         tables.patient_dimension.c.upload_id != ignore_upload_id))
        qr = session.query(q).all()
        self._next_number = qr[0][0] + 1 if qr else 1
        session.close()
        return self._next_number


class PatientMappingKey(NamedTuple):
    patient_id: str
    patient_ide_src: str
    project_id: str


patient_number = int


class FHIRPatientMapping:
    project_id = DEFAULT_PROJECT_ID         # Default project identifier
    identity_source_id = IDE_SOURCE_HIVE    # source_id for identity mapping
    number_generator = PatientNumberGenerator(DEFAULT_PATIENT_NUMBER_START)
    number_map: Dict[PatientMappingKey, patient_number] = dict()

    @classmethod
    def _clear(cls) -> None:
        """ Reset the FHIRPatientMapping resource to its default state

        """
        cls.project_id = DEFAULT_PROJECT_ID
        cls.identity_source_id = IDE_SOURCE_HIVE
        cls.number_generator = PatientNumberGenerator(DEFAULT_PATIENT_NUMBER_START)
        cls.number_map.clear()

    @classmethod
    def refresh_patient_number_generator(cls, tables: I2B2Tables, ignore_upload_id: Optional[int]) -> int:
        """ Perform a refresh on the patient number generator, setting the next number to one greater
        than the last one used, ignoring ``ignore_upload_id`` if it is supplied.

        :param tables: i2b2 tables link
        :param ignore_upload_id: If present, identifiers associated with this upload id will be removed from the
            table and should be ignored
        :return: first available patient number
        """
        return cls.number_generator.refresh(tables, ignore_upload_id)

    def __init__(self, tables: Optional[I2B2Tables], patient_id: str, patient_ide_source: str) -> None:
        """ Create a new patient mapping entry in the FHIR context

        :param tables: i2b2 data tables link.  None means that we are generating tsv files and we are "write only"
        :param patient_id: patient identifier (not number - real id)
        :param patient_ide_source: patient identifier source
        """
        self.patient_mapping_entries = []
        key = PatientMappingKey(patient_id, patient_ide_source, self.project_id)

        # If it is in our map, just use it
        if key in self.number_map:
            self.patient_num = self.number_map[key]

        # Look it up in the tables
        else:
            self.patient_num = self._existing_entry(tables, key)
            if self.patient_num is None:
                self.patient_num = self.number_generator.new_number(tables)
            pm = PatientMapping(self.patient_num,
                                patient_id,
                                PatientIDEStatus.active,
                                patient_ide_source,
                                self.project_id)
            self.number_map[key] = self.patient_num
            self.patient_mapping_entries.append(pm)

        # Add two mapping entries -- one four our source and one for the number itself
        identity_id = str(self.patient_num)
        ikey = PatientMappingKey(identity_id, self.identity_source_id, self.project_id)
        if ikey not in self.number_map:
            ipm = PatientMapping(self.patient_num,
                                 identity_id,
                                 PatientIDEStatus.active,
                                 self.identity_source_id,
                                 self.project_id)
            self.number_map[ikey] = ipm
            self.patient_mapping_entries.append(ipm)

    @staticmethod
    def _existing_entry(tables: Optional[I2B2Tables], key: PatientMappingKey) -> Optional[int]:
        if not tables:
            return None                                 # Generating tsv files, nothihc exists
        pdtabc = tables.patient_mapping.c
        s = select([pdtabc.patient_num])\
            .where(pdtabc.patient_ide == key.patient_id and
                   pdtabc.patient_ide_source == key.patient_ide_src
                   and pdtabc.project_id == key.project_id)
        qr = list(tables.crc_connection.execute(s))
        return qr[0][0] if qr else None
