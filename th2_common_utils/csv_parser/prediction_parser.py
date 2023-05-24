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

from config import Configuration
from event_batcher import EventBatcher
from row_handler import create_row_handler, RowHandler
from th2_common.schema.factory.common_factory import CommonFactory
from th2_common.schema.message.message_router import MessageRouter

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('csv.log'),
        logging.StreamHandler()
    ]
)


def main():
    line_count = 0
    if len(sys.argv) == 1:
        logging.critical("Pass path to csv file as a console argument")
        return
    filename = sys.argv[1]
    try:
        cf = CommonFactory()
        event_batch_router: MessageRouter = cf.event_batch_router

        event_batcher = EventBatcher(event_batch_router, Configuration.batch_size_bytes)
        rh: RowHandler = create_row_handler(event_batcher)
    except Exception as e:
        logging.critical('Exception during initialization - %s', e)
        logging.exception(e)
        return

    try:
        with open(filename, mode='r') as csv_file:
            logging.info('Parsing %s', filename)

            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                rh.handle_row(line_count, row)
                line_count += 1

            logging.info('Parsed %i lines in file %s', line_count, filename)
    except Exception as e:
        logging.critical('Exception at line %i (zero-based) of file %s - %s', line_count, filename, e)
        logging.exception(e)


if __name__ == '__main__':
    main()
