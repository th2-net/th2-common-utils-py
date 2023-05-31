#   Copyright 2022-2023 Exactpro (Exactpro Systems Limited)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import logging
from datetime import datetime
from enum import Enum
from typing import Iterable

from th2_common_utils.csv_parser.adapters.adapter_factory import AbstractCsvStreamAdapter
from th2_common_utils.csv_parser.csv_test_case_event import CsvTestCaseEvent, ActionEventNameRule
from th2_common_utils.csv_parser.utils import get_filename_from_path


class PredictionCsvRulesV1:
    def __init__(self):
        # rules of version 1.0
        self.root_event_name_pattern = 'Model prediction {}, {}'
        self.test_case_markers = {
            'TEST_CASE_START': self.PredictionRowType.TEST_CASE_START,
            'TEST_CASE_END': self.PredictionRowType.TEST_CASE_END,
        }
        # party_column_names -- will be handled as str to obj (dict or list)
        self.party_column_names = ['NoPartyIDs']
        self.event_types = {
            'root_event_type': 'ModelPredictionRoot',
            'test_case_event_type': 'ModelPredictionTestCase',
            'action_event_type': 'ModelPredictionTestCaseAction',
        }

    class PredictionRowType(Enum):
        TEST_CASE_START = 1
        TEST_CASE_END = 2
        HEADER = 3
        DATA = 4
        EMPTY = 5

    def get_row_type(self, row: list) -> PredictionRowType:
        if self.test_case_markers.get(row[0]) is not None:
            return self.test_case_markers.get(row[0])
        else:
            if (row[0]) == '':
                # to not check every cell in every data row
                if row[3] == '' and row[2] == '':
                    if all(elem == '' for elem in row):
                        return self.PredictionRowType.EMPTY
                return self.PredictionRowType.DATA
            else:
                return self.PredictionRowType.HEADER


PredictionRowTypeV1 = PredictionCsvRulesV1.PredictionRowType


class PredictionCsvStreamAdapter(AbstractCsvStreamAdapter):

    def get_root_event_type(self):
        return self.rules.event_types['root_event_type']

    def get_event_types(self) -> dict:
        return self.rules.event_types

    def __init__(self, path: str, csv_version='1.0'):
        self.rules = PredictionCsvRulesV1()
        root_event_name = self.rules.root_event_name_pattern.format(
            get_filename_from_path(path), datetime.now()
        )
        super().__init__(csv_version, root_event_name, path)
        self.current_csv_event = CsvTestCaseEvent(self.root_event['eventId'],
                                                  party_fields=self.rules.party_column_names)

    def handle(self, stream: Iterable) -> dict:
        logging.info("Parsing prediction CSV version {}".format(self.csv_version))
        if self.csv_version == '1.0':
            self.rules = PredictionCsvRulesV1()
            yield self.root_event
            yield from self.handler_1_0(stream)
        else:
            raise Exception('unknown csv file version')

    def handler_1_0(self, stream: Iterable):
        # One TestCaseEvent starts with TEST_CASE_START and ends with TEST_CASE_END
        # 1st line -- test case start block
        # 2nd line -- header (can be different)
        # last line -- test case end block
        # some actions start from # e.g. #sleep
        # empty lines should be skipped

        try:
            for row in stream:
                row_type = self.rules.get_row_type(row)

                if row_type == PredictionRowTypeV1.TEST_CASE_START:
                    csv_event_name = row[1]
                    self.current_csv_event = CsvTestCaseEvent(self.root_event['eventId'], csv_event_name,
                                                              party_fields=self.rules.party_column_names)
                    yield self.current_csv_event.convert_to_event(self.rules.event_types['test_case_event_type'])
                elif row_type == PredictionRowTypeV1.TEST_CASE_END:
                    pass
                elif row_type == PredictionRowTypeV1.HEADER:
                    self.current_csv_event.set_header(row)
                elif row_type == PredictionRowTypeV1.DATA:
                    yield self.current_csv_event. \
                        convert_row_to_event(row,
                                             self.rules.event_types['action_event_type'],
                                             ActionEventNameRule("{}, {}", ['MessageType', 'Action']))
                elif row_type == PredictionRowTypeV1.EMPTY:
                    continue
        except Exception as e:
            logging.critical('Error while handling row:')
            logging.exception(e)
            raise e
