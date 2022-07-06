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

from functools import lru_cache, singledispatch
from typing import Any, Optional, Union

from th2_grpc_common.common_pb2 import ConnectionID, EventID, ListValue, Message, MessageID, MessageMetadata, Value


def dict_to_message(fields: dict,
                    parent_event_id: Optional[EventID] = None,
                    session_alias: str = '',
                    message_type: str = '') -> Message:
    """Converts a dict to th2-message with 'metadata' and 'parent_event_id'.

    Args:
        fields: Message fields as a dict.
        parent_event_id: Parent event id.
        session_alias: Session alias (is used when creating message metadata).
        message_type: Message type (is used when creating message metadata).

    Returns:
        th2-message with 'metadata' and 'parent_event_id'. All 'fields' nested entities will be converted.

        Conversion rules:
            str, int, float, Value - Value.simple_value
            list, ListValue - Value.list_value
            dict, Message - Value.message_value.

    Raises:
        TypeError: Occurs when 'message.fields' contains a field of the unsupported type.
    """

    if parent_event_id is None:
        parent_event_id = EventID()

    return Message(parent_event_id=parent_event_id,
                   metadata=MessageMetadata(id=MessageID(connection_id=ConnectionID(session_alias=session_alias)),
                                            message_type=message_type),
                   fields={field: _dict_to_message_convert_value(field_value) for field, field_value in fields.items()})


@singledispatch
def _dict_to_message_convert_value(entity: Any) -> Value:
    raise TypeError('Cannot convert %s object.' % type(entity))


@_dict_to_message_convert_value.register(Value)
def _(value: Value) -> Value:
    return value


@_dict_to_message_convert_value.register(Message)
def _(message: Message) -> Value:
    return Value(message_value=message)


@_dict_to_message_convert_value.register(ListValue)
def _(list_value: ListValue) -> Value:
    return Value(list_value=list_value)


@_dict_to_message_convert_value.register(dict)
def _(dict_obj: dict) -> Value:
    return Value(message_value=Message(fields={k: _dict_to_message_convert_value(v) for k, v in dict_obj.items()}))


@_dict_to_message_convert_value.register(list)
def _(list_obj: list) -> Value:
    return Value(list_value=ListValue(values=list(map(_dict_to_message_convert_value, list_obj))))


@lru_cache(maxsize=128)
@_dict_to_message_convert_value.register(str)
@_dict_to_message_convert_value.register(int)
@_dict_to_message_convert_value.register(float)
def _(simple_obj: Union[str, int, float]) -> Value:
    return Value(simple_value=str(simple_obj))
