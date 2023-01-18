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

from th2_common_utils.event_components import Table, TreeTable
from th2_grpc_common.common_pb2 import ListValue, Message, Value


listvalue_message = Value(message_value=Message(fields={
    'ListFields': Value(list_value=ListValue(values=[
        Value(message_value=Message(fields={
            'List_SimpleField1': Value(simple_value='A'),
            'List_SimpleField2': Value(simple_value='B')
        }))
    ]))
}))

message = Message(fields={
    'SimpleField1': Value(simple_value='1'),
    'SimpleField2': Value(simple_value='2'),
    'List': listvalue_message
})


tree_table = TreeTable(columns_names=['Field Value'], sort=True)
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
