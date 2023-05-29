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
import json
from typing import List

from config import Configuration
from th2_common_utils.event_utils import create_event, create_event_id


class CsvTestCaseEvent:

    def __init__(self, root_event_id, name='', party_fields=None):
        if party_fields is None:
            party_fields = []
        self.headers = []
        self.rows = []
        self.name = name
        self.json_fields = party_fields
        self.event_id = create_event_id()
        self.root_event_id = root_event_id

    def set_header(self, headers: list):
        self.headers = headers

    def convert_row_to_event(self, row: List[str]):
        dict_for_row = {}
        for index, value in enumerate(row):
            if value == '' or self.headers[index] == '':
                continue

            if self.headers[index] in self.json_fields and self.headers[index] != value:
                dict_for_row[self.headers[index]] = convert_inner_json(value)
            else:
                dict_for_row[self.headers[index]] = value
        json_row = json.dumps(dict_for_row)
        return create_event(
            body=json_row,
            parent_id=self.event_id,
            event_type=Configuration.action_event_type
        )

    def convert_to_event(self):
        body = {'caseName': self.name}
        return create_event(
            body=body,
            event_type=Configuration.test_case_event_type,
            event_id=self.event_id,
            parent_id=self.root_event_id
        )


def convert_inner_json(json_str: str):
    return ast.literal_eval(json_str)
