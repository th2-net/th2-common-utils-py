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


from pprint import pformat

from th2_common_utils.converters import message_to_dict, _dict_to_message_convert_value, ValueType, TypeName
from th2_grpc_common.common_pb2 import Value, ListValue, Message


# =========================
# Value
# =========================

def value_get(self, item):
    return getattr(self, self.WhichOneof(ValueType.KIND))


Value.__get__ = value_get


# =========================
# ListValue
# =========================

def listvalue_getitem(self, index):
    value = self.values[index]
    return value.__get__(index)


def listvalue_len(self):
    return len(self.values)


ListValue.__getitem__ = listvalue_getitem
ListValue.__len__ = listvalue_len


# =========================
# Message
# =========================

def message_setitem(self, key, value):
    value_type = type(value).__name__

    if value_type in {TypeName.STR, TypeName.INT, TypeName.FLOAT}:
        self.fields[key].simple_value = str(value)

    elif value_type == TypeName.VALUE:
        self.fields[key].simple_value = value.simple_value

    elif value_type in {TypeName.LIST, TypeName.LIST_VALUE}:
        th2_value = _dict_to_message_convert_value(value)
        self.fields[key].list_value.CopyFrom(th2_value.list_value)

    elif value_type in {TypeName.DICT, TypeName.MESSAGE}:
        th2_value = _dict_to_message_convert_value(value)
        self.fields[key].message_value.CopyFrom(th2_value.message_value)

    else:
        raise TypeError('Cannot set %s object as field value.' % value_type)


def message_getitem(self, item):
    if item in self.fields:
        value = self.fields[item]
        return value.__get__(item)
    else:
        raise KeyError(item)


def message_contains(self, item):
    return item in self.fields


def message_repr(self):
    return pformat(message_to_dict(self))


Message.__setitem__ = message_setitem
Message.__getitem__ = message_getitem
Message.__contains__ = message_contains
Message.__repr__ = message_repr
