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

import os
from typing import Optional, List

from tests.utils.crc_testcase import CRCTestCase

from i2fhirb2.loaders.i2b2graphmap import I2B2GraphMap
from i2fhirb2.loadfacts import load_facts, load_graph_map, genargs
from tests.utils.fhir_graph import test_conf_directory, test_data_directory


class LoadFactsHelper(CRCTestCase):
    caller_filename = None

    @classmethod
    def setUpClass(cls):
        cls.conf = os.path.abspath(os.path.join(test_conf_directory, 'db_conf'))
        cls.mv = os.path.abspath(os.path.join(test_data_directory, 'fhir_metadata_vocabulary'))
        cls.dirname, test_file = os.path.split(os.path.abspath(cls.caller_filename))

    def _setup_opts_string(self, resource_name: str, resource_path: Optional[str]) -> List[str]:
        if resource_path is None:
            resource_path = os.path.join(self.dirname, 'data')
        if ":" in resource_path:
            input_file = resource_path + ('' if resource_path.endswith(('#', '/')) else '/') + resource_name
        else:
            input_file = os.path.abspath(os.path.join(resource_path, resource_name))
        fmt = 'json' if resource_name.endswith('.json') else 'rdf'
        return f"--sourcesystem {self._sourcesystem_cd} -u {self._upload_id} -mv {self.mv} " \
               f"--conf {self.conf} -i {input_file} -t {fmt} -l".split()

    def load_named_resource(self, resource_name: str, resource_path: Optional[str] = None) -> None:
        """ Load resource_name from resource path and save it into the i2b2 facts table

        :param resource_name: name of resource
        :param resource_path: Directory or URI. If none, self.dirname will be used
        """
        with self.sourcesystem_cd():
            load_facts(self._setup_opts_string(resource_name, resource_path))

    def load_i2b2_to_memory(self, resource_name: str, resource_path: Optional[str] = None) -> Optional[I2B2GraphMap]:
        """ Load resource_name from resource path

        :param resource_name: name of resource
        :param resource_path: Directory or URI. If none, self.dirname will be used
        :return: in-memory representation of resource
        """
        with self.sourcesystem_cd():
            return load_graph_map(genargs(self._setup_opts_string(resource_name, resource_path)))
