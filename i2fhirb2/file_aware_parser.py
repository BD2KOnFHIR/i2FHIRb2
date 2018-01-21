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
import argparse
import shlex
from typing import List

import os


class FileAwareParser(argparse.ArgumentParser):
    """ Argument parser that tracks which arguments are file names for relative file relocation. """
    def __init__(self, use_defaults: bool=True, *args, **kwargs) -> None:
        """ Constructor

        :param use_defaults: If False, omit defaults values.  Used for parsing configuration files
        :param args: ArgumentParser args -- passed on
        :param kwargs: ArgumentParser args -- passed on
        """
        self.use_defaults = use_defaults
        super().__init__(*args, **kwargs)
        self.file_args = []

    def add_file_argument(self, *args, **kwargs):
        """ Add an argument that represents the location of a file

        :param args:
        :param kwargs:
        :return:
        """
        rval = self.add_argument(*args, **kwargs)
        self.file_args.append(rval)
        return rval

    def add_argument(self, *args, **kwargs):
        """ Add an argument incorporating the default value into the help string

        :param args:
        :param kwargs:
        :return:
        """
        defhelp = kwargs.pop("help", None)
        defaults = kwargs.pop("default", None)
        default = defaults if self.use_defaults else None
        if not defhelp or default is None or kwargs.get('action') == 'help':
            return super().add_argument(*args, help=defhelp, default=default, **kwargs)
        else:
            return super().add_argument(*args, help=defhelp + " (default: {})".format(default),
                                        default=default, **kwargs)

    def decode_file_args(self, argv: List[str]) -> List[str]:
        """
        Preprocess a configuration file.  The location of the configuration file is stored in the parser so that the
        FileOrURI action can add relative locations.
        :param argv: raw options list
        :return: options list with '--conf' references replaced with file contents
        """
        for i in range(0, len(argv) - 1):
            # TODO: take prefix into account
            if argv[i] == '--conf':
                del argv[i]
                conf_file = argv[i]
                del (argv[i])
                with open(conf_file) as config_file:
                    conf_args = shlex.split(config_file.read())
                    # We take advantage of a poential bug in the parser where you can say "foo -u 1 -u 2" and get
                    # 2 as a result
                    argv = self.fix_rel_paths(conf_args, conf_file) + argv
                return self.decode_file_args(argv)
        return argv

    def fix_rel_paths(self, conf_args: List[str], conf_file: str) -> List[str]:
        base_path = os.path.abspath(os.path.split(conf_file)[0])
        rval = []
        is_file_arg = False
        for conf_arg in conf_args:
            if any(conf_arg.startswith(prefix) for prefix in self.prefix_chars):
                rval.append(conf_arg)
                is_file_arg = any(conf_arg in file_action.option_strings for file_action in self.file_args)
                # TODO: recursive config files
            elif is_file_arg and ('://' not in conf_arg and not os.path.isabs(conf_arg)):
                rval.append(os.path.abspath(os.path.join(base_path, conf_arg)))
            else:
                rval.append(conf_arg)
        return rval
