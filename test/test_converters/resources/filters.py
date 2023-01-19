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

from th2_grpc_common.common_pb2 import FilterOperation, ListValueFilter, MessageFilter, MetadataFilter, \
    RootMessageFilter, SimpleList, ValueFilter

from th2_common_utils.converters.filter_converters import FieldFilter


root_message_filter = RootMessageFilter(
    messageType='MessageType',
    message_filter=MessageFilter(fields={
        'field1': ValueFilter(simple_filter='1', operation=FilterOperation.EQUAL),
        'field2': ValueFilter(simple_filter='2', operation=FilterOperation.NOT_EQUAL, key=True),
        'field3': ValueFilter(operation=FilterOperation.EMPTY, key=True),
        'field4': ValueFilter(operation=FilterOperation.NOT_EMPTY),
        'field5': ValueFilter(simple_list=SimpleList(simple_values=['AB', 'BC', 'CD']), operation=FilterOperation.IN),
        'field6': ValueFilter(simple_list=SimpleList(simple_values=['AB', 'BC', 'CD']),
                              operation=FilterOperation.NOT_IN),
        'field7': ValueFilter(simple_filter='^TH*2$', operation=FilterOperation.LIKE),
        'field8': ValueFilter(simple_filter='^TH2$', operation=FilterOperation.NOT_LIKE),
        'field9': ValueFilter(list_filter=ListValueFilter(values=[
            ValueFilter(message_filter=MessageFilter(fields={
                'inner_field1': ValueFilter(simple_filter='1', operation=FilterOperation.MORE),
                'inner_field2': ValueFilter(simple_filter='2', operation=FilterOperation.NOT_LESS)
            })),
            ValueFilter(message_filter=MessageFilter(fields={
                'inner_field3': ValueFilter(simple_filter='3', operation=FilterOperation.LESS),
                'inner_field4': ValueFilter(simple_filter='4', operation=FilterOperation.NOT_MORE)
            }))
        ])),
        'field10': ValueFilter(simple_filter='ABC?', operation=FilterOperation.WILDCARD),
        'field11': ValueFilter(simple_filter='ABC*', operation=FilterOperation.NOT_WILDCARD),
        'field12': ValueFilter(simple_filter='0.5', operation=FilterOperation.EQ_TIME_PRECISION),
        'field13': ValueFilter(simple_filter='0.1', operation=FilterOperation.EQ_DECIMAL_PRECISION),
    }),
    metadata_filter=MetadataFilter(property_filters={
        'md_field1': MetadataFilter.SimpleFilter(value=str('1')),
        'md_field2': MetadataFilter.SimpleFilter(value=str('2')),
        'md_field3': MetadataFilter.SimpleFilter(value=str('3'),
                                                 operation=FilterOperation.NOT_EQUAL,
                                                 key=True),
        'md_field4': MetadataFilter.SimpleFilter(simple_list=SimpleList(simple_values=['X', 'W']),
                                                 operation=FilterOperation.IN)
    })
)


value_filters_dict = root_message_filter.message_filter.fields


message_filter_dict = {
    'field1': 1,  # EQUAL
    'field2': FieldFilter(2, operation=FilterOperation.NOT_EQUAL, key=True),
    'field3': FieldFilter(operation=FilterOperation.EMPTY, key=True),
    'field4': FieldFilter(operation=FilterOperation.NOT_EMPTY),
    'field5': FieldFilter(['AB', 'BC', 'CD'], operation=FilterOperation.IN),
    'field6': FieldFilter(['AB', 'BC', 'CD'], operation=FilterOperation.NOT_IN),
    'field7': FieldFilter('^TH*2$', operation=FilterOperation.LIKE),
    'field8': FieldFilter('^TH2$', operation=FilterOperation.NOT_LIKE),
    'field9': [
        {
            'inner_field1': FieldFilter(1, operation=FilterOperation.MORE),
            'inner_field2': FieldFilter(2, operation=FilterOperation.NOT_LESS)
        },
        {
            'inner_field3': FieldFilter(3, operation=FilterOperation.LESS),
            'inner_field4': FieldFilter(4, operation=FilterOperation.NOT_MORE)
        }
    ],
    'field10': FieldFilter('ABC?', operation=FilterOperation.WILDCARD),
    'field11': FieldFilter('ABC*', operation=FilterOperation.NOT_WILDCARD),
    'field12': FieldFilter(0.5, operation=FilterOperation.EQ_TIME_PRECISION),
    'field13': FieldFilter(0.1, operation=FilterOperation.EQ_DECIMAL_PRECISION),
}

metadata_filter_dict = {
    'md_field1': 1,
    'md_field2': 2,
    'md_field3': FieldFilter(3, operation=FilterOperation.NOT_EQUAL, key=True),
    'md_field4': FieldFilter(['X', 'W'], operation=FilterOperation.IN)
}
