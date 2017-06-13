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
from typing import List, Callable, Optional

from rdflib import Namespace, Graph, URIRef, RDFS
from rdflib.namespace import split_uri

W5 = Namespace("http://hl7.org/fhir/w5#")
FHIR = Namespace("http://hl7.org/fhir/")
nsmap = {str(W5): "W5",
         str(FHIR): "FHIR"}


def concept_path(subject: URIRef) -> str:
    """
    Convert subject into an i2b2 concept path fragment.
    Example: Patient.status --> Patient\\status\\
    :param subject: FHIR URI
    :return: i2b2 path fragment
    """
    return split_uri(subject)[1].replace('.', '\\') + '\\'


def concept_code(subject: URIRef) -> str:
    """
    Return the i2b2 concept code for subject
    :param subject:
    :return:
    """
    ns, code = split_uri(subject)
    return nsmap[ns] + ':' +  code


def concept_name(g: Graph, subject: URIRef) -> str:
    """
    Return the i2b2 concept name for subject
    :param g: Graph - used to access label
    :param subject: concept subject
    :return: Name derived from lable if it exists otherwise the URI itself
    """
    # Note - labels appear to have '.' in them as well
    return str(g.label(subject, split_uri(subject)[1])).replace('.', ' ')


def modifier_path(modifier: URIRef) -> str:
    """
    Convert modifier uri into an i2b2 modifier path fragment, removing the first part of the name
    Example: CodedEntry.code.text --> code\\text\\
    :param modifier: FHIR URI
    :return: i2b2 path fragment
    """
    path = split_uri(modifier)[1]
    return (path.split('.', 1)[1].replace('.', '\\') if '.' in path else path)  + '\\'


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


# List of W5 categores that should not be included in the output
w5_infrastructure_categories = {W5.conformance, W5.infrastructure, W5.information}
recursive_fhir_types = {FHIR.TermComponent, FHIR.Extension, FHIR.Meta, FHIR.QuestionnaireItemComponent,
                        FHIR.Quantity, FHIR.SimpleQuantity, FHIR.QuestionnaireResponseItemComponent,
                        FHIR.SectionComponent, FHIR.GraphDefinitionLinkComponent, FHIR.GraphDefinitionLinkTargetComponent}
skip_fhir_predicates = {FHIR['index'], FHIR.nodeRole, FHIR['id']}


def w5_infrastructure_category(g: Graph, subj: URIRef) -> bool:
    """
    Determine whether subj belongs to a w5 infrastructure category
    :param g: Graph for transitive parent traversal
    :param subj: FHIR Element
    :return:
    """
    return bool(set(g.transitive_objects(subj, RDFS.subClassOf)).intersection(w5_infrastructure_categories))


def is_w5_uri(uri: URIRef) -> bool:
    return split_uri(uri)[0] == str(W5)


def is_w5_path(path: List[URIRef]) -> bool:
    """
    Determine whether path represents a primary w5 path.  This exists to remove the alternate
    paths that culminate in fhir:Thing.
    :param path: path to test
    :return: True if it is a single length path (e.g. Patient.status) or has a non-skipped w5
    category in its ancestors.
    """
    if len(path) > 1:
        if split_uri(path[0])[0] != str(W5):
            return False
    if bool(set(path).intersection(w5_infrastructure_categories)):
        print("Skipping {}".format('.'.join(split_uri(e)[1] for e in path)))
        return False
    return not bool(set(path).intersection(w5_infrastructure_categories))


def full_paths(g: Graph, subject: URIRef, predicate: URIRef) -> List[List[URIRef]]:
    parents = [obj for obj in g.objects(subject, predicate) if isinstance(obj, URIRef)]
    if not parents:
        rval = [[subject]]
    else:
        rval = []
        for parent in parents:
            for e in full_paths(g, parent, predicate):
                e.append(subject)
                rval.append(e)
    return rval


def i2b2_paths(base: str, g: Graph, subject: URIRef, predicate: URIRef,
               filtr: Optional[Callable[[List[URIRef]], bool]]=None) -> [str]:
    rval = []
    for path in full_paths(g, subject, predicate):
        if not filtr or filtr(path):
            rval.append(base + (''.join(concept_path(e) for e in path[:-1])))
    return rval
