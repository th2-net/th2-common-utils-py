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

from itertools import zip_longest
from typing import Any, List, Optional, Union

import orjson
from sortedcontainers import SortedDict


class MessageComponent:

    def __init__(self, data: Any) -> None:
        self.type = 'message'
        self.data = str(data)

    def __bytes__(self) -> bytes:
        return _create_event_body(self)


class AbstractTable:

    def __init__(self, table_type: str, columns_names: List[str], sort: bool):
        self.type = table_type
        self.columns_names = columns_names
        self.sort = sort

        if sort:
            self.rows = SortedDict()
        else:
            self.rows = {}

    def add_row(self, row_name: Union[str, int, float], *values: Optional[Union[str, int, float]]) -> None:
        """Adds row to the table.

        Args:
            row_name: Name of the row.
            *values: Values of row to fit in the table's columns.

        """
        if values:
            self.rows[row_name] = {
                'type': 'row',
                'columns': dict(zip_longest(self.columns_names, values, fillvalue=''))
            }

    def add_table(self, table_name: Union[str, int, float], table: 'TableComponent') -> None:
        """Adds inner table.

        Args:
            table_name: Name of the table.
            table: Table itself.

        """
        self.rows[table_name] = table

    @property
    def __dict__(self) -> dict:
        return {'type': self.type, 'rows': self.rows}

    @__dict__.setter
    def __dict__(self, value: dict) -> None:
        raise NotImplementedError


class TableComponent(AbstractTable):

    def __init__(self, columns_names: List[str], sort: bool = False):
        super().__init__('collection', columns_names, sort)


class TreeTableComponent(AbstractTable):

    def __init__(self, columns_names: List[str], sort: bool = False) -> None:
        super().__init__('treeTable', columns_names, sort)

    def __bytes__(self) -> bytes:
        return _create_event_body(self, sort=self.sort)


def _create_event_body(component: Any, sort: bool = False) -> bytes:
    if sort:
        return orjson.dumps(component,
                            default=lambda o: o.__dict__,
                            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SORT_KEYS)
    else:
        return orjson.dumps(component,
                            default=lambda o: o.__dict__,
                            option=orjson.OPT_NON_STR_KEYS)
