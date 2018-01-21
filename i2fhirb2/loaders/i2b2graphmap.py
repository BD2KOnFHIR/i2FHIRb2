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
from argparse import Namespace
from datetime import datetime
from typing import List, Tuple, Optional

from fhirtordf.rdfsupport.fhirgraphutils import value
from fhirtordf.rdfsupport.uriutils import uri_to_ide_and_source
from rdflib import Graph, RDF, URIRef

from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFactFactory
from i2fhirb2.fhir.fhirpatientdimension import FHIRPatientDimension
from i2fhirb2.fhir.fhirpatientmapping import FHIRPatientMapping
from i2fhirb2.fhir.fhirresourcemap import FHIR_RESOURCE_MAP, FHIR_Infrastructure_type, FHIR_Observation_Fact_type, \
    FHIR_Visit_Dimension_type, FHIR_Provider_Dimension_type, FHIR_Patient_Dimension_type, FHIR_Bundle_type, \
    FHIR_Resource_type
from i2fhirb2.fhir.fhirspecific import FHIR
from i2fhirb2.fhir.fhirvisitdimension import FHIRVisitDimension
from i2fhirb2.i2b2model.data.i2b2encountermapping import EncounterMapping
from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFactKey, ObservationFact
from i2fhirb2.i2b2model.data.i2b2patientdimension import PatientDimension
from i2fhirb2.i2b2model.data.i2b2patientmapping import PatientMapping
from i2fhirb2.i2b2model.data.i2b2visitdimension import VisitDimension
from i2fhirb2.i2b2model.shared.i2b2core import I2B2Core
from i2fhirb2.sqlsupport.dbconnection import I2B2Tables
from i2fhirb2.sqlsupport.i2b2tables import change_column_length
from i2fhirb2.tsv_support.tsvwriter import write_tsv


# TODO: Handle continuation pages in queries and bundles

class I2B2GraphMap:
    def __init__(self, g: Graph, opts: Namespace) -> None:
        """
        Iterate over the resources in the graph mapping them to their i2b2 equivalent
        :param g: graph
        :param opts: input options
        """
        self._opts = opts
        self._g = g
        self.num_infrastructure = 0         # Number of infrastructure resources encountered (and not loaded)
        self.num_visit = 0                  # Number of visit resources (to be implemented)
        self.num_provider = 0               # Number of provider resources
        self.num_bundle = 0                 # Number of bundler resources (we should be unwrapping these?)
        self.num_unmapped = 0               # Number of untyped resources encountered (need classifying)
        self.observation_facts = []         # type: List[ObservationFact]
        self.patient_dimensions = []        # type: List[PatientDimension]
        self.patient_mappings = []          # type: List[PatientMapping]
        self.visit_dimensions = []          # type: List[VisitDimension]
        self.encounter_mappings = []        # type: List[EncounterMapping]
        self.tables = opts.tables           # type: I2B2Tables
        nresources = 0
        for subj, subj_type in g.subject_objects(RDF.type):
            if isinstance(subj, URIRef) and subj_type in FHIR_RESOURCE_MAP:
                print("{}: ({}) - {}".format(nresources, str(subj_type).split('/')[-1], subj))
                nresources += 1
                mapped_type = FHIR_RESOURCE_MAP[subj_type]
                if isinstance(mapped_type, FHIR_Infrastructure_type):
                    self.num_infrastructure += 1
                elif isinstance(mapped_type, FHIR_Observation_Fact_type):
                    pm, vd, start_date = self.process_resource_instance(subj, mapped_type)
                    if pm is not None:
                        obsfactory = \
                            FHIRObservationFactFactory(g, ObservationFactKey(pm.patient_num,
                                                                             vd.visit_dimension_entry.encounter_num,
                                                                             opts.providerid, start_date), subj)
                        # TODO: Decide what do do with the other mappings in the observation factory
                        self.observation_facts += obsfactory.observation_facts
                elif isinstance(mapped_type, FHIR_Visit_Dimension_type):
                    self.num_visit += 1
                elif isinstance(mapped_type, FHIR_Provider_Dimension_type):
                    self.num_provider += 1
                elif isinstance(mapped_type, FHIR_Patient_Dimension_type):
                    pd = FHIRPatientDimension(self._g, self.tables, subj)
                    self.patient_dimensions.append(pd.patient_dimension_entry)
                    self.patient_mappings += pd.patient_mappings.patient_mapping_entries
                elif isinstance(mapped_type, FHIR_Bundle_type):
                    self.num_bundle += 1
                else:
                    self.num_unmapped += 1
        print("---> Graph map phase complete")

    def process_resource_instance(self, subj: URIRef,  mapped_type: FHIR_Resource_type) \
            -> Tuple[Optional[FHIRPatientMapping], Optional[FHIRVisitDimension], Optional[datetime]]:
        patient_id_uri, encounter_id_uri, provider_id = mapped_type.fact_key_for(self._g, subj)
        if patient_id_uri is not None:
            patient_id, patient_ide_source = uri_to_ide_and_source(patient_id_uri)
            pm = FHIRPatientMapping(self.tables, patient_id, patient_ide_source)
            self.patient_mappings += pm.patient_mapping_entries
            start_date = value(self._g, subj, FHIR.Observation.effectiveDateTime)
            if not start_date:
                start_date = datetime.now()
            vd = FHIRVisitDimension(subj, pm.patient_num, patient_id, patient_ide_source, start_date)
            self.visit_dimensions.append(vd.visit_dimension_entry)
            self.encounter_mappings += vd.encounter_mappings.encounter_mapping_entries
            return pm, vd, start_date
        else:
            # Just a reference to a resource instance -- drop it
            return None, None, None

    def generate_tsv_files(self) -> None:
        self._generate_tsv_file("observation_fact.tsv", ObservationFact, self.observation_facts)
        self._generate_tsv_file("patient_dimension.tsv", PatientDimension, self.patient_dimensions)
        self._generate_tsv_file("patient_mapping.tsv", PatientMapping, self.patient_mappings)
        self._generate_tsv_file("visit_dimension.tsv", VisitDimension, self.visit_dimensions)
        self._generate_tsv_file("encounter_mapping.tsv", EncounterMapping, self.encounter_mappings)

    def _generate_tsv_file(self, fname: str, cls, values: List[I2B2Core]) -> None:
        write_tsv(self._opts.outdir, fname, cls._header(), values)

    @staticmethod
    def clear_i2b2_tables(tables: I2B2Tables, uploadid: int) -> None:
        """
        Remove all entries in the i2b2 tables for uploadid.
        :param tables:
        :param uploadid:
        :return:
        """
        # This is a static function to support the removefacts operation
        print("Deleted {} patient_dimension records"
              .format(PatientDimension.delete_upload_id(tables, uploadid)))
        print("Deleted {} patient_mapping records"
              .format(PatientMapping.delete_upload_id(tables, uploadid)))
        print("Deleted {} observation_fact records"
              .format(ObservationFact.delete_upload_id(tables, uploadid)))
        print("Deleted {} visit_dimension records"
              .format(VisitDimension.delete_upload_id(tables, uploadid)))
        print("Deleted {} encounter_mapping records"
              .format(EncounterMapping.delete_upload_id(tables, uploadid)))

    @staticmethod
    def clear_i2b2_sourcesystems(tables: I2B2Tables, sourcesystemcd: str) -> None:
        print("Deleted {} patient_dimension records"
              .format(PatientDimension.delete_sourcesystem_cd(tables, sourcesystemcd)))
        print("Deleted {} patient_mapping records"
              .format(PatientMapping.delete_sourcesystem_cd(tables, sourcesystemcd)))
        print("Deleted {} observation_fact records"
              .format(ObservationFact.delete_sourcesystem_cd(tables, sourcesystemcd)))
        print("Deleted {} visit_dimension records"
              .format(VisitDimension.delete_sourcesystem_cd(tables, sourcesystemcd)))
        print("Deleted {} encounter_mapping records"
              .format(EncounterMapping.delete_sourcesystem_cd(tables, sourcesystemcd)))

    def load_i2b2_tables(self, check_dups=False) -> None:
        # session = sessionmaker(bind=tables.crc_engine)()
        I2B2Core._check_dups = check_dups
        if self._opts.remove:
            # TODO: This should really be within a transaction boundary
            self.clear_i2b2_tables(self._opts.tables, self._opts.uploadid)
        change_column_length(self._opts.tables.observation_fact, self._opts.tables.observation_fact.c.concept_cd,
                             200, self._opts.tables.crc_connection)
        change_column_length(self._opts.tables.observation_fact, self._opts.tables.observation_fact.c.modifier_cd,
                             200, self._opts.tables.crc_connection)
        print("{} / {} patient_dimension records added / modified"
              .format(*PatientDimension.add_or_update_records(self._opts.tables, self.patient_dimensions)))
        print("{} / {} patient_mapping records added / modified"
              .format(*PatientMapping.add_or_update_records(self._opts.tables, self.patient_mappings)))
        print("{} / {} visit_dimension records added / modified"
              .format(*VisitDimension.add_or_update_records(self._opts.tables, self.visit_dimensions)))
        print("{} / {} encounter_mapping records added / modified"
              .format(*EncounterMapping.add_or_update_records(self._opts.tables, self.encounter_mappings)))
        print("{} / {} observation_fact records added / modified"
              .format(*ObservationFact.add_or_update_records(self._opts.tables, self.observation_facts)))
        # session.close()

    def summary(self) -> str:
        summary_text = """Generated:
    {} Observation facts
    {} Patients
    {} Patient mappings
"""
        skip_text = """=== SKIPS ===
    {num_bundle} Bundled resources (shouldn't happen?)
    {num_visit} Visit resources
    {num_infrastructure} Infrastructure resources
    {num_provider} Provider resources
    {num_unmapped} Unmapped resources
"""
        num_skips = self.num_infrastructure + self.num_visit + self.num_provider + self.num_unmapped + self.num_bundle
        rval = summary_text.format(len(self.observation_facts),
                                   len(self.patient_dimensions),
                                   len(self.patient_mappings))
        if num_skips:
            rval += skip_text.format(**self.__dict__)
        return rval
