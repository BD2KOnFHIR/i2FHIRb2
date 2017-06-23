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
from argparse import ArgumentParser


def genargs() -> ArgumentParser:
    """
    Create a command line parser
    :return: parser
    """
    parser = ArgumentParser(description="i2b2/FHIR concept_dimension manager")
    parser.add_argument("indir", help="Input directory or URI of w5.ttl and fhir.ttl files")
    parser.add_argument("outdir", help="Output directory to store .tsv files")
    parser.add_argument("-r", "--resource",
                        help="Name of specific resource to emit (e.g. Observation) - default is all")
    parser.add_argument("-s", "--sourcesystem",
                        default=Default_Sourcesystem_Code,
                        help="sourcesystem code. Default: 'F{}'".format(Default_Sourcesystem_Code))
    parser.add_argument("-b", "--base",
                        default=Default_Path_Base,
                        help="Concept dimension and ontology base path. Default:{}".format(Default_Path_Base))
    return parser


def generate_i2b2(argv) -> bool:
    opts = genargs().parse_args(argv)
    opts.updatedate = datetime.now()
    if not opts.indir.endswith(os.sep):
        opts.indir = os.path.join(opts.indir, '')
    if not opts.outdir.endswith(os.sep):
        opts.outdir = os.path.join(opts.outdir, '')
    g = load_fhir_ontology(opts)
    return g is not None and generate_i2b2_files(g, opts)