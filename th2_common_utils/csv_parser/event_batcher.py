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

from test_case import TestCase
from params import Parameters
from th2_common_utils.event_utils import create_event
from th2_grpc_common.common_pb2 import Event
from th2_common.schema.message.message_router import MessageRouter


class EventBatcher:
    def __init__(self, batch_router: MessageRouter):
        self.current_events_list = []
        self.current_events_size = 0
        self.batch_router = batch_router

    def consume_test_case(self, test_case: TestCase):
        json_str = test_case.convert_to_json()
        event = create_event_from_json(json_str)
        size = calculate_size_of_event(event)
        if self.current_events_size + size > Parameters.batch_size_bytes:
            self.send_current_events()
        self.current_events_size += size
        self.current_events_list.append(event)

    def _add_test_case(self, json, size):
        self.current_events_size += size
        self.current_events_list.append(json)

    def send_current_events(self):
        logging.debug("Sent batch of size %i bytes with %i events",
                      self.current_events_size, len(self.current_events_list))
        send_batch(self.batch_router, self.current_events_list)
        self.current_events_list.clear()
        self.current_events_size = 0


def send_batch(batch_router: MessageRouter, message):
    batch_router.send(message)


def create_event_from_json(json_str) -> Event:
    return create_event(body=json_str)


def calculate_size_of_string(s: str):
    return len(s.encode('utf-8'))


def calculate_size_of_event(event: Event):
    return len(event.body)
