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

from test.test_converters.resources.new_order_single import new_order_single_message

from th2_common_utils.message_fields_access import *  # noqa: F401, F403


def test_message_fields_access() -> None:
    party_id_source = new_order_single_message.fields['TradingParty'].message_value.fields['NoPartyIDs']. \
        list_value.values[1].message_value.fields['PartyIDSource'].simple_value  # noqa: ECE001

    party_id_source_easy_access = new_order_single_message['TradingParty']['NoPartyIDs'][1]['PartyIDSource']

    assert party_id_source_easy_access == party_id_source
