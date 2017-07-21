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
import os
import sys
from argparse import ArgumentParser, Namespace
from datetime import datetime
from typing import List, Optional, Any

from rdflib import Graph

from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact, FHIRObservationFactFactory
from i2fhirb2.generate_i2b2 import Default_Sourcesystem_Code, Default_Path_Base
from i2fhirb2.i2b2model.data.i2b2observationfact import ObservationFactKey


# TODO: merge this function and generate_i2b2
def pluralize(cnt: int, base: Any) -> str:
    """
    Pluralize base based on the number in cnt
    :param cnt: number of elements
    :param base: base word
    :return: plural
    """
    return str(base) + ('s' if cnt != 1 else '')

def remove_existing_facts(opts: Namespace, ofk: ObservationFactKey) -> None:
    # TODO: Remove any entries in the file or observation_fact table that match the key
    pass


def add_facts_to_table(facts: FHIRObservationFactFactory, opts: Namespace) -> bool:
    if opts.outdir:
        fname = os.path.join(opts.outdir, "fhir_observation_fact.tsv")
        print("Creating {}".format(fname))
        with open(fname, 'w') as outf:
            outf.write(FHIRObservationFact._header() + '\n')
            for fact in facts.facts:
                outf.write(repr(fact) + '\n')
        print("  {} records generated".format(len(facts.facts)))
    else:
        table = opts.tables.observation_fact
        nins = opts.tables.crc_connection.execute(table.insert(), [fact._freeze() for fact in facts.facts])
        print("{} {} {} inserted".format(nins, table, pluralize(nins, "record")))
    return True


def load_observation_facts(g: Graph, opts: Namespace) -> FHIRObservationFactFactory:
    ofk = ObservationFactKey(opts.patnum, opts.encounter, opts.provider)
    FHIRObservationFact.sourcesystem_cd = opts.sourcesystem
    return FHIRObservationFactFactory(g, ofk, None)


def load_rdf_graph(opts: Namespace) -> Graph:
    g = Graph()

    def load_file(dirname, fname):
        filepath = os.path.join(dirname, fname)
        print("--> loading {}".format(filepath))
        g.load(filepath, format="turtle")

    if opts.file:
        load_file("", opts.file)
    else:
        for dirpath, _, filenames in os.walk(opts.dir):
            for filename in filenames:
                if filename.endswith(".ttl"):
                    g.load(dirpath, filename)

    return g


def create_parser() -> ArgumentParser:
    """
    Create a command line parser
    :return: parser
    """
    parser = ArgumentParser(description="Load FHIR Resource Data into i2b2 Observation Fact Table")
    parser.add_argument("-f", "--file", help="URL or name of input .ttl file")
    parser.add_argument("-d", "--indir", help="URI of server or directory of input files")
    parser.add_argument("-o", "--outdir", help="Output directory to store .tsv files. "
                                               "If absent, no .tsv files are generated.")
    parser.add_argument("--sourcesystem",
                        default=Default_Sourcesystem_Code,
                        help="sourcesystem code. (default: \"{}\")".format(Default_Sourcesystem_Code))
    parser.add_argument("--base",
                        default=Default_Path_Base,
                        help="Concept dimension and ontology base path. (default:\"{}\")".format(Default_Path_Base))
    parser.add_argument("-l", "--load", help="Load i2b2 SQL tables", action="store_true")
    parser.add_argument("-p", "--patnum", help="i1b2 patient number", type=int)
    parser.add_argument("-e", "--encounter", help="i2b2 encounter number", type=int)
    parser.add_argument("-pr", "--provider", help="i2b2 provider identifier")
    return parser


def genargs(argv: List[str]) -> Optional[Namespace]:
    opts = create_parser().parse_args(argv)
    if not (opts.file or opts.indir):
        print("Either an input file or input directory must be supplied", file=sys.stderr)
        return None
    opts.updatedate = datetime.now()
    if opts.indir and not opts.indir.endswith(os.sep):
        opts.indir = os.path.join(opts.indir, '')
    if opts.outdir and not opts.outdir.endswith(os.sep):
        opts.outdir = os.path.join(opts.outdir, '')
    return opts


def populate_fact_table(argv: List[str]) -> bool:
    opts = genargs(argv)
    if opts:
        g = load_rdf_graph(opts)
        fact_factory = load_observation_facts(g, opts)
        return fact_factory is not None and add_facts_to_table(facts, opts)


if __name__ == "__main__":
    populate_fact_table(sys.argv[1:])
