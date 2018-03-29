from fhirtordf.rdfsupport.namespaces import namespace_for
from i2b2model.metadata.i2b2modifierdimension import ModifierDimension
from rdflib import Graph, URIRef
from rdflib.namespace import split_uri

from i2fhirb2.fhir.fhirspecific import concept_path, concept_code


class FHIRModifierDimension(ModifierDimension):
    graph: Graph = None

    def __init__(self, subject: URIRef, subject_name: str, base_path: str = '\\FHIR\\') -> None:
        """ FHIR wrapper for ModifierDimension

        :param subject: URI of the subject
        :param subject_name: name of subject
        :param base_path: base path of items
        """
        ns, code = split_uri(subject)
        ns_prefix = namespace_for(ns).upper()
        super().__init__(ns_prefix, code, subject_name, concept_path(subject)[:-1].split('\\'), base_path)

    def path(self) -> str:
        return self._base_path + self._subject_path

    def name_char_(self) -> str:
        return self._name
