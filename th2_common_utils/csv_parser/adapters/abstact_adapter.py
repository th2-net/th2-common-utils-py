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
from abc import abstractmethod

from th2_data_services.data_source.lwdp.stub_builder import http_event_stub_builder
from th2_data_services.interfaces import IStreamAdapter

from th2_common_utils import create_event_id


class AbstractCsvStreamAdapter(IStreamAdapter):

    def __init__(self, csv_version: str, root_event_name: str, path: str):
        # root_event - root event of all events that will be produced
        self.root_event = http_event_stub_builder.build({
            'eventName': root_event_name,
            'eventType': self.get_root_event_type(),
            'eventId': create_event_id().id,
            'parentEventId': None,
            'body': {'sourceFile': path},
            'batchId': None
        })
        self.csv_version = csv_version

    @abstractmethod
    def get_event_types(self):
        pass

    @abstractmethod
    def get_root_event_type(self):
        pass
