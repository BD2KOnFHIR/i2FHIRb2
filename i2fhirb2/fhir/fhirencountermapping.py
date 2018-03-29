from typing import Dict, Tuple, Optional

from fhirtordf.rdfsupport.uriutils import parse_fhir_resource_uri
from rdflib import URIRef
from rdflib.namespace import split_uri
from sqlalchemy import func, or_
from sqlalchemy.orm import sessionmaker

from i2fhirb2.common_cli_parameters import DEFAULT_PROJECT_ID, DEFAULT_ENCOUNTER_NUMBER_START, IDE_SOURCE_HIVE
from i2b2model.data.i2b2encountermapping import EncounterMapping, EncounterIDEStatus
from i2b2model.sqlsupport.dbconnection import I2B2Tables


class EncounterNumberGenerator:
    """
    i2b2 encounter number generator.
    """
    def __init__(self, next_number: int) -> None:
        """
        Create the number generator
        :param next_number: First encounter number to assign
        """
        self._next_number = next_number

    def new_number(self) -> int:
        """
        Return a new encounter number
        :return:
        """
        rval = self._next_number
        self._next_number += 1
        return rval

    def refresh(self, tables: I2B2Tables, ignore_upload_id: Optional[int]) -> int:
        """
        Determine the greatest encounter number that is currently in use and set the next number to one greater
        :param tables: i2b2 SQL tables
        :param ignore_upload_id: If present, encounters with this upload id are ignored.  This is used in cases when
        an upload is being replaced.
        :return: next number
        """
        session = sessionmaker(bind=tables.crc_engine)()
        q = func.max(tables.visit_dimension.c.encounter_num)
        if ignore_upload_id is not None:
            q = q.filter(or_(tables.visit_dimension.c.upload_id.is_(None),
                         tables.visit_dimension.c.upload_id != ignore_upload_id))
        qr = session.query(q).all()
        self._next_number = qr[0][0] + 1
        session.close()
        return self._next_number


class FHIREncounterMapping:
    project_id = DEFAULT_PROJECT_ID         # Project identifier
    identity_source_id = IDE_SOURCE_HIVE    # source_id for identity mapping
    number_generator = EncounterNumberGenerator(DEFAULT_ENCOUNTER_NUMBER_START)
    number_map = dict()                     # type: Dict[Tuple[str, str, str, str, str], int]

    @classmethod
    def _clear(cls) -> None:
        """
        Reset the mapping table to its default. (Primarily used for testing)
        """
        cls.project_id = DEFAULT_PROJECT_ID
        cls.identity_source_id = IDE_SOURCE_HIVE
        cls.number_generator = EncounterNumberGenerator(DEFAULT_ENCOUNTER_NUMBER_START)
        cls.number_map.clear()

    @classmethod
    def refresh_encounter_number_generator(cls, tables: I2B2Tables, ignore_upload_id: Optional[int]) -> int:
        """
        Reset the generator
        :param tables: i2b2 tables
        :param ignore_upload_id: if present, do not look at the encounter numbers from this upload
        :return: starting encounter number
        """
        return cls.number_generator.refresh(tables, ignore_upload_id)

    def __init__(self, encounterURI: URIRef, patient_id: str, patient_ide_source: str) -> None:
        """
        Create a new encounter mapping entry
        :param encounterURI: URI of the encounter
        :param patient_id: Associated patient identifier
        :param patient_ide_source: Associated patient identifier source
        """
        self.encounter_mapping_entries = []
        parsed_resource = parse_fhir_resource_uri(encounterURI)
        resource_namespace = str(parsed_resource.namespace)
        resource_ide = split_uri(parsed_resource.resource_type)[1] + '/' + parsed_resource.resource
        key = (resource_ide, resource_namespace, self.project_id, patient_id, patient_ide_source)
        if key in self.number_map:
            self.encounter_num = self.number_map[key]
        else:
            self.encounter_num = self.number_generator.new_number()
            pm = EncounterMapping(resource_ide, resource_namespace, self.project_id,
                                  self.encounter_num, patient_id, patient_ide_source, EncounterIDEStatus.active)
            self.number_map[key] = self.encounter_num
            self.encounter_mapping_entries.append(pm)

        identity_id = str(self.encounter_num)
        ikey = (identity_id, self.identity_source_id, self.project_id)
        if ikey not in self.number_map:
            ipm = EncounterMapping(identity_id,
                                   self.identity_source_id,
                                   self.project_id,
                                   self.encounter_num,
                                   patient_id,
                                   patient_ide_source,
                                   EncounterIDEStatus.active)
            self.encounter_mapping_entries.append(ipm)
