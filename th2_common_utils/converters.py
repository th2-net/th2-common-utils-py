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


import enum
from typing import List, Callable, Union, Dict

from google.protobuf.duration_pb2 import Duration
from th2_common_utils.util.tree_table import TreeTable, Collection, Row
from th2_grpc_common.common_pb2 import Message, ListValue, Value, MessageMetadata, MessageID, ConnectionID, \
    RootMessageFilter, MessageFilter, MetadataFilter, RootComparisonSettings, ValueFilter, ListValueFilter, \
    SimpleList, EventID


class ValueType(str, enum.Enum):

    WHICH_ONE_OF = 'kind'

    SIMPLE = 'simple_value'
    LIST = 'list_value'
    MESSAGE = 'message_value'


class TypeName(str, enum.Enum):

    STR = 'str'
    INT = 'int'
    FLOAT = 'float'
    LIST = 'list'
    DICT = 'dict'

    VALUE = 'Value'
    LIST_VALUE = 'ListValue'
    MESSAGE = 'Message'

    VALUE_FILTER = 'ValueFilter'


def _message_to_dict_convert_value(value):
    value_kind = value.WhichOneof(ValueType.WHICH_ONE_OF)
    if value_kind == ValueType.SIMPLE:
        return value.simple_value
    elif value_kind == ValueType.LIST:
        return [_message_to_dict_convert_value(list_item) for list_item in value.list_value.values]
    elif value_kind == ValueType.MESSAGE:
        return {field: _message_to_dict_convert_value(value.message_value.fields[field])
                for field in value.message_value.fields}


def message_to_dict(message: Message) -> Dict:
    """Converts th2-message to a dict.

    Fields of th2-message will be converted to a dict. You will lose all metadata.

    Args:
        message: th2-message.

    Returns:
        th2-message fields (message.fields) as a dict. All nested entities will be also converted.

        Conversion rules:
            Value.simple_value - str
            Value.list_value - list
            Value.message_value - dict

    Raises:
        TypeError: Occurs when 'message.fields' contains a field not of the 'Value' type.
    """

    return {field: _message_to_dict_convert_value(message.fields[field]) for field in message.fields}


def _dict_to_message_convert_value(value):
    value_type = type(value).__name__

    if value_type in {TypeName.STR, TypeName.INT, TypeName.FLOAT}:
        return Value(simple_value=str(value))
    elif value_type == TypeName.LIST:
        return Value(list_value=ListValue(values=[_dict_to_message_convert_value(x) for x in value]))
    elif value_type == TypeName.DICT:
        return Value(message_value=Message(fields={key: _dict_to_message_convert_value(value[key]) for key in value}))

    elif value_type == TypeName.VALUE:
        return value
    elif value_type == TypeName.LIST_VALUE:
        return Value(list_value=value)
    elif value_type == TypeName.MESSAGE:
        return Value(message_value=value)

    else:
        raise TypeError('Cannot convert %s object.' % value_type)


def dict_to_message(fields: dict, parent_event_id: EventID = None, session_alias: str = None,
                    message_type: str = None) -> Message:
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
                   fields={field: _dict_to_message_convert_value(fields[field]) for field in fields})


def _convert_filter_value(value, message_type=None, direction=None, values=False, metadata=False):
    value_type = type(value).__name__

    if value_type == TypeName.VALUE_FILTER:
        return value

    elif value_type in {TypeName.STR, TypeName.INT, TypeName.FLOAT} and values is True:
        return ValueFilter(simple_filter=str(value))
    elif value_type in {TypeName.STR, TypeName.INT, TypeName.FLOAT} and metadata is True:
        return MetadataFilter.SimpleFilter(value=str(value))

    elif value_type == TypeName.LIST and values is True:
        return ValueFilter(list_filter=ListValueFilter(
            values=[_convert_filter_value(x, values=values, metadata=metadata) for x in value]))
    elif value_type == TypeName.LIST and metadata is True:
        return MetadataFilter.SimpleFilter(simple_list=SimpleList(simple_values=value))

    elif value_type == TypeName.DICT:
        return ValueFilter(
            message_filter=MessageFilter(messageType=message_type,
                                         fields={key: _convert_filter_value(value[key],
                                                                            values=values,
                                                                            metadata=metadata)
                                                 for key in value},
                                         direction=direction))
    else:
        raise TypeError('Cannot convert %s object.' % type(value))


def dict_to_root_message_filter(message_type: str = None,
                                message_filter: Union[Dict, MessageFilter] = None,
                                metadata_filter: Union[Dict, MetadataFilter] = None,
                                ignore_fields: List[str] = None,
                                check_repeating_group_order: bool = None,
                                time_precision: Duration = None,
                                decimal_precision: str = None) -> RootMessageFilter:
    """Converts a dict to root message filter.

    Args:
        message_type: Message type.
        message_filter: Message filter as a dict or MessageFilter class instance.
        metadata_filter: Metadata filter as a dict or MetadataFilter class instance.
        ignore_fields: Fields to ignore (is used when creating filter's comparison settings).
        check_repeating_group_order: Whether check repeating group order or not (is used when creating filter's
            comparison settings).
        time_precision: Time precision (is used when creating filter's comparison settings).
        decimal_precision: Decimal Precision (is used when creating filter's comparison settings).

    Returns:
        Root message filter class instance.

    Raises:
        TypeError: Occurs when MessageFilter or MetadataFilter as dicts contain a field of the unsupported type.
    """

    if message_filter is None:
        message_filter = MessageFilter()
    if isinstance(message_filter, Dict):
        message_filter = MessageFilter(fields={field: _convert_filter_value(message_filter[field], values=True)
                                               for field in message_filter})

    if metadata_filter is None:
        metadata_filter = MetadataFilter()
    elif isinstance(metadata_filter, Dict):
        metadata_filter = MetadataFilter(property_filters={
            value: _convert_filter_value(metadata_filter[value], metadata=True)
            for value in metadata_filter
        })

    return RootMessageFilter(messageType=message_type,
                             message_filter=message_filter,
                             metadata_filter=metadata_filter,
                             comparison_settings=RootComparisonSettings(
                                 ignore_fields=ignore_fields,
                                 check_repeating_group_order=check_repeating_group_order,
                                 time_precision=time_precision,
                                 decimal_precision=decimal_precision))


def _convert_value_into_typed_field(value, typed_value):
    field_value_kind = value.WhichOneof(ValueType.WHICH_ONE_OF)

    if field_value_kind == ValueType.SIMPLE:
        return type(typed_value)(value.simple_value)
    elif field_value_kind == ValueType.LIST:
        return [_convert_value_into_typed_field(list_item, typed_value.add()) for list_item in value.list_value.values]
    elif field_value_kind == ValueType.MESSAGE:
        fields_typed = {
            field: _convert_value_into_typed_field(value.message_value.fields[field], getattr(typed_value, field))
            for field in value.message_value.fields
        }
        return type(typed_value)(**fields_typed)


def message_to_typed_message(message: Message, message_type: Callable):
    """Converts th2-message to typed message.

    Args:
        message: th2-message.
        message_type: Typed message class object (described in gRPC API).

    Returns:
        Message as typed message class instance.

    Raises:
        TypeError: Occurs when 'message.fields' contains a field not of the 'Value' type.
    """

    response_fields = [field.name for field in message_type().DESCRIPTOR.fields]
    fields_typed = {field: _convert_value_into_typed_field(message.fields[field], getattr(message_type(), field))
                    for field in response_fields}
    return message_type(**fields_typed)


class TableColumnName(str, enum.Enum):

    FIELD_VALUE = 'Field Value'


def _message_to_table_convert_value(value):
    value_type = type(value).__name__

    if value_type in {TypeName.STR, TypeName.INT, TypeName.FLOAT}:
        table_entity = Row()
        table_entity.add_column(name=TableColumnName.FIELD_VALUE, value=value)
    elif value_type == TypeName.LIST:
        table_entity = Collection()
        for index, item in enumerate(value):
            table_entity.add_row(name=index, row=_message_to_table_convert_value(item))
    elif value_type == TypeName.DICT:
        table_entity = Collection()
        for item in value:
            table_entity.add_row(name=item, row=_message_to_table_convert_value(value[item]))
    else:
        raise TypeError('Expected object type of str, int, float, list or dict, got %s' % type(value))
    return table_entity


def message_to_table(message: Union[Message, Dict]) -> TreeTable:
    """Converts th2-message or dict to a tree table.

    Table can have only two columns. Nested tables are allowed. You will lose 'parent_event_id' and 'metadata'
        of the message.

    Args:
        message: th2-message.

    Returns:
        Tree table with two columns - one contains the name of the field and the other contains the value of this field.

    Raises:
        TypeError: Occurs when 'message.fields' contains a field not of the 'Value' type.
    """

    if isinstance(message, Message):
        message = message_to_dict(message)

    table = TreeTable()

    for field_name in message:
        table_entity = _message_to_table_convert_value(message[field_name])
        table.add_row(field_name, table_entity)

    return table
