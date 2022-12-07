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
import orjson
from th2_grpc_common.common_pb2 import Event, EventID, EventStatus, MessageID, EventBatch


def create_event_body(component: Any, sort: bool = False) -> bytes:
    """Creates event body (component) as bytes.

    Args:
        component: Event body to be converted into bytes.
        sort: Set True if you need your object properties to be sorted.

    Returns:
        Event body as bytes.
    """

    if sort:
        return orjson.dumps(component,
                            default=lambda o: o.__dict__,
                            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SORT_KEYS)
    else:
        return orjson.dumps(component,
                            default=lambda o: o.__dict__,
                            option=orjson.OPT_NON_STR_KEYS)


common_id = str(uuid.uuid1())
counter = 0


def create_event_id(book_name: str,
                    scope: str,
                    start_timestamp: Optional[Timestamp] = None) -> EventID:
    """Creates event id as EventID class instance.

    Args:
        book_name: Name of the book.
        scope: Scope name. Scope is a thing like a stream but for events.
        start_timestamp: Start timestamp.

    Returns:
        EventID class instance with 'id' attribute.
    """
    global counter
    counter += 1
    return EventID(id=f'{common_id}_{counter}',
                   book_name=book_name,
                   scope=scope,
                   start_timestamp=start_timestamp or create_timestamp()
                   )


def create_timestamp() -> Timestamp:
    timestamp = Timestamp()
    timestamp.GetCurrentTime()

    return timestamp


def create_event(event_id: Optional[EventID] = None,
                 parent_id: Optional[EventID] = None,
                 end_timestamp: Optional[Timestamp] = None,
                 status: Union[str, int] = EventStatus.SUCCESS,
                 name: str = 'Event',
                 event_type: str = '',
                 body: bytes = b'',
                 attached_message_ids: Optional[List[MessageID]] = None) -> Event:
    """Creates event as Event class instance.

    Args:
        event_id: ID of the event.
        parent_id: Parent ID of the event.
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
        end_timestamp=end_timestamp or create_timestamp(),
        status=status,  # type: ignore
        name=name,
        type=event_type,
        body=body,
        attached_message_ids=attached_message_ids)


def create_event_batch(parent_id: Optional[EventID] = None) -> EventBatch:
    """Creates event batch.

    Args:
        parent_id: parent event ID

    Returns:
        EventBatch object.
    """

    event_batch = EventBatch()
    # TODO - add EventBatchMetadata  # noqa: T101
    if parent_id:
        event_batch.parent_event_id.CopyFrom(parent_id)

    return event_batch
