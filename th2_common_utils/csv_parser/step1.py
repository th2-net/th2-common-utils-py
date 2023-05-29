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

import csv
import logging
import sys
from enum import Enum
from typing import Iterable

from th2_data_services.interfaces import IStreamAdapter
from th2_grpc_common.common_pb2 import Event

from config import Configuration
from th2_common.schema.factory.common_factory import CommonFactory
from th2_common.schema.message.message_router import MessageRouter
from th2_common_utils.csv_parser.csv_test_case_event import CsvTestCaseEvent
from th2_common_utils.csv_parser.event_batcher import EventBatcher
from th2_common_utils.event_utils import create_event

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('csv.log'),
        logging.StreamHandler()
    ]
)


class PredictionCsvRulesV1:
    def __init__(self):
        # rules of version 1.0
        self.test_case_markers = {
            'TEST_CASE_START': self.PredictionRowType.TEST_CASE_START,
            'TEST_CASE_END': self.PredictionRowType.TEST_CASE_END,
        }
        # party_column_names -- will be handled as str to obj (dict or list)
        self.party_column_names = ['NoPartyIDs']

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


class PredictionCsvStreamAdapter(IStreamAdapter):

    def __init__(self, root_event_id, csv_version='1.0'):
        self.rules = PredictionCsvRulesV1()
        self.current_csv_event = CsvTestCaseEvent(root_event_id, party_fields=self.rules.party_column_names)
        self.csv_version = csv_version
        # root_event_id - root event id of all events that will be produced
        self.root_event_id = root_event_id

    def handle(self, stream: Iterable) -> dict:
        logging.info("Parsing CSV version {}".format(self.csv_version))
        if self.csv_version == '1.0':
            self.rules = PredictionCsvRulesV1()
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
                    self.current_csv_event = CsvTestCaseEvent(self.root_event_id, csv_event_name,
                                                              party_fields=self.rules.party_column_names)
                    yield self.current_csv_event.convert_to_event()
                elif row_type == PredictionRowTypeV1.TEST_CASE_END:
                    pass
                elif row_type == PredictionRowTypeV1.HEADER:
                    self.current_csv_event.set_header(row)
                elif row_type == PredictionRowTypeV1.DATA:
                    yield self.current_csv_event.convert_row_to_event(row)
                elif row_type == PredictionRowTypeV1.EMPTY:
                    continue
        except Exception as e:
            logging.critical('Error while handling row:')
            logging.exception(e)
            raise e


def main():
    if len(sys.argv) == 1:
        logging.critical('No path to file found: pass path to CSV file as a console argument')
        return
    try:
        filename = sys.argv[1]
        root_event = create_event(event_type=Configuration.root_event_type)
        adapter = PredictionCsvStreamAdapter(root_event.id)
        cf = CommonFactory()
        event_batch_router: MessageRouter = cf.event_batch_router
        event_batcher = EventBatcher(event_batch_router, Configuration.batch_size_bytes)
    except Exception as e:
        logging.critical('Exception during initialization - %s', e)
        logging.exception(e)
        return

    event_counter = EventCounter(Configuration.action_event_type, Configuration.test_case_event_type,
                                 Configuration.root_event_type)
    try:
        event_batcher.consume_event(root_event)
        event_counter.count(root_event)
        with open(filename, mode='r') as csv_file:
            logging.info('Parsing %s', filename)
            csv_reader = csv.reader(csv_file, delimiter=',')
            data = adapter.handle(csv_reader)

            event: Event
            for event in data:
                event_batcher.consume_event(event)
                event_counter.count(event)
        event_batcher.flush()
    except Exception as e:
        logging.critical('Exception during parsing file %s', filename, e)
        logging.exception(e)
    finally:
        print(event_counter.counting_dict)
        logging.info('Parsing finished with total %i events', event_counter.total())
        for event_type, value in event_counter.counting_dict.items():
            logging.info('Event type %s - parsed %i events', event_type, value)


class EventCounter:
    def __init__(self, *args):
        self.counting_dict = {el: 0 for el in args}

    def count(self, event: Event):
        self.counting_dict[event.type] += 1

    def total(self):
        return sum(self.counting_dict.values())


if __name__ == '__main__':
    main()
