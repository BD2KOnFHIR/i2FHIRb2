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
from argparse import ArgumentParser, Namespace
from datetime import datetime

import sys
from typing import List

from i2fhirb2.generate_i2b2 import Default_Sourcesystem_Code, Default_Path_Base
from i2fhirb2.i2b2model.i2b2observationfact import ObservationFactKey
from i2fhirb2.fhir.fhirobservationfact import FHIRObservationFact, FHIRObservationFactFactory
from i2fhirb2.sqlsupport.i2b2_tables import I2B2Tables
from i2fhirb2.i2b2model.tablenames import i2b2table

ofk = ObservationFactKey(1000000133, 471882, 'LCS-I2B2:D000109100', datetime(2017, 5, 23, 11, 17))
# FHIRObservationFact.update_date = datetime(2017, 2, 19, 12, 33)
# FHIRObservationFact.sourcesystem_cd = "FHIR STU3"
# oflist = FHIRObservationFactFactory(self.g, ofk, None)

def load_observation_facts(opts: Namespace) -> List[FHIRObservationFact]:
    ofk = ObservationFactKey(opts.patnum, opts.encounter, opts.provider, datetime.now())
    FHIRObservationFact.sourcesystem_cd = opts.sourcesystem
    return FHIRObservationFactFactory(g, ofk, None)

def genargs() -> ArgumentParser:
    """
    Create a command line parser
    :return: parser
    """
    parser = ArgumentParser(description="Load FHIR data into i2b2 observation fact table")
    parser.add_argument("-f", "--file", help="URL or name of input .ttl file")
    parser.add_argument("-d", "--dir", help="URI of server or directory of input files")
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


def generate_i2b2(argv) -> bool:
    opts = genargs().parse_args(argv)
    if not (opts.file or opts.dir):
        print("Either an input file or input directory must be supplied", file=sys.stderr)
        return False
    if not(opts.outdir or opts.load):
        print("Either an output directory or '-l' option must be specified", file=sys.stderr)
        return False

    opts.updatedate = datetime.now()
    if not opts.indir.endswith(os.sep):
        opts.indir = os.path.join(opts.indir, '')
    if opts.outdir and not opts.outdir.endswith(os.sep):
        opts.outdir = os.path.join(opts.outdir, '')
    opts.tables = I2B2Tables() if opts.load else None
    g = load_observation_facts(opts)
    return g is not None and generate_i2b2_tables(g, opts)

