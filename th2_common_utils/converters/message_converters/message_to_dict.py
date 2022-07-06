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
from typing import Any, Dict, Optional, Union

from google.protobuf.json_format import MessageToDict
from th2_grpc_common.common_pb2 import ListValue, Message, Value

DictMessageType = Union[str, list, dict]


def message_to_dict(message: Message) -> Dict[str, Optional[DictMessageType]]:
    """Converts th2-message to a dict.

    Args:
        message: th2-message.

    Returns:
        th2-message as a dict. All nested entities will be also converted.

        Conversion rules:
            Value.simple_value - str
            Value.list_value - list
            Value.message_value - dict

    Raises:
        TypeError: Occurs when 'message.fields' contains a field not of the 'Value' type.
    """

    return {
        'parent_event_id': message.parent_event_id.id,
        'metadata': MessageToDict(message.metadata),
        'fields': {
            field: _message_to_dict_convert_value(__get_inner_value(field_value))
            for field, field_value in message.fields.items()
        }
    }


@singledispatch
def _message_to_dict_convert_value(entity: Any) -> Optional[DictMessageType]:
    raise TypeError('Expected simple_value, list_value or message_value. %s object received: %s'
                    % (type(entity), entity))


@_message_to_dict_convert_value.register(Message)
def _(message: Message) -> dict:
    return {
        field: _message_to_dict_convert_value(__get_inner_value(field_value))
        for field, field_value in message.fields.items()
    }


@_message_to_dict_convert_value.register(ListValue)
def _(list_value: ListValue) -> list:
    values = map(__get_inner_value, list_value.values)
    return list(map(_message_to_dict_convert_value, values))


@lru_cache(maxsize=128)
@_message_to_dict_convert_value.register(int)
@_message_to_dict_convert_value.register(str)
def _(simple_obj: Union[str, int]) -> Union[str, int]:
    return simple_obj


def __get_inner_value(value: Value) -> Union[str, int, ListValue, Message]:
    return getattr(value, value.WhichOneof('kind'))  # type: ignore
