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

from th2_data_services.data import Data
from th2_data_services.event_tree import EventTreeCollection

from th2_common_utils.csv_parser.adapters.prediction_adapter import PredictionCsvStreamAdapter

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('csv.log'),
        logging.StreamHandler()
    ]
)


def stream_events_from_csv(filename: str):
    adapter = PredictionCsvStreamAdapter(filename, csv_version='1.0')
    event_counter = EventCounter(adapter.get_event_types())

    try:
        for event in Data.from_csv(filename).map_stream(adapter):
            event_counter.count(event)
            yield event
    except FileNotFoundError:
        logging.critical('File %s not found', filename)
    except Exception as e:
        logging.critical('Exception during parsing file %s', filename, e)
    finally:
        logging.info('Parsing finished with total %i events', event_counter.total())
        for event_type, value in event_counter.counting_dict.items():
            logging.info('Event type %s - parsed %i events', event_type, value)


class EventCounter:
    def __init__(self, event_types: dict):
        self.counting_dict = {el: 0 for el in event_types.values()}

    def count(self, event: dict):
        self.counting_dict[event['eventType']] += 1

    def total(self):
        return sum(self.counting_dict.values())


# step 1
if __name__ == '__main__':
    from th2_data_services.data_source.lwdp.event_tree.http_etc_driver import HttpETCDriver

    if len(sys.argv) == 1:
        logging.critical('No path to file found: pass path to CSV file as a console argument')
        raise ValueError('No path to file found: pass path to CSV file as a console argument')

    filename = sys.argv[1]
    data = stream_events_from_csv(filename)
    print(data)
    # data.to_json('my_test.jsons')

    etc = EventTreeCollection(HttpETCDriver())
    etc.build(data)
    etc.show()