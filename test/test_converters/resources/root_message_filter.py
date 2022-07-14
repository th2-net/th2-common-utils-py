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

from th2_grpc_common.common_pb2 import FilterOperation, ListValueFilter, MessageFilter, MetadataFilter, NullValue, \
    RootComparisonSettings, RootMessageFilter, SimpleList, ValueFilter

root_message_filter = RootMessageFilter(
    messageType='MessageType',
    comparison_settings=RootComparisonSettings(),
    message_filter=MessageFilter(fields={
        'FILTER1': ValueFilter(
            operation=FilterOperation.LESS,
            key=True,
            list_filter=ListValueFilter(values=[
                ValueFilter(message_filter=MessageFilter(fields={
                    'msg_filter1': ValueFilter(simple_filter=str('1')),
                    'msg_filter2': ValueFilter(simple_filter=str('2')),
                })),
                ValueFilter(
                    operation=FilterOperation.NOT_EQUAL,
                    key=False,
                    message_filter=MessageFilter(fields={
                        'msg_filter3': ValueFilter(simple_filter=str('3')),
                        'msg_filter4': ValueFilter(simple_filter=str('4')),
                    })
                ),
                ValueFilter(operation=FilterOperation.EQUAL,
                            key=False,
                            simple_list=SimpleList(simple_values=['a', 'b', 'c'])),
                ValueFilter(null_value=NullValue.NULL_VALUE)
            ])
        )
    }),
    metadata_filter=MetadataFilter(property_filters={
        'md_filter1': MetadataFilter.SimpleFilter(value=str('1')),
        'md_filter2': MetadataFilter.SimpleFilter(value=str('2')),
        'md_filter3': MetadataFilter.SimpleFilter(operation=FilterOperation.EQUAL,
                                                  key=True,
                                                  value=str('3')),
        'md_filter4': MetadataFilter.SimpleFilter(operation=FilterOperation.NOT_EQUAL,
                                                  key=False,
                                                  simple_list=SimpleList(simple_values=['4.1', '4.2']))
    })
)

message_filter_dict = {
    'FILTER1': {
        'operation': FilterOperation.LESS,
        'key': True,
        'value': [
            {
                'value': {
                    'msg_filter1': '1',
                    'msg_filter2': '2'
                }
            },
            {
                'operation': FilterOperation.NOT_EQUAL,
                'key': False,
                'value': {
                    'msg_filter3': '3',
                    'msg_filter4': '4',
                }
            },
            {
                'operation': FilterOperation.EQUAL,
                'key': False,
                'value': ['a', 'b', 'c']
            },
            {
                'value': None
            }
        ]
    }
}

metadata_filter_dict = {
    'md_filter1': {
        'value': '1'
    },
    'md_filter2': {
        'value': '2'
    },
    'md_filter3': {
        'operation': FilterOperation.EQUAL,
        'key': True,
        'value': '3'
    },
    'md_filter4': {
        'operation': FilterOperation.NOT_EQUAL,
        'key': False,
        'value': ['4.1', '4.2']
    }
}
