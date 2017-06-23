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
from typing import List, Optional

from rdflib import RDFS, RDF, OWL, URIRef
from i2fhirb2.fhir.fhirmetadata import FHIRMetadata
from i2fhirb2.fhir.fhirspecific import FHIR
from i2fhirb2.i2b2model.i2b2modifierdimension import ModifierDimension


class FHIRModifierDimension(FHIRMetadata):
    """ A list of all FHIR predicates. """

    class UniqueEntries:
        """
        Much of the metadata tooling is created to handle the ontology file, which carries multiple entries at
        different depths.  Modifiers only need one entry, so this class exists to make sure that each modifier is
        unique.
        """
        def __init__(self):
            self.elements = {}

        def add(self, element: ModifierDimension):
            self.elements.setdefault(element.modifier_path, element)

        def as_list(self):
            return list(self.elements.values())

    def dimension_list(self, _: Optional[URIRef]=None, domain: Optional[URIRef]=None) -> List[ModifierDimension]:
        """
        Return the complete set of modifiers in the ontology
        :param _: subject - used for testing and ignored here
        :param domain: restrict to properties in this domain (e.g. FHIR.CodeableConcept)
        :return: list of modifiers
        """
        # TODO: Include references as modifiers (e.g. \FHIR\Patient\managingOrganization\)
        rval = self.UniqueEntries()
        conc_dimension = self.fhir_concepts()

        properties = self.g.subjects(RDFS.domain, domain) if domain else self.g.subjects(RDF.type, OWL.ObjectProperty)
        for prop in properties:
            if prop not in conc_dimension and not self.skipped_v5_domain(prop):
                # If this is one of the value[x] properties, value_property handles the mapping.
                # Note that the UniqueEntries() element covers duplicates
                vp = self.value_property(prop)
                if vp:
                    rval.add(ModifierDimension(vp, self._name_base))
                else:
                    rval.add(ModifierDimension(prop, self._name_base))
                    for range_ in self.g.objects(prop, RDFS.range):
                        if not self.is_primitive(range_):
                            for mod_path in self.extend_modifier_path(prop, range_):
                                rval.add(mod_path)

        # Add the special Narrative.text DatatypeProperty
        if not domain:
            rval.add(ModifierDimension(FHIR['Narrative.div'], self._name_base))
        return rval.as_list()

    def extend_modifier_path(self, prop: URIRef, range_type: URIRef) -> List[ModifierDimension]:
        """
        Synthesize a URI for embedded paths (e.g. CodeableConcept.coding.[Coding].system)
        :param prop: Base URI
        :param range_type: URI of range
        :return:
        """
        return [ModifierDimension(p.predicate, self._name_base) for p in self.generate_modifier_path(prop, range_type)]

    @staticmethod
    def tsv_header() -> str:
        return ModifierDimension._header()
