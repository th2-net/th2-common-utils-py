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

import enum
from sortedcontainers import SortedDict
from typing import Union

from th2_common_utils.util.common import ComponentEncoder


class TableEntityType(str, enum.Enum):
    ROW = 'row'
    COLLECTION = 'collection'
    TREE_TABLE = 'treeTable'


class Row:

    def __init__(self) -> None:
        self.type = TableEntityType.ROW
        self.columns = {}

    def add_column(self, name: str, value: Union[str, int, float]):
        self.columns[name] = value


class Collection:

    def __init__(self) -> None:
        self.type = TableEntityType.COLLECTION
        self.rows = SortedDict()

    def add_row(self, name: Union[str, int], row: Row):
        self.rows[name] = row


class TreeTable:

    def __init__(self) -> None:
        self.type = TableEntityType.TREE_TABLE
        self.rows = SortedDict()

    def __bytes__(self):
        return TreeTableEncoder.create_bytes(self)

    def add_row(self, name: str, table_entity: Union[Row, Collection]):
        self.rows[name] = table_entity


class TreeTableEncoder:
    @staticmethod
    def create_bytes(tree_table: TreeTable) -> bytes:
        return ComponentEncoder().encode(tree_table).encode()
