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

from th2_common.schema.message.message_router import MessageRouter


class EventBatcher:
    def __init__(self, batch_router: MessageRouter, batch_size: int):
        self.current_events_list = []
        self.current_events_size = 0
        self.batch_router = batch_router
        self.batch_size = batch_size

    def consume_event(self, event: dict):
        size = calculate_size_of_event(event)
        if self.current_events_size + size > self.batch_size:
            self.flush()
        self.current_events_size += size
        self.current_events_list.append(event)

    def flush(self):
        if self.current_events_size != 0:
            send_batch(self.batch_router, self.current_events_list)
            logging.debug('Sent batch of size %i bytes with %i events',
                          self.current_events_size, len(self.current_events_list))
            self.current_events_list.clear()
            self.current_events_size = 0


def send_batch(batch_router: MessageRouter, message):
    batch_router.send(message)


def calculate_size_of_event(event: dict):
    return len(event['body'])
