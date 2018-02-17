# Copyright (c) 2018, Mayo Clinic
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

