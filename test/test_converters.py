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

from datetime import datetime
import random

from th2_common_utils.util.tree_table import TreeTable, Table

from th2_common_utils import message_to_dict, dict_to_message, message_to_table, dict_to_root_message_filter
from th2_grpc_common.common_pb2 import Value, Message, ListValue, MessageMetadata, MessageID, ConnectionID, EventID, \
    RootMessageFilter, MessageFilter, ValueFilter, ListValueFilter, MetadataFilter, SimpleList, RootComparisonSettings

cl_ord_id = random.randint(10 ** 6, (10 ** 7) - 1)
transact_time = datetime.now().isoformat()
parent_event_id = EventID()

trading_party_message = Value(message_value=Message(fields={'NoPartyIDs': Value(list_value=ListValue(values=[
    Value(message_value=Message(fields={'PartyID': Value(simple_value='DEMO-CONN1'),
                                        'PartyIDSource': Value(simple_value='D'),
                                        'PartyRole': Value(simple_value='76')})),
    Value(message_value=Message(fields={'PartyID': Value(simple_value='0'),
                                        'PartyIDSource': Value(simple_value='P'),
                                        'PartyRole': Value(simple_value='3')})),
    Value(message_value=Message(fields={'PartyID': Value(simple_value='0'),
                                        'PartyIDSource': Value(simple_value='P'),
                                        'PartyRole': Value(simple_value='122')})),
    Value(message_value=Message(fields={'PartyID': Value(simple_value='3'),
                                        'PartyIDSource': Value(simple_value='P'),
                                        'PartyRole': Value(simple_value='12')}))]))}))

new_order_single_message = Message(parent_event_id=parent_event_id,
                                   metadata=MessageMetadata(message_type='NewOrderSingle',
                                                            id=MessageID(
                                                                connection_id=ConnectionID(session_alias='arfq02fix10'))
                                                            ),
                                   fields={
                                       'SecurityID': Value(simple_value='5221001'),
                                       'SecurityIDSource': Value(simple_value='8'),
                                       'OrdType': Value(simple_value='2'),
                                       'AccountType': Value(simple_value='1'),
                                       'OrderCapacity': Value(simple_value='A'),
                                       'OrderQty': Value(simple_value='30'),
                                       'DisplayQty': Value(simple_value='30'),
                                       'Price': Value(simple_value='55'),
                                       'ClOrdID': Value(simple_value=str(cl_ord_id)),
                                       'SecondaryClOrdID': Value(simple_value='11111'),
                                       'Side': Value(simple_value='1'),
                                       'TimeInForce': Value(simple_value='0'),
                                       'TransactTime': Value(simple_value=transact_time),
                                       'TradingParty': trading_party_message
                                   })

trading_party_dict = {'NoPartyIDs': [{'PartyID': 'DEMO-CONN1',
                                      'PartyIDSource': 'D',
                                      'PartyRole': '76'},
                                     {'PartyID': '0',
                                      'PartyIDSource': 'P',
                                      'PartyRole': '3'},
                                     {'PartyID': '0',
                                      'PartyIDSource': 'P',
                                      'PartyRole': '122'},
                                     {'PartyID': '3',
                                      'PartyIDSource': 'P',
                                      'PartyRole': '12'}]}

new_order_single_dict = {'AccountType': '1',
                         'ClOrdID': str(cl_ord_id),
                         'DisplayQty': '30',
                         'OrdType': '2',
                         'OrderCapacity': 'A',
                         'OrderQty': '30',
                         'Price': '55',
                         'SecondaryClOrdID': '11111',
                         'SecurityID': '5221001',
                         'SecurityIDSource': '8',
                         'Side': '1',
                         'TimeInForce': '0',
                         'TradingParty': trading_party_dict,
                         'TransactTime': transact_time}


def test_message_to_dict() -> None:
    assert message_to_dict(new_order_single_message) == new_order_single_dict


def test_dict_to_message() -> None:
    assert dict_to_message(fields=new_order_single_dict,
                           parent_event_id=parent_event_id,
                           session_alias='arfq02fix10',
                           message_type='NewOrderSingle') == new_order_single_message


def test_dict_to_root_message_filter() -> None:
    root_message_filter = RootMessageFilter(
        messageType='MessageType',
        comparison_settings=RootComparisonSettings(),
        message_filter=MessageFilter(
            fields={
                'FILTERS': ValueFilter(
                    list_filter=ListValueFilter(
                        values=[ValueFilter(
                            message_filter=MessageFilter(
                                fields={
                                    'msg_filter1': ValueFilter(simple_filter=str('1')),
                                    'msg_filter2': ValueFilter(simple_filter=str('2')),
                                    'msg_filter3': ValueFilter(simple_filter=str('3')),
                                    'msg_filter4': ValueFilter(simple_filter=str('4'))
                                }
                            )
                        ),
                            ValueFilter(
                                message_filter=MessageFilter(
                                    fields={
                                        'msg_filter5': ValueFilter(simple_filter=str('5')),
                                        'msg_filter6': ValueFilter(simple_filter=str('6')),
                                        'msg_filter7': ValueFilter(simple_filter=str('7')),
                                        'msg_filter8': ValueFilter(simple_filter=str('8'))
                                    }
                                )
                            )
                        ]
                    )
                )
            }
        ),
        metadata_filter=MetadataFilter(
            property_filters={
                'md_filter1': MetadataFilter.SimpleFilter(value=str('1')),
                'md_filter2': MetadataFilter.SimpleFilter(value=str('2')),
                'md_filter3': MetadataFilter.SimpleFilter(value=str('3')),
                'md_filter4': MetadataFilter.SimpleFilter(simple_list=SimpleList(simple_values=['4.1', '4.2']))
            }
        )
    )

    message_filter_dict = {'FILTERS': [{'msg_filter1': '1',
                                        'msg_filter2': '2',
                                        'msg_filter3': '3',
                                        'msg_filter4': '4'},

                                       {'msg_filter5': '5',
                                        'msg_filter6': '6',
                                        'msg_filter7': '7',
                                        'msg_filter8': '8'}]}

    metadata_filter_dict = {'md_filter1': '1',
                            'md_filter2': '2',
                            'md_filter3': '3',
                            'md_filter4': ['4.1', '4.2']}

    assert dict_to_root_message_filter(message_type='MessageType',
                                       message_filter=message_filter_dict,
                                       metadata_filter=metadata_filter_dict) == root_message_filter


def test_message_to_table() -> None:
    listvalue_message = Value(message_value=Message(fields={'ListFields': Value(list_value=ListValue(values=[
        Value(message_value=Message(fields={'List_SimpleField1': Value(simple_value='A'),
                                            'List_SimpleField2': Value(simple_value='B')}))]))}))

    message = Message(fields={'SimpleField1': Value(simple_value='1'),
                              'SimpleField2': Value(simple_value='2'),
                              'List': listvalue_message})

    tree_table = TreeTable(columns_names=['Field Value'])
    tree_table.add_row('SimpleField1', '1')
    tree_table.add_row('SimpleField2', '2')

    list_table = Table(columns_names=tree_table.columns_names)
    nested_list_table = Table(columns_names=tree_table.columns_names)
    nested_list_table_item0 = Table(columns_names=tree_table.columns_names)
    nested_list_table_item0.add_row('List_SimpleField1', 'A')
    nested_list_table_item0.add_row('List_SimpleField2', 'B')

    nested_list_table.add_table(table_name=0, table=nested_list_table_item0)
    list_table.add_table(table_name='ListFields', table=nested_list_table)
    tree_table.add_table(table_name='List', table=list_table)

    assert bytes(tree_table) == bytes(message_to_table(message))
