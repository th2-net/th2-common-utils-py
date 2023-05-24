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
from enum import Enum

from event_batcher import EventBatcher
from test_case import TestCase


class RowHandler:
    def handle_row(self, index, row: list):
        pass


class PredictionRowType(Enum):
    TEST_CASE_START = 1
    TEST_CASE_END = 2
    HEADER = 3
    DATA = 4


class PredictionRowHandler(RowHandler):
    class Parameters:
        def __init__(self):
            self.json_fields = ['NoPartyIDs']
            self.test_case_markers = {
                'TEST_CASE_START': PredictionRowType.TEST_CASE_START,
                'TEST_CASE_END': PredictionRowType.TEST_CASE_END,
            }

    def __init__(self, event_batcher: EventBatcher):
        self.event_batcher = event_batcher
        self.current_test_case = None
        self.parameters = self.Parameters()

    def handle_row(self, index, row: list):
        if index == 0:
            self._handle_first_prediction_row(row)
        else:
            self._handle_prediction_row(row)

    def _handle_first_prediction_row(self, row: list):
        row_type = self._get_row_type(row)
        if row_type != PredictionRowType.HEADER:
            self._handle_prediction_row(row)
        self.current_test_case = TestCase(json_fields=self.parameters.json_fields)
        self.current_test_case.set_header(row)
        self.current_test_case.append_row(row)
        self.event_batcher.consume_test_case(self.current_test_case)

    def _handle_prediction_row(self, row: list):
        try:
            row_type = self._get_row_type(row)

            if row_type == PredictionRowType.TEST_CASE_START:
                test_case_name = row[1]
                self.current_test_case = TestCase(test_case_name, json_fields=self.parameters.json_fields)
                self.current_test_case.append_row(row)
            elif row_type == PredictionRowType.TEST_CASE_END:
                self.event_batcher.consume_test_case(self.current_test_case)
            elif row_type == PredictionRowType.HEADER:
                self.current_test_case.set_header(row)
            elif row_type == PredictionRowType.DATA:
                self.current_test_case.append_row(row)
        except Exception as e:
            logging.critical('Error while handling row:')
            logging.exception(e)
            raise e

    def _get_row_type(self, row: list) -> PredictionRowType:
        if self.parameters.test_case_markers.get(row[0]) is not None:
            return self.parameters.test_case_markers.get(row[0])
        else:
            if (row[0]) == '':
                return PredictionRowType.DATA
            else:
                return PredictionRowType.HEADER


def create_row_handler(event_batcher) -> RowHandler:
    # add more types of csv files here
    return PredictionRowHandler(event_batcher)
