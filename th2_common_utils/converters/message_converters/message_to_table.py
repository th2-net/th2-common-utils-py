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
from typing import Any, Dict, List, Optional, Union

from th2_common_utils.converters.message_converters.message_to_dict import message_to_dict
from th2_common_utils.util.tree_table import Table, TreeTable
from th2_grpc_common.common_pb2 import Message


def message_to_table(message: Union[Dict, Message]) -> TreeTable:
    """Converts th2-message or dict to a TreeTable.

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
        message = message_to_dict(message)['fields']

    table = TreeTable(columns_names=['Field Value'])

    for field_name in message:  # type: ignore
        table_entity = _dict_to_table_convert_value(message[field_name],  # type: ignore
                                                    columns_names=table.columns_names)
        if isinstance(table_entity, Table):
            table.add_table(field_name, table_entity)
        else:
            table.add_row(field_name, table_entity)

    return table


@singledispatch
def _dict_to_table_convert_value(entity: Union[str, List, Dict],
                                 *args: Any, **kwargs: Any) -> Optional[Union[str, Table]]:
    raise TypeError('Expected object type of str, int, float, list or dict, got %s' % type(entity))


@_dict_to_table_convert_value.register(dict)
def _(dict_obj: dict, columns_names: List[str]) -> Table:
    table = Table(columns_names)

    for field_name, field_value in dict_obj.items():  # type: ignore
        table_inner_item = _dict_to_table_convert_value(field_value, columns_names=columns_names)
        if isinstance(table_inner_item, Table):
            table.add_table(field_name, table_inner_item)
        else:
            table.add_row(field_name, table_inner_item)

    return table


@_dict_to_table_convert_value.register(list)
def _(list_obj: list, columns_names: List[str]) -> Table:
    table = Table(columns_names)

    for index, list_item in enumerate(list_obj):
        table_inner_item = _dict_to_table_convert_value(list_item, columns_names)
        if isinstance(table_inner_item, Table):
            table.add_table(index, table_inner_item)
        else:
            table.add_row(index, table_inner_item)

    return table


@lru_cache(maxsize=128)
@_dict_to_table_convert_value.register(str)
def _(simple_obj: Union[str, int], *args: Any, **kwargs: Any) -> Union[str, int]:
    return simple_obj
