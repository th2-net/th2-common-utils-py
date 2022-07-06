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

from pathlib import Path
from test.test_converters.resources import json_message, table
from test.test_converters.resources.new_order_single import new_order_single_dict, new_order_single_message, \
    parent_event_id, session_alias
from test.test_converters.resources.root_message_filter import message_filter_dict, metadata_filter_dict, \
    root_message_filter

from th2_common_utils.converters.filter_converters import dict_to_root_message_filter
from th2_common_utils.converters.message_converters.dict_to_message import dict_to_message
from th2_common_utils.converters.message_converters.json_to_message import json_to_message
from th2_common_utils.converters.message_converters.message_to_dict import message_to_dict
from th2_common_utils.converters.message_converters.message_to_table import message_to_table


def test_message_to_dict() -> None:
    assert message_to_dict(new_order_single_message) == new_order_single_dict


def test_dict_to_message() -> None:
    assert dict_to_message(fields=new_order_single_dict,
                           parent_event_id=parent_event_id,
                           session_alias=session_alias,
                           message_type='NewOrderSingle') == new_order_single_message


def test_dict_to_root_message_filter() -> None:
    assert dict_to_root_message_filter(message_type='MessageType',
                                       message_filter=message_filter_dict,
                                       metadata_filter=metadata_filter_dict) == root_message_filter


def test_message_to_table() -> None:
    assert bytes(table.tree_table) == bytes(message_to_table(table.message))


def test_json_to_message() -> None:
    json_path = Path(__file__).parent / 'resources' / 'message.json'

    assert json_to_message(json_path) == json_message.message
