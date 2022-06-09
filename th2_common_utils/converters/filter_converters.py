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

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from google.protobuf.duration_pb2 import Duration
from th2_common_utils.converters.message_converters import TypeName
from th2_grpc_common.common_pb2 import ListValueFilter, MessageFilter, MetadataFilter, NullValue, \
    RootComparisonSettings, RootMessageFilter, SimpleList, ValueFilter


class ProtobufDefaults(Enum):
    BOOL = False
    INT = 0


class FilterField(str, Enum):
    OPERATION = 'operation'
    KEY = 'key'
    VALUE = 'value'


def __is_list_value_filter(value: List[Any]) -> bool:
    if isinstance(value[0], Dict):
        return True

    return False


def __is_simple_list(value: List[Any]) -> bool:
    if isinstance(value[0], (str, int, float)):
        return True

    return False


def __convert_entity_to_simple_filer(entity: Any) -> MetadataFilter.SimpleFilter:
    entity_type = type(entity).__name__

    if entity_type in {TypeName.STR, TypeName.INT, TypeName.FLOAT}:
        return MetadataFilter.SimpleFilter(value=str(entity))

    elif entity_type == TypeName.LIST and __is_simple_list(entity):
        return MetadataFilter.SimpleFilter(simple_list=SimpleList(simple_values=list(map(str, entity))))

    else:
        raise TypeError('Cannot convert %s object to MetadataFilter.SimpleFilter: %s' % (type(entity), entity))


def _create_simple_filter(entity: Any) -> MetadataFilter.SimpleFilter:
    entity_type = type(entity).__name__

    if entity_type == TypeName.SIMPLE_FILTER:
        return entity  # type: ignore

    elif entity_type == TypeName.DICT:
        simple_filter = __convert_entity_to_simple_filer(entity[FilterField.VALUE])

        simple_filter.operation = entity.get(FilterField.OPERATION, ProtobufDefaults.INT.value)
        simple_filter.key = entity.get(FilterField.KEY, ProtobufDefaults.BOOL.value)

        return simple_filter

    else:
        raise TypeError('Cannot convert %s object to MetadataFilter.SimpleFilter: %s' % (type(entity), entity))


def __convert_entity_to_value_filter(entity: Any) -> ValueFilter:
    entity_type = type(entity).__name__

    if entity_type == TypeName.VALUE_FILTER:
        return entity  # type: ignore

    elif entity_type in {TypeName.STR, TypeName.INT, TypeName.FLOAT}:
        return ValueFilter(simple_filter=str(entity))

    elif entity_type == TypeName.LIST and __is_simple_list(entity):
        return ValueFilter(simple_list=SimpleList(simple_values=list(map(str, entity))))

    elif entity_type == TypeName.LIST and __is_list_value_filter(entity):
        return ValueFilter(list_filter=ListValueFilter(values=list(map(_create_value_filter, entity))))

    elif entity_type == TypeName.DICT:
        return ValueFilter(message_filter=dict_to_message_filter(entity))

    elif entity_type == TypeName.NONE:
        return ValueFilter(null_value=NullValue.NULL_VALUE)

    else:
        raise TypeError('Cannot convert %s object to ValueFilter: %s' % (type(entity), entity))


def _create_value_filter(entity: Any) -> ValueFilter:
    if isinstance(entity, Dict):
        value_filter = __convert_entity_to_value_filter(entity.get(FilterField.VALUE))

        value_filter.operation = entity.get(FilterField.OPERATION, ProtobufDefaults.INT.value)
        value_filter.key = entity.get(FilterField.KEY, ProtobufDefaults.BOOL.value)

        return value_filter

    else:
        return __convert_entity_to_value_filter(entity)


def dict_to_message_filter(entity: Dict[str, Any]) -> MessageFilter:
    return MessageFilter(fields={
        filter_name: _create_value_filter(filter_value)
        for filter_name, filter_value in entity.items()
    })


def dict_to_metadata_filter(entity: Dict[str, Any]) -> MetadataFilter:
    return MetadataFilter(property_filters={
        filter_name: _create_simple_filter(filter_value)
        for filter_name, filter_value in entity.items()
    })


MetadataDict = Dict[str, Any]


def dict_to_root_message_filter(message_type: str = '',
                                message_filter: Optional[Union[MetadataDict, MessageFilter]] = None,
                                metadata_filter: Optional[Union[MetadataDict, MetadataFilter]] = None,
                                ignore_fields: Optional[List[str]] = None,
                                check_repeating_group_order: bool = False,
                                time_precision: Optional[Duration] = None,
                                decimal_precision: str = '') -> RootMessageFilter:
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
    elif isinstance(message_filter, Dict):
        message_filter = dict_to_message_filter(message_filter)

    if metadata_filter is None:
        metadata_filter = MetadataFilter()
    elif isinstance(metadata_filter, Dict):
        metadata_filter = dict_to_metadata_filter(metadata_filter)

    return RootMessageFilter(messageType=message_type,
                             message_filter=message_filter,
                             metadata_filter=metadata_filter,
                             comparison_settings=RootComparisonSettings(
                                 ignore_fields=ignore_fields,
                                 check_repeating_group_order=check_repeating_group_order,
                                 time_precision=time_precision,
                                 decimal_precision=decimal_precision))
