#   Copyright 2022-2023 Exactpro (Exactpro Systems Limited)
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

import ast
from typing import List

from th2_data_services.data_source.lwdp.stub_builder import http_event_stub_builder

from th2_common_utils.event_utils import create_event_id


class ActionEventNameRule:
    def __init__(self, pattern: str, keys: List[str]):
        self.pattern = pattern
        self.keys = keys

    def compile(self, data: dict) -> str:
        values = [data[key] for key in self.keys]
        return self.pattern.format(*values)


class CsvTestCaseEvent:

    def __init__(self, root_event_id, name='', party_fields=None):
        if party_fields is None:
            party_fields = []
        self.headers = []
        self.name = name
        self.json_fields = party_fields
        self.event_id = create_event_id()
        self.root_event_id = root_event_id

    def set_header(self, headers: list):
        self.headers = headers

    def convert_row_to_event(self, row: List[str], event_type: str, name_rule: ActionEventNameRule) -> dict:
        dict_for_row = {}
        for index, value in enumerate(row):
            if value == '' or self.headers[index] == '':
                continue

            if self.headers[index] in self.json_fields and self.headers[index] != value:
                dict_for_row[self.headers[index]] = convert_inner_json(value)
            else:
                dict_for_row[self.headers[index]] = value
        event_name = name_rule.compile(dict_for_row)
        return http_event_stub_builder.build({
            'body': dict_for_row,
            'parentEventId': self.event_id.id,
            'eventType': event_type,
            'eventId': create_event_id().id,
            'eventName': event_name,
            'batchId': None
        })

    def convert_to_event(self, event_type: str) -> dict:
        body = {'caseName': self.name}
        return http_event_stub_builder.build({
            'body': body,
            'parentEventId': self.root_event_id,
            'eventType': event_type,
            'eventId': self.event_id.id,
            'eventName': self.name,
            'batchId': None
        })


def convert_inner_json(json_str: str) -> str:
    return ast.literal_eval(json_str)
