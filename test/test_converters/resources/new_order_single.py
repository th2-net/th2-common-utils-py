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

from th2_grpc_common.common_pb2 import ConnectionID, Direction, EventID, ListValue, Message, MessageID, \
    MessageMetadata, Value

parent_event_id = EventID()
session_alias = 'kNglFzrW'

trading_party_message = Value(message_value=Message(fields={
    'NoPartyIDs': Value(list_value=ListValue(values=[
        Value(message_value=Message(fields={
            'PartyID': Value(simple_value='1'),
            'PartyIDSource': Value(simple_value='A'),
            'PartyRole': Value(simple_value='11')
        })),
        Value(message_value=Message(fields={
            'PartyID': Value(simple_value='2'),
            'PartyIDSource': Value(simple_value='A'),
            'PartyRole': Value(simple_value='12')
        }))
    ]))
}))

new_order_single_message = Message(
    parent_event_id=parent_event_id,
    metadata=MessageMetadata(message_type='NewOrderSingle',
                             id=MessageID(
                                 connection_id=ConnectionID(session_alias=session_alias),
                                 direction=Direction.FIRST,
                                 sequence=12,
                                 subsequence=[1, 2]),
                             properties={'prop1': '1'}),
    fields={
        'OrdType': Value(simple_value='1'),
        'AccountType': Value(simple_value='2'),
        'OrderCapacity': Value(simple_value='A'),
        'Price': Value(simple_value='100'),
        'TradingParty': trading_party_message
    }
)

new_order_single_message_from_dict = Message(
    parent_event_id=parent_event_id,
    metadata=MessageMetadata(message_type='NewOrderSingle',
                             id=MessageID(
                                 connection_id=ConnectionID(session_alias=session_alias))),
    fields={
        'OrdType': Value(simple_value='1'),
        'AccountType': Value(simple_value='2'),
        'OrderCapacity': Value(simple_value='A'),
        'Price': Value(simple_value='100'),
        'TradingParty': trading_party_message
    }
)

trading_party_dict = {
    'NoPartyIDs': [
        {
            'PartyID': '1',
            'PartyIDSource': 'A',
            'PartyRole': '11'
        },
        {
            'PartyID': '2',
            'PartyIDSource': 'A',
            'PartyRole': '12'
        }
    ]
}

new_order_single_dict = {
    'metadata': {
        'session_alias': 'kNglFzrW',
        'session_group': '',
        'direction': 'FIRST',
        'sequence': 12,
        'subsequence': [1, 2],
        # 'timestamp': None,  # TODO - grpc4 doesn't have timestamp more
        'message_type': 'NewOrderSingle',
        'properties': {'prop1': '1'},
        'protocol': ''
    },
    'parent_event_id': '',
    'fields': {
        'OrdType': '1',
        'AccountType': '2',
        'OrderCapacity': 'A',
        'Price': '100',
        'TradingParty': trading_party_dict
    }
}
