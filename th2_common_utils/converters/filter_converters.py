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

from typing import Any, Dict, List, Optional, Union

from google.protobuf.duration_pb2 import Duration
from th2_grpc_common.common_pb2 import FilterOperation, ListValueFilter, MessageFilter, MetadataFilter, \
    RootComparisonSettings, RootMessageFilter, SimpleList, ValueFilter


class FieldFilter:
    __slots__ = ('value', 'operation', 'key')

    def __init__(self,
                 value: Optional[Any] = None,
                 operation: Any = FilterOperation.EQUAL,
                 key: bool = False):
        self.value = value
        self.operation = operation
        self.key = key


FieldsDict = Dict[str, Any]


def dict_to_root_message_filter(message_type: str = '',
                                message_filter: Optional[Union[FieldsDict, MessageFilter]] = None,
                                metadata_filter: Optional[Union[FieldsDict, MetadataFilter]] = None,
                                ignore_fields: Optional[List[str]] = None,
                                check_repeating_group_order: bool = False,
                                time_precision: Optional[Duration] = None,
                                decimal_precision: str = '') -> RootMessageFilter:
    """Converts a dict to RootMessageFilter.

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
        RootMessageFilter class instance.

    Raises:
        TypeError: Occurs when MessageFilter or MetadataFilter as dicts contain a field of the unsupported type.
    """

    root_message_filter = RootMessageFilter(messageType=message_type)

    if isinstance(message_filter, MessageFilter):
        root_message_filter.message_filter.CopyFrom(message_filter)
    elif isinstance(message_filter, Dict):
        root_message_filter.message_filter.CopyFrom(to_message_filter(message_filter))

    if isinstance(metadata_filter, MetadataFilter):
        root_message_filter.metadata_filter.CopyFrom(metadata_filter)
    elif isinstance(metadata_filter, Dict):
        root_message_filter.metadata_filter.CopyFrom(dict_to_metadata_filter(metadata_filter))

    root_comparison_settings: Dict[str, Any] = {}

    if ignore_fields is not None:
        root_comparison_settings['ignore_fields'] = ignore_fields
    if check_repeating_group_order:
        root_comparison_settings['check_repeating_group_order'] = check_repeating_group_order
    if time_precision is not None:
        root_comparison_settings['time_precision'] = time_precision
    if len(decimal_precision) > 0:
        root_comparison_settings['decimal_precision'] = decimal_precision

    if len(root_comparison_settings) > 0:
        root_message_filter.comparison_settings.CopyFrom(RootComparisonSettings(**root_comparison_settings))

    return root_message_filter


def dict_values_to_value_filters(fields: Dict[str, Any]) -> Dict[str, ValueFilter]:
    return {k: to_value_filter(v) for k, v in fields.items()}


# =========================
# MessageFilter
# =========================

def to_message_filter(dict_obj: Dict[str, Any]) -> MessageFilter:
    return MessageFilter(fields={k: to_value_filter(v) for k, v in dict_obj.items()})


def to_value_filter(value: Any) -> ValueFilter:
    if isinstance(value, FieldFilter):
        value_filter = to_value_filter(value.value)
        value_filter.operation = value.operation
        value_filter.key = value.key
        return value_filter

    elif isinstance(value, (str, int, float)):
        return ValueFilter(simple_filter=str(value))

    elif isinstance(value, dict):
        return dict_to_value_filter(value)

    elif isinstance(value, list):
        return list_to_value_filter(value)

    elif value is None:
        return ValueFilter()

    else:
        raise TypeError(f'Cannot convert {type(value)} object to ValueFilter: {value}')


def list_to_value_filter(list_value: list) -> ValueFilter:
    if all(isinstance(v, str) for v in list_value):
        return ValueFilter(simple_list=SimpleList(simple_values=[str(v) for v in list_value]))
    else:
        return ValueFilter(list_filter=ListValueFilter(values=[to_value_filter(v) for v in list_value]))


def dict_to_value_filter(dict_value: dict) -> ValueFilter:
    return ValueFilter(message_filter=MessageFilter(fields={k: to_value_filter(v) for k, v in dict_value.items()}))


# =========================
# MetadataFilter
# =========================

def dict_to_metadata_filter(fields: Dict[str, Any]) -> MetadataFilter:
    return MetadataFilter(property_filters={
        filter_name: to_simple_filter(filter_value)
        for filter_name, filter_value in fields.items()
    })


def to_simple_filter(value: Any) -> MetadataFilter.SimpleFilter:
    if isinstance(value, FieldFilter):
        value_filter = to_simple_filter(value.value)
        value_filter.operation = value.operation
        value_filter.key = value.key
        return value_filter

    elif isinstance(value, (str, int, float)):
        return MetadataFilter.SimpleFilter(value=str(value))

    elif isinstance(value, list):
        if all(isinstance(v, (str, int, float)) for v in value):
            return MetadataFilter.SimpleFilter(simple_list=SimpleList(simple_values=[str(v) for v in value]))
        else:
            raise TypeError(f'Expected list to contain strings: {value}')

    else:
        raise TypeError(f'Cannot convert {type(value)} object to ValueFilter: {value}')
