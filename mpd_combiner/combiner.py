# Copyright (C) 2020 Kenneth Solbø Andersen

# This file is part of MPD-combiner.
#
# MPD-combiner is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MPD-combiner is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import logging
import xml.etree.ElementTree as ElementTree
from pathlib import Path


class Combiner:
    def __init__(self, args):
        self._args = args
        self._input_filenames = []
        self._output_filename = ''
        self._output_tree = None
        self._period = None
        namespace = 'urn:mpeg:dash:schema:mpd:2011'
        ElementTree.register_namespace('', namespace)
        self._namespaces = {'': namespace}

    def combine_files(self):
        self.parse_arguments()
        self.create_output_tree()
        self.add_adaptation_sets_from_remaining_input_files()
        self.write_to_output_file()

    def add_adaptation_sets_from_remaining_input_files(self):
        logging.debug('Looping through remaining files to find their adaptation sets.')
        for filename in self._input_filenames:
            logging.debug(f'Parsing file: "{filename}"')
            tree = ElementTree.parse(filename)
            root = tree.getroot()
            adaptation_sets = root.findall('./Period/AdaptationSet', namespaces=self._namespaces)
            logging.debug(f'Found {len(adaptation_sets)} adaptation sets to add.')
            self._period.extend(adaptation_sets)

    def write_to_output_file(self):
        self._output_tree.write(open(self._output_filename, 'wb'), xml_declaration=True, encoding='utf-8', method='xml')

    def create_output_tree(self):
        first_file = self._input_filenames.pop()
        self._output_tree = ElementTree.parse(first_file)
        self._period = self._output_tree.getroot().find('./Period', namespaces=self._namespaces)

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Combine adaptation sets from several MPD files into one.')
        parser.add_argument('-d', '--debug', required=False, action='store_true')
        parser.add_argument('-o', '--output', required=True,
                            help='Output file name. Extension (.mpd) will be added if not set.')
        parser.add_argument('input_files', metavar='<input file>', nargs='+')
        parsed_args = parser.parse_args(self._args)

        input_filenames = []
        for filename in parsed_args.input_files:
            filenames = Path('.').glob(filename)
            input_filenames.extend(filenames)

        output_filename = parsed_args.output
        if not output_filename.endswith('.mpd'):
            output_filename += '.mpd'

        if parsed_args.debug:
            logging.basicConfig(level=logging.DEBUG)

        logging.debug(f'Input files: "{", ".join([str(input_file) for input_file in input_filenames])}"')
        logging.debug(f'Output file: "{str(output_filename)}"')

        self._input_filenames = input_filenames
        self._output_filename = output_filename
