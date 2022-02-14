#   Copyright 2022-2022 Exactpro (Exactpro Systems Limited)
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

import uuid

from google.protobuf.timestamp_pb2 import Timestamp
from th2_grpc_common.common_pb2 import EventID, EventStatus, MessageID, Event

from th2_common_utils.util.common import ComponentEncoder


class EventUtils:
    """This class contains methods for th2-events creating."""

    @staticmethod
    def create_event_body(component) -> bytes:
        """Creates event body (component) as bytes."""

        return EventUtils.component_encoder().encode(component).encode()

    @staticmethod
    def component_encoder() -> ComponentEncoder:
        return ComponentEncoder()

    @staticmethod
    def create_event_id() -> EventID:
        """Creates event id as EventID class instance."""

        return EventID(id=str(uuid.uuid1()))

    @staticmethod
    def create_timestamp():
        timestamp = Timestamp()
        timestamp.GetCurrentTime()
        return timestamp

    @staticmethod
    def create_event(id: EventID = None,
                     parent_id: EventID = None,
                     start_timestamp: Timestamp = None,
                     end_timestamp: Timestamp = None,
                     status: EventStatus = 'SUCCESS',
                     name: str = 'Event',
                     type: str = None,
                     body: bytes = b'',
                     attached_message_ids: [MessageID] = None) -> Event:
        """Creates event as Event class instance."""

        return Event(
            id=id or EventUtils.create_event_id(),
            parent_id=parent_id,
            start_timestamp=start_timestamp or EventUtils.create_timestamp(),
            end_timestamp=end_timestamp or EventUtils.create_timestamp(),
            status=status,
            name=name,
            type=type,
            body=body,
            attached_message_ids=attached_message_ids)
