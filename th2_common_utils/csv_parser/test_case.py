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


class TestCase:

    def __init__(self, name='', json_fields=None):
        if json_fields is None:
            json_fields = []
        self.headers = []
        self.rows = []
        self.name = name
        self.json_fields = json_fields

    def set_header(self, headers):
        self.headers = headers

    def append_row(self, row):
        self.rows.append(row)

    def convert_to_json(self) -> str:
        dict_list = []
        for row in self.rows:
            dict_for_row = {}
            for index, value in enumerate(row):
                if value == '' or self.headers[index] == '':
                    continue
                if self.headers[index] in self.json_fields and self.headers[index] != value:
                    dict_for_row[self.headers[index]] = convert_inner_json(value)
                else:
                    dict_for_row[self.headers[index]] = value
            if len(dict_for_row) != 0:
                dict_list.append(dict_for_row)
        return json.dumps(dict_list, indent=4)


def convert_inner_json(json_str):
    return ast.literal_eval(json_str)
