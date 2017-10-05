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

from fhirtordf.rdfsupport.namespaces import W5, FHIR, namespace_for
from rdflib import Graph, URIRef
from rdflib.namespace import split_uri


# TODO: move this to a stable version when R4 is adopted
DEFAULT_FMV = "http://build.fhir.org/"
DEFAULT_PROVIDER_ID = "FHIR:DefaultProvider"


# List of W5 categores that should not be included in the output
w5_infrastructure_categories = {W5.conformance, W5.infrastructure, W5.information}

# List of predicates that aren't a direct part of the i2b2 structure
skip_fhir_predicates = {FHIR.index, FHIR.nodeRole, FHIR['id']}

# List of FHIR 'primitive' types, not to be further expanded
fhir_primitives = {FHIR.Reference}

ide_source_hive = "HIVE"        # Identity source for patient and encounter mapping tables


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
    return (path.split('.', 1)[1].replace('.', '\\') if '.' in path else path) + '\\'


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
    p1 = split_uri(mod)
    if len(p1) < 2:
        print("E1")
    p2 = p1[1].rsplit('.', 1)
    if len(p2) < 2:
        print("E2")
    last_mod_component = split_uri(mod)[1].rsplit('.', 1)[1]
    return URIRef(str(parent) + '.' + last_mod_component)


def is_w5_uri(uri: URIRef) -> bool:
    return split_uri(uri)[0] == str(W5)
