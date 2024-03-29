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

from typing import Any, List, Optional, Union
import uuid

from google.protobuf.timestamp_pb2 import Timestamp
from th2_grpc_common.common_pb2 import Event, EventID, EventStatus, MessageID

from th2_common_utils.event_components import MessageComponent, TreeTableComponent


common_id = str(uuid.uuid1())
counter = 0


def create_event_id(**kwargs) -> EventID:
    """Creates event id as EventID class instance.

    Returns:
        EventID class instance with 'id' attribute.
    """
    global counter
    counter += 1
    return EventID(id=f'{common_id}_{counter}')


def create_timestamp() -> Timestamp:
    timestamp = Timestamp()
    timestamp.GetCurrentTime()

    return timestamp


def create_event(event_id: Optional[EventID] = None,
                 parent_id: Optional[EventID] = None,
                 start_timestamp: Optional[Timestamp] = None,
                 end_timestamp: Optional[Timestamp] = None,
                 status: Union[str, int] = EventStatus.SUCCESS,
                 name: str = 'Event',
                 event_type: str = '',
                 body: Any = None,
                 attached_message_ids: Optional[List[MessageID]] = None) -> Event:
    """Creates event as Event class instance.

    Args:
        event_id: ID of the event.
        parent_id: Parent ID of the event.
        start_timestamp: Start timestamp.
        end_timestamp: End timestamp.
        status: Event status ('SUCCESS' or 'FAILED').
        name: Event name.
        event_type: Event type.
        body: Event body as bytes. TreeTable class instance as bytes can be passed.
        attached_message_ids: Attached message IDs.

    Returns:
        Event class instance with attributes.
    """

    return Event(
        id=event_id or create_event_id(),
        parent_id=parent_id,
        start_timestamp=start_timestamp or create_timestamp(),
        end_timestamp=end_timestamp or create_timestamp(),
        status=status,  # type: ignore
        name=name,
        type=event_type,
        body=bytes(body
                   if isinstance(body, (MessageComponent, TreeTableComponent, bytes))
                   else MessageComponent(body)) if body is not None else b'',
        attached_message_ids=attached_message_ids)
