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

from th2_grpc_common.common_pb2 import Event, EventID

from config import Configuration
from th2_common.schema.factory.common_factory import CommonFactory
from th2_common.schema.message.message_router import MessageRouter
from th2_common_utils.csv_parser.adapters.adapter_factory import create_adapter
from th2_common_utils.csv_parser.event_batcher import EventBatcher
from th2_common_utils.event_utils import create_event, create_event_id

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('csv.log'),
        logging.StreamHandler()
    ]
)


def main():
    if len(sys.argv) == 1:
        logging.critical('No path to file found: pass path to CSV file as a console argument')
        return
    try:
        filename = sys.argv[1]
        root_event_id: EventID = create_event_id()
        adapter = create_adapter(filename, root_event_id, csv_version="1.0")
        root_event: Event = create_event(event_type=adapter.get_root_event_type(), event_id=root_event_id)
        cf = CommonFactory()
        event_batch_router: MessageRouter = cf.event_batch_router
        event_batcher = EventBatcher(event_batch_router, Configuration.batch_size_bytes)
    except Exception as e:
        logging.critical('Exception during initialization - %s', e)
        logging.exception(e)
        return

    event_counter = EventCounter(adapter.get_event_types())
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
    def __init__(self, event_types: dict):
        self.counting_dict = {el: 0 for el in event_types.values()}

    def count(self, event: Event):
        self.counting_dict[event.type] += 1

    def total(self):
        return sum(self.counting_dict.values())


if __name__ == '__main__':
    main()
