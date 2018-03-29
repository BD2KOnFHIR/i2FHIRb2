from typing import Optional, Tuple, Union

from fhirtordf.rdfsupport.namespaces import W5, FHIR, namespace_for
from rdflib import Graph, URIRef
from rdflib.namespace import split_uri, RDFS, NAME_START_CATEGORIES
from rdflib.term import Node, BNode, Literal


DEFAULT_SOURCE_SYSTEM = 'FHIR STU3'
DEFAULT_BASE = 'FHIR'
DEFAULT_BASE_PATH = '\\{}\\'.format(DEFAULT_BASE)

# List of W5 categores that should not be included in the output
w5_infrastructure_categories = {W5.conformance, W5.infrastructure, W5.information}

# List of predicates that aren't a direct part of the i2b2 structure
skip_fhir_predicates = {FHIR.index, FHIR.nodeRole, FHIR['id']}
skip_fhir_types = {FHIR.BackboneElement, FHIR.Element, FHIR.Resource}

# List of FHIR 'primitive' types, not to be further expanded
# TODO: FHIR.Reference shouldn't be in this list
fhir_primitives = {FHIR.Reference, FHIR.index, FHIR.nodeRole, FHIR.value}

# rdflib is a bit too strict when it comes to URI's.  This fix allows numeric codes
if 'Nd' not in NAME_START_CATEGORIES:
    NAME_START_CATEGORIES.append('Nd')


def concept_path_sans_root(subject: URIRef) -> str:
    """
    Generate a concept path without the root node (e.g. Observation//component//code --> component//code
    :param subject: URI to trim
    :return: resulting path
    """
    return concept_path(subject).split('\\', 1)[1]


def concept_path(subject: URIRef) -> str:
    """
    Convert subject into an i2b2 concept path fragment.
    Example: Patient.status --> Patient\\status\\
    :param subject: FHIR URI
    :return: i2b2 path fragment
    """
    subj_path = split_uri(subject)[1]
    if is_w5_uri(subject):
        return (subj_path.rsplit('.', 1)[1] if '.' in subj_path else subj_path) + '\\'
    else:
        return split_uri(subject)[1].replace('.', '\\') + '\\'


def concept_code(subject: URIRef) -> str:
    """
    Return the i2b2 concept code for subject
    :param subject: URI to convert
    :return: 'ns:code' form of URI
    """
    ns, code = split_uri(subject)

    return '{}:{}'.format(namespace_for(ns).upper(), code)


def concept_name(g: Graph, subject: URIRef) -> str:
    """
    Return the i2b2 concept name for subject
    :param g: Graph - used to access label
    :param subject: concept subject
    :return: Name derived from label if it exists otherwise the URI itself
    """
    # Note - labels appear to have '.' in them as well
    return str(g.label(subject, split_uri(subject)[1])).replace('.', ' ')


def modifier_path(modifier: URIRef) -> str:
    """
    Convert modifier uri into an i2b2 modifier path fragment, removing the first part of the name
    Example: CodedEntry.code.text --> code\text\
    :param modifier: FHIR URI
    :return: i2b2 path fragment
    """
    path = split_uri(modifier)[1]
    return (path.split('.', 1)[1].replace('.', '\\') if '.' in path else path) + '\\'


def rightmost_element(uri: URIRef) -> str:
    """
    Isolate the rightmost element in a URI path.
    Example: CodedEntry.code.text --> \text\
             CodedEntry           --> \
    :param uri: input URI
    :return: rightmost element in path form
    """
    uri_path = split_uri(uri)[1]
    return '\\' + ((uri_path.rsplit('.', 1)[1] + '\\') if '.' in uri_path else "")


def modifier_code(modifier: URIRef) -> str:
    """
    Return the i2b2 modifier code for subject.  Output is same as concept_code
    :param modifier:
    :return:
    """
    return concept_code(modifier)


def modifier_name(g: Graph, modifier: URIRef) -> str:
    """
    Return the i2b2 concept name for modifier removing the first part of the name
    :param g: Graph - used to access label
    :param modifier: concept subject
    :return: Name derived from lable if it exists otherwise the URI itself
    """
    default_name = split_uri(modifier)[1]
    full_name = str(g.label(modifier, default_name))
    if '.' in full_name:
        full_name = default_name.split('.', 1)[1]        # Remove first name segment
    return full_name.replace('.', ' ')


def composite_uri(parent: URIRef, mod: URIRef) -> URIRef:
    """
    Return a composite URI consisting of the parent + '.' + the last element in the modifier
    :param parent: base URI
    :param mod: modifier URI
    :return: composite
    """
    p1 = split_uri(mod)[1]
    return URIRef(str(parent) + '.' + (p1.rsplit('.', 1)[1] if '.' in p1 else p1))


def is_w5_uri(uri: URIRef) -> bool:
    return split_uri(uri)[0] == str(W5)


def is_primitive(g: Graph, subj: Node) -> bool:
    """
    Determine whether subj is an instance of a FHIR primitive type
    :param g: Graph context for testing
    :param subj: element to test
    :return:
    """
    parents = set(g.objects(subj, RDFS.subClassOf))
    return FHIR.Primitive in parents or subj in fhir_primitives


def instance_is_primitive(g: Graph, obj: Optional[Node]) -> bool:
    """
    Determine whether obj is a FHIR 'primitive', which we can identify by testing for a fhir:value entry
    :param g: Graph context for testing
    :param obj: object to test
    :return:
    """
    if obj is None or not isinstance(obj, BNode):
        return False
    obj_vals = list(g.objects(obj, FHIR.value))
    return len(obj_vals) == 1 and isinstance(obj_vals[0], Literal)
