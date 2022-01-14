# Copyright 2020-2021 Exactpro (Exactpro Systems Limited)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import copy

from typing import List, Callable

from google.protobuf.duration_pb2 import Duration
from th2_grpc_common.common_pb2 import Message, ListValue, Value, MessageMetadata, MessageID, ConnectionID, \
    RootMessageFilter, MessageFilter, MetadataFilter, RootComparisonSettings, ValueFilter, ListValueFilter, SimpleList


def message_to_dict(msg):
    """
    Convert protobuf class Message to dict.

    Note, you will lose all metadata of the Message.
    """

    if isinstance(msg, Message):
        d = {}
        for k in (msg.fields.keys()):
            fk = _value_get(msg.fields[k], None, k)
            d[k] = message_to_dict(fk)
    elif isinstance(msg, ListValue):
        return [message_to_dict(_value_get(v, None, None)) for v in tuple(msg.values)]
    elif isinstance(msg, Value):
        return _value_get(msg, None, None)
    else:
        return msg

    return d


def dict_to_message(fields: dict, message_type='none_type', session_alias=''):
    """Convert dict to protobuf class Message."""

    fields = copy.deepcopy(fields)
    for field, f_val in fields.items():
        if isinstance(f_val, (str, int, float)) or f_val is None:
            fields[field] = Value(simple_value=str(f_val))
        elif isinstance(f_val, dict):
            fields[field] = Value(message_value=dict_to_message(f_val))
        elif isinstance(f_val, (list, tuple)):
            lst = []
            for v in f_val:
                lst.append(Value(message_value=dict_to_message(v)))
            fields[field] = Value(list_value=ListValue(values=lst))
        else:
            fields[field] = Value(message_value=dict_to_message(vars(f_val)))
    return Message(
        metadata=MessageMetadata(
            message_type=message_type,
            id=MessageID(
                connection_id=ConnectionID(session_alias=session_alias))),
        fields=fields)


def _value_get(self, instance, item):
    """__get__ descriptor for protobuf class Value."""

    try:
        return getattr(self, self.ListFields()[0][0].name)
    except IndexError:
        # If you request protobuf class Value without any values inside, you will get IndexError.
        # Occurs when requesting a non-existent key in the dict.
        return None


def convert_message_value(value):
    if isinstance(value, Value):
        return value
    elif isinstance(value, (str, int, float)):
        return Value(simple_value=str(value))
    elif isinstance(value, list):
        return Value(list_value=ListValue(values=[convert_message_value(x) for x in value]))
    elif isinstance(value, dict):
        return Value(message_value=Message(fields={key: convert_message_value(value[key]) for key in value}))


def create_message(fields: dict, session_alias=None, message_type=None):
    return Message(metadata=MessageMetadata(id=MessageID(connection_id=ConnectionID(session_alias=session_alias)),
                                            message_type=message_type),
                   fields={field: convert_message_value(fields[field]) for field in fields})


def convert_filter_value(value, message_type=None, direction=None, values=False, metadata=False):
    if isinstance(value, ValueFilter):
        return value
    elif isinstance(value, (str, int, float)) and values is True:
        return ValueFilter(simple_filter=str(value))
    elif isinstance(value, (str, int, float)) and metadata is True:
        return MetadataFilter.SimpleFilter(value=str(value))
    elif isinstance(value, list) and values is True:
        return ValueFilter(list_filter=ListValueFilter(
            values=[convert_filter_value(x, values=values, metadata=metadata) for x in value]))
    elif isinstance(value, list) and metadata is True:
        return MetadataFilter.SimpleFilter(simple_list=SimpleList(simple_values=value))
    elif isinstance(value, dict):
        return ValueFilter(
            message_filter=MessageFilter(messageType=message_type,
                                         fields={key: convert_filter_value(value[key],
                                                                           values=values,
                                                                           metadata=metadata)
                                                 for key in value},
                                         direction=direction))


def create_root_message_filter(message_type=None,
                               message_filter=None,
                               metadata_filter=None,
                               ignore_fields: List[str] = None,
                               check_repeating_group_order: bool = None,
                               time_precision: Duration = None,
                               decimal_precision: str = None):
    if message_filter is None:
        message_filter = {}
    if metadata_filter is None:
        metadata_filter = {}
    return RootMessageFilter(messageType=message_type,
                             message_filter=MessageFilter(fields={
                                 field: convert_filter_value(message_filter[field], values=True)
                                 for field in message_filter}),
                             metadata_filter=MetadataFilter(property_filters={
                                 value: convert_filter_value(metadata_filter[value], metadata=True)
                                 for value in metadata_filter}),
                             comparison_settings=RootComparisonSettings(
                                 ignore_fields=ignore_fields,
                                 check_repeating_group_order=check_repeating_group_order,
                                 time_precision=time_precision,
                                 decimal_precision=decimal_precision))


def convert_value_into_typed_field(field_value, typed_field_value):
    if field_value.WhichOneof('kind') == 'simple_value':
        return type(typed_field_value)(field_value.simple_value)
    elif field_value.WhichOneof('kind') == 'list_value':
        return [convert_value_into_typed_field(list_item, typed_field_value.add())
                for list_item in field_value.list_value.values]
    elif field_value.WhichOneof('kind') == 'message_value':
        fields_typed = {field: convert_value_into_typed_field(field_value.message_value.fields[field],
                                                              getattr(typed_field_value, field))
                        for field in field_value.message_value.fields}
        return type(typed_field_value)(**fields_typed)


def create_typed_message_from_message(message, message_type: Callable):
    response_fields = [field.name for field in message_type().DESCRIPTOR.fields]
    fields_typed = {field: convert_value_into_typed_field(message.fields[field], getattr(message_type(), field))
                    for field in response_fields}
    return message_type(**fields_typed)
