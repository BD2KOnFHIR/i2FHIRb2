from datetime import datetime

from rdflib import URIRef

from i2fhirb2.fhir.fhirencountermapping import FHIREncounterMapping
from i2b2model.data.i2b2visitdimension import VisitDimension, ActiveStatusCd


class FHIRVisitDimension:
    """
    For the short term, we are using the FHIR resource instance URI to uniquely identify a 'visit'
    """
    def __init__(self, resourceURI: URIRef, patient_num: int, patient_ide: str,
                 patient_ide_source: str, start_date: datetime) -> None:
        self.encounter_mappings = FHIREncounterMapping(resourceURI, patient_ide, patient_ide_source)
        self.visit_dimension_entry = \
            VisitDimension(self.encounter_mappings.encounter_num, patient_num,
                           ActiveStatusCd(ActiveStatusCd.sd_ongoing, ActiveStatusCd.ed_ongoing), start_date)
