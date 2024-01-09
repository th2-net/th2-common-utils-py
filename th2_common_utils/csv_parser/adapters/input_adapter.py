import logging
from datetime import datetime
from enum import Enum
from typing import Iterable

from th2_common_utils.csv_parser.adapters.abstact_adapter import AbstractCsvStreamAdapter
from th2_common_utils.csv_parser.csv_test_case_event import CsvTestCaseEvent
from th2_common_utils.csv_parser.utils import get_filename_from_path


class InputCsvRulesV1:
    def __init__(self):
        self.root_event_name_pattern = 'Model input {}, {}'
        self.test_case_markers = {
            'TEST_CASE_START': self.InputRowType.TEST_CASE_START,
            'TEST_CASE_END': self.InputRowType.TEST_CASE_END,
        }
        self.event_types = {
            'root_event_type': 'ModelInputRoot',
            'test_case_event_type': 'ModelInputTestCase',
            'action_event_type': 'ModelInputTestCaseAction',
        }
        self.party_column_names = ['OrderID']
        self.additional_reading_flag = False
        # whether a header was read for this case
        self.header_is_read_flag = False
        self.inside_test_case_now_flag = False

    class InputRowType(Enum):
        TEST_CASE_START = 1
        TEST_CASE_END = 2
        HEADER = 3
        DATA = 4
        EMPTY = 5
        TEST_CASE_START_ADDITIONAL_DATA = 6

    def get_row_type(self, row: list) -> InputRowType:
        type_from_dict = self.test_case_markers.get(row[0])
        if type_from_dict is not None:
            # either a TEST_CASE_START or TEST_CASE_START
            if type_from_dict == self.InputRowType.TEST_CASE_START:
                self.inside_test_case_now_flag = True
                self.additional_reading_flag = True
            if type_from_dict == self.InputRowType.TEST_CASE_END:
                self.inside_test_case_now_flag = False
                self.header_is_read_flag = False
            return type_from_dict
        else:
            if self._is_row_empty_(row):
                self.additional_reading_flag = False
                return self.InputRowType.EMPTY
            if self.additional_reading_flag:
                return self.InputRowType.TEST_CASE_START_ADDITIONAL_DATA
            if not self.header_is_read_flag and self.inside_test_case_now_flag:
                self.header_is_read_flag = True
                return self.InputRowType.HEADER
            return self.InputRowType.DATA

    def _is_row_empty_(self, row: list) -> bool:
        if (row[0]) == '':
            # to not check every cell in every data row
            if row[4] == '' and row[2] == '':
                if all(elem == '' for elem in row):
                    return True
        return False


class InputCsvStreamAdapter(AbstractCsvStreamAdapter):

    def __init__(self, path: str, csv_version='1.0'):
        self.rules = InputCsvRulesV1()
        root_event_name = self.rules.root_event_name_pattern.format(
            get_filename_from_path(path), datetime.now()
        )
        super().__init__(csv_version, root_event_name, path)
        self.current_csv_event = CsvTestCaseEvent(self.root_event['eventId'], party_fields=self.rules.party_column_names)

    def get_event_types(self):
        return self.rules.event_types

    def get_root_event_type(self):
        return self.rules.event_types['root_event_type']

    def handle(self, stream: Iterable) -> dict:
        logging.info("Parsing input CSV version {}".format(self.csv_version))
        if self.csv_version == '1.0':
            yield self.root_event
            yield from self.handler_1_0(stream)
        else:
            raise Exception('unknown csv file version')

    def handler_1_0(self, stream: Iterable):
        try:
            row_counter = 0
            for row in stream:
                row_counter += 1
                if row_counter == 100:
                    break
                row_type = self.rules.get_row_type(row)
                print(row_type, row)
        except Exception as e:
            logging.critical('Error while handling row:')
            logging.exception(e)
            raise e
