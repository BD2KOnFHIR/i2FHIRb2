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
from typing import Optional, List

from fhirtordf.rdfsupport.fhirgraphutils import value, extension, concept_uri, codeable_concept_code
from fhirtordf.rdfsupport.namespaces import FHIR, SNOMEDCT, V3
from fhirtordf.rdfsupport.uriutils import parse_fhir_resource_uri
from rdflib import Graph, URIRef, Literal, XSD

from i2fhirb2.fhir.fhirpatientmapping import FHIRPatientMapping
from i2fhirb2.i2b2model.data.i2b2codes import I2B2DemographicsCodes
from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFact, ObservationFactKey
from i2fhirb2.i2b2model.data.i2b2patientdimension import PatientDimension, VitalStatusCd
# TODO: is there any reason to pull patient_id from Patient.identifier rather than URL?
# TODO: what of foreign addresses?
from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientIDEStatus
from i2fhirb2.sqlsupport.i2b2tables import I2B2Tables


class FHIRPatientDimension:
    def __init__(self, g: Graph, tables: Optional[I2B2Tables], patient: URIRef) -> None:
        """
        Generate i2b2 patient dimension and patient_mapping records from PATIENT resources in graph g

        :param g: Graph containing 0 or more FHIR Patient resources
        :param tables: i2b2 tables connection if we are using a database (vs. tsv output)
        :param patient: Graph subject
        """
        assert value(g, patient, FHIR.animal) is None       # We don't do animals
        parsed_resource = parse_fhir_resource_uri(patient)
        self.patient_mappings = FHIRPatientMapping(tables, parsed_resource.resource, str(parsed_resource.namespace))
        active = value(g, patient, FHIR.Patient.active)
        if active is not None and not active:
            self.patient_mappings._patient_ide_status = PatientIDEStatus.inactive
        self.patient_dimension_entry = PatientDimension(self.patient_mappings.patient_num,
                                                        VitalStatusCd(VitalStatusCd.bd_unknown,
                                                                      VitalStatusCd.dd_unknown))

        # Additional attributes that don't go into patient dimension but are recorded as observation facts
        self._language = None
        self._marital_status = None
        self._race = None
        self._religion = None
        self.add_patient_information(g, patient)

    def add_patient_information(self, g: Graph, patient: URIRef) -> None:
        """
        Add additional information to the patient
        :param g: Graph carrying additional facts about the patient
        :param patient: URI of the actual patient
        """
        if not g.value(patient, FHIR.Patient.animal):       # i2b2 doesn't do animals
            # gender
            gender = value(g, patient, FHIR.Patient.gender)
            if gender == "male":
                self.patient_dimension_entry._sex_cd = 'M'
            elif gender == "female":
                self.patient_dimension_entry._sex_cd = 'F'
            elif gender == "other":
                self.patient_dimension_entry._sex_cd = 'U'

            # deceased.deceasedBoolean --> vital_status_code.deathInd
            isdeceased = value(g, patient, FHIR.Patient.deceasedBoolean)
            if isdeceased is not None:
                self.patient_dimension_entry._vital_status_cd = VitalStatusCd.dd_deceased if isdeceased \
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
            addresses = g.objects(patient, FHIR.Patient.address)
            for address in addresses:
                address_use = value(g, address, FHIR.Address.use)
                if address_use is None or address_use == "home":
                    period = g.value(address, FHIR.Address.period)
                    if not period or (period and value(g, period, FHIR.Period.end) is None):
                        city = value(g, address, FHIR.Address.city)
                        state = value(g, address, FHIR.Address.state)
                        zipcode = value(g, address, FHIR.Address.postalCode)
                        if zipcode:
                            self.patient_dimension_entry._zip_cd = zipcode
                            if city and state:
                                self.patient_dimension_entry._statecityzip_path = \
                                    'Zip codes\\' + state + '\\' + city + '\\' + zipcode + '\\'

            # maritalStatus --> map to 'single', 'married', 'divorced', 'widow', other?
            marital_stati = codeable_concept_code(g, patient, FHIR.Patient.maritalStatus)
            for ms in marital_stati:
                if ms.system == str(V3.MaritalStatus):
                    self._marital_status = marital_stati[0]
                    msc = self._marital_status.code
                    if msc != 'UNK':
                        self.patient_dimension_entry._marital_status_cd = \
                            'divorced' if msc in ['A', 'D'] else \
                            'married' if msc in ['L', 'M', 'P'] else \
                            'widow' if msc in ['W'] else \
                            'single'
                    break
            else:
                msuri = concept_uri(g, patient, FHIR.Patient.maritalStatus, SNOMEDCT)
                if msuri:
                    # TODO: figure out what to do with SNOMED id's (terminology service, anyone?)
                    pass

            # language
            communications = list(g.objects(patient, FHIR.Patient.communication))
            language = None
            for communication in communications:
                pref = value(g, communication, FHIR.Patient.communication.preferred)
                if pref or (pref is None and len(communications) == 1):
                    languages = codeable_concept_code(g, communication, FHIR.Patient.communication.language)
                    if languages:
                        language = languages[0]
                        break

            if language is not None:
                self._language = language.code

            # race - not a part of the core fhir spec or known extensions

            # religion

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

    def as_observation_facts(self, encounter_num: int, provider_id: str, start_date: datetime) -> List[ObservationFact]:
        rval = []
        pde = self.patient_dimension_entry
        ofk = ObservationFactKey(self.patient_dimension_entry.patient_num, encounter_num, provider_id, start_date)

        # Age entry
        rval.append(ObservationFact(ofk, I2B2DemographicsCodes.age(pde.age_in_years_num)))

        # Sex
        rval.append(ObservationFact(ofk, 
                                    I2B2DemographicsCodes.sex_female if pde.sex_cd == 'F'
                                    else I2B2DemographicsCodes.sex_male if pde.sex_cd == 'M'
                                    else I2B2DemographicsCodes.sex_undifferentiated if pde.sex_cd == 'U'
                                    else I2B2DemographicsCodes.sex_unknown))

        # Birthdate
        if pde.birth_date:
            bd_of = ObservationFact(ofk, I2B2DemographicsCodes.birthdate)
            bd_of._date_val(pde.birth_date)
            rval.append(bd_of)

        # Deathdate
        if pde.death_date:
            dd_of = ObservationFact(ofk, I2B2DemographicsCodes.birthdate)
            dd_of._date_val(pde.death_date)
            rval.append(dd_of)

        # Language
        rval.append(ObservationFact(ofk, I2B2DemographicsCodes.language(self._language)))

        # Marital status
        rval.append(ObservationFact(ofk, I2B2DemographicsCodes.marital_status(self._marital_status)))

        # race
        rval.append(ObservationFact(ofk, I2B2DemographicsCodes.race(self._race)))

        # religion
        # Religion codes currently like the FHIR
        rval.append(ObservationFact(ofk, I2B2DemographicsCodes.religion(self._religion)))

        # vital -- no idea what vital_deferred means
        rval.append(
            ObservationFact(ofk,
                            I2B2DemographicsCodes.vital_living
                            if pde._vital_status_code.dd_deceased == VitalStatusCd.dd_living
                            else I2B2DemographicsCodes.vital_unknown if pde._vital_status_code.dd_unknown
                            else I2B2DemographicsCodes.vital_dead))

        # zip
        rval.append(ObservationFact(ofk, I2B2DemographicsCodes.zip(pde.zip_cd)))

        return rval
