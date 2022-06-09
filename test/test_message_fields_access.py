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

from th2_common_utils.message_fields_access import *  # noqa: F401, F403
from th2_grpc_common.common_pb2 import ListValue, Message, Value

trading_party = Value(message_value=Message(fields={
    'NoPartyIDs': Value(list_value=ListValue(values=[
        Value(message_value=Message(fields={
            'PartyIDSource': Value(simple_value='A'),
        })),
        Value(message_value=Message(fields={
            'PartyIDSource': Value(simple_value='B'),
        })),
        Value(message_value=Message(fields={
            'PartyIDSource': Value(simple_value='C'),
        })),
        Value(message_value=Message(fields={
            'PartyIDSource': Value(simple_value='D'),
        }))
    ]))
}))

new_order_single = Message(fields={'TradingParty': trading_party})


def test_message_fields_access() -> None:
    party_id_source = new_order_single.fields['TradingParty'].message_value.fields['NoPartyIDs'].list_value.values[3] \
        .message_value.fields['PartyIDSource'].simple_value  # noqa: ECE001

    party_id_source_easy_access = new_order_single['TradingParty']['NoPartyIDs'][3]['PartyIDSource']  # type: ignore

    assert party_id_source_easy_access == party_id_source
