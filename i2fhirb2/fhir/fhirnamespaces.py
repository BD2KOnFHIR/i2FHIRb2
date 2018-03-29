from typing import Union, ChainMap, Optional

from fhirtordf.rdfsupport.namespaces import AnonNS, namespaces as fhirtordf_namespaces, FHIR, SCT
from fhirtordf.rdfsupport.numericnamespace import NumericNamespace
from rdflib import Namespace, URIRef


HGNC = Namespace("http://www.genenames.org/")
RXNORM = NumericNamespace("http://www.nlm.nih.gov/research/umls/rxnorm/")

# Note that this is a different namespace than the one that is included in the type arc
SNOMED = Namespace("http://snomed.info/sct/")


namespaces = ChainMap(fhirtordf_namespaces,
                      {"hgnc": str(HGNC),
                       "rxnorm": str(RXNORM)
                       })


def fhir_namespace_for(uri: Union[URIRef, Namespace, str]) -> Optional[str]:
    """
    Reverse namespace lookup.  Note that returned namespace may not be unique

    :param uri: namespace URI
    :return: namespace (lower case form)
    """
    uri = str(uri)
    if not uri.endswith(('#', '/')):
        uri += '/'
    if uri not in namespaces.values():
        if uri.startswith(str(FHIR)):
            ns = uri[len(str(FHIR)):-1]
            namespaces[ns] = uri
        elif uri == str(SNOMED):
            return fhir_namespace_for(SCT)
        else:
            return None
    return [k for k, v in namespaces.items() if uri == v][0]

