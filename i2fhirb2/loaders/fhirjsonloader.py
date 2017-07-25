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
from typing import Optional
from rdflib import Graph

from i2fhirb2.loaders.fhircollectionloader import FHIRCollection
from i2fhirb2.loaders.fhirresourceloader import FHIRResource


def fhir_json_to_rdf(metavoc: Graph, json_fname: str, base_uri: str, target_graph: Optional[Graph]=None) -> Graph:
    if target_graph is None:
        target_graph = Graph()
    data = FHIRResource.load_file_or_uri(json_fname)
    if 'resourceType' in data and data.resourceType != 'Bundle':
        FHIRResource(metavoc, None, base_uri, data, target=target_graph, add_ontology_header=False)
    elif 'entry' in data and isinstance(data.entry, list) and 'resource' in data.entry[0]:
        FHIRCollection(metavoc, None, base_uri, data, target=target_graph, add_ontology_header=False)
    else:
        print("File does not appear to be a FHIR resource")
    return target_graph