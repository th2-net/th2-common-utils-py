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
import sys
from pathlib import Path
from typing import Iterable

from th2_common.schema.factory.common_factory import CommonFactory
from th2_common.schema.message.message_router import MessageRouter

from th2_common_utils.csv_parser.config import Configuration
from th2_common_utils.csv_parser.event_batcher import EventBatcher
from th2_common_utils.csv_parser.csv_stream import stream_events_from_csv

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('csv.log'),
        logging.StreamHandler()
    ]
)


def batch_and_send(stream: Iterable[dict], config_path: str = None):
    if config_path is None:
        cf = CommonFactory()
    else:
        cf = CommonFactory(config_path=Path(config_path))
    event_batch_router: MessageRouter = cf.event_batch_router
    event_batcher = EventBatcher(event_batch_router, Configuration.batch_size_bytes)

    for event in stream:
        event_batcher.consume_event(event)
    event_batcher.flush()


def parse_and_send_events_from_matrix_csv():
    try:
        if len(sys.argv) == 1:
            logging.critical('No path to file found: pass path to CSV file as a console argument')
            raise ValueError('No path to file found: pass path to CSV file as a console argument')

        filename = sys.argv[1]
        if len(sys.argv) == 2:
            logging.info('Using default config path')
            config_path = None
        else:
            config_path = sys.argv[2]
        batch_and_send(config_path=config_path, stream=stream_events_from_csv(filename))
    except Exception:
        logging.critical('Exception with console args:', sys.argv)


# step 3
if __name__ == '__main__':
    parse_and_send_events_from_matrix_csv()
