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
from typing import Optional, Tuple

from rdflib import Graph, URIRef, Literal, XSD

from i2fhirb2.fhir.fhirpatientmapping import FHIRPatientMapping
from i2fhirb2.fhir.fhirspecific import FHIR, FHIR_RE_ID, FHIR_RE_BASE, V3, SNOMEDCT, \
    FHIR_RESOURCE_RE
from i2fhirb2.i2b2model.data.i2b2patientdimension import PatientDimension, VitalStatusCd


# TODO: is there any reason to pull patient_id from Patient.identifier rather than URL?
# TODO: what of foreign addresses
from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientIDEStatus
from i2fhirb2.rdfsupport.fhirgraphutils import value, extension, concept_uri, code
from i2fhirb2.rdfsupport.uriutils import uri_to_ide_and_source


class FHIRPatientDimension:
    def __init__(self, g: Graph, patient: URIRef):
        """
        Generate i2b2 patient dimension and patient_mapping records from PATIENT resources in graph g
        :param g: Graph containing 0 or more FHIR Patient resources
        :param patient: Graph subject
        """
        assert value(g, patient, FHIR.animal) is None       # We don't do animals
        patient_id, patient_ide_source = self.uri_to_patient_id(patient)
        self.patient_mappings = FHIRPatientMapping(patient_id, patient_ide_source)
        active = value(g, patient, FHIR.Patient.active)
        if active is not None and not active:
            self.patient_mappings._patient_ide_status = PatientIDEStatus.inactive
        self.patient_dimension_entry = PatientDimension(self.patient_mappings.patient_num,
                                                        VitalStatusCd(VitalStatusCd.bd_unknown,
                                                                      VitalStatusCd.dd_unknown))
        self.add_patient_information(g, patient)

    @staticmethod
    def uri_to_patient_id(patient: URIRef) -> Tuple[str, str]:
        """
        Convert a patient URI into a patient identifier / identifier source tuple
        :param patient: patient URI
        :return: patient_id, patient_ide_source
        """
        return uri_to_ide_and_source(patient)

    def add_patient_information(self, g: Graph, patient: URIRef) -> None:
        """
        Add additional information to the patient
        :param g: Graph carrying additional facts about the patient
        :param patient: URI of the actual patient
        """
        if not g.value(patient, FHIR.animal):       # i2b2 doesn't do animals
            # gender
            gender = value(g, patient, FHIR.Patient.gender)
            if gender == "male":
                self.patient_dimension_entry._sex_cd = 'M'
            elif gender == "female":
                self.patient_dimension_entry._sex_cd = 'F'

            # deceased.deceasedBoolean --> vital_status_code.deathInd
            isdeceased = value(g, patient, FHIR.Patient.deceasedBoolean)
            if isdeceased is not None:
                self.patient_dimension_entry.deathcode = VitalStatusCd.dd_deceased if isdeceased \
                    else VitalStatusCd.dd_living

            # deceased.deceasedDateTime --> deathcode / death_date
            self.deathdate = value(g, patient, FHIR.Patient.deceasedDateTime, True)

            # birthdate - must be processed after deceased, as deceased goes into age calculation
            bd = g.value(patient, FHIR.Patient.birthDate)
            birthdate = None
            if bd:
                birthdate = extension(g, bd, "http://hl7.org/fhir/StructureDefinition/patient-birthTime",
                                      asLiteral=True)
                if not birthdate:
                    birthdate = value(g, patient, FHIR.Patient.birthDate, asLiteral=True)
            self.birthdate = birthdate

            # address -- use == home / period.end is empty or past deathcode date
            for address in g.objects(patient, FHIR.Patient.address):
                if value(g, address, FHIR.Address.use) == "home":
                    period = g.value(address, FHIR.Address.period)
                    if period and value(g, period, FHIR.Period.end) is None:
                        city = value(g, address, FHIR.Address.city)
                        state = value(g, address, FHIR.Address.state)
                        zipcode = value(g, address, FHIR.Address.postalCode)
                        if zipcode:
                            self.patient_dimension_entry._zip_cd = zipcode
                            if city and state:
                                self.patient_dimension_entry._statecityzip_path = \
                                    'Zip codes\\' + state + '\\' + city + '\\' + zipcode + '\\'

            # maritalStatus --> map to 'single', 'married', 'divorced', 'widow', other?
            # TODO: This should be done with an ontology
            ms = code(g, patient, FHIR.Patient.maritalStatus, V3.MaritalStatus)
            if ms:
                if ms != 'UNK':
                    self.patient_dimension_entry._marital_status_cd = \
                        'divorced' if ms in ['A', 'D'] else \
                        'married' if ms in ['L', 'M', 'P'] else \
                        'widow' if ms in ['W'] else \
                        'single'
            else:
                msuri = concept_uri(g, patient, FHIR.Patient.maritalStatus, SNOMEDCT)
                if msuri:
                    # TODO: figure out what to do with SNOMED id's (terminology service, anyone?)
                    pass

    @property
    def birthdate(self) -> Literal:
        return Literal(self.patient_dimension_entry.birth_date)

    @birthdate.setter
    def birthdate(self, bd: Optional[Literal]) -> None:
        if bd is None:
            self.patient_dimension_entry._birth_date = None
        else:
            # TODO: decide whether we want to refine this further
            if bd.datatype == XSD.gYear:
                self.patient_dimension_entry._vital_status_code.birthcode = VitalStatusCd.bd_year
            elif bd.datatype == XSD.gYearMonth:
                self.patient_dimension_entry._vital_status_code.birthcode = VitalStatusCd.bd_month
            elif bd.datatype == XSD.date:
                self.patient_dimension_entry._vital_status_code.birthcode = VitalStatusCd.bd_day
            else:
                self.patient_dimension_entry._vital_status_code.birthcode = VitalStatusCd.bd_hour
            self.patient_dimension_entry._birth_date = bd.toPython()

            # Age calculation --
            # TODO: figure out what to do with tzoffset
            # TODO: figure out what rdflib delivers in the toPython() function
            niave_bd = bd.toPython()
            ref_date = None
            if self.patient_dimension_entry._vital_status_code.deathcode \
                    in {VitalStatusCd.dd_living, VitalStatusCd.dd_unknown}:
                ref_date = datetime.now()
            elif self.patient_dimension_entry._death_date is not None:
                ref_date = self.patient_dimension_entry._death_date
            if ref_date is not None:
                age = ref_date.year - niave_bd.year
                if age > 0:
                    if ref_date.month > niave_bd.month:
                        age -= 1
                    elif ref_date.month == niave_bd.month:
                        if ref_date.day > niave_bd.day:
                            age -= 1
                self.patient_dimension_entry._age_in_years_num = age

    @property
    def deathdate(self) -> Literal:
        return Literal(self.patient_dimension_entry.death_date)

    @deathdate.setter
    def deathdate(self, dd: Optional[Literal]) -> None:
        if dd is None:
            self.patient_dimension_entry._death_date = None
        else:
            # TODO: decide whether we want to refine this further
            if dd.datatype == XSD.gYear:
                self.patient_dimension_entry._vital_status_code.deathcode = VitalStatusCd.dd_year
            elif dd.datatype == XSD.gYearMonth:
                self.patient_dimension_entry._vital_status_code.deathcode = VitalStatusCd.dd_month
            elif dd.datatype == XSD.date:
                self.patient_dimension_entry._vital_status_code.deathcode = VitalStatusCd.dd_day
            else:
                self.patient_dimension_entry._vital_status_code.deathcode = VitalStatusCd.dd_hour
            self.patient_dimension_entry._death_date = dd.toPython()
