#   Copyright 2020-2021 Exactpro (Exactpro Systems Limited)
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
from th2_grpc_common.common_pb2 import Message, Value, ListValue
from th2_common_utils.convertors import message_to_dict, _value_get as value_get

"""
This patch provides a convenient way for Message fields access.  
The patch is backward compatible.
"""

# =========================
# Value
# =========================

Value.__get__ = value_get


# =========================
# ListValue
# =========================

def listvalue_getitem(self, idx):
    # values -  class 'google.protobuf.pyext._message.RepeatedCompositeContainer (Value inside)
    v: Value = getattr(self, 'values')[idx]
    return v.__get__(v, idx)


def listvalue_len(self):
    return len(self.values)


def listvalue_repr(self):
    val_lst = list(self.values)
    return str([v.__get__('', v) for v in val_lst])


ListValue.__getitem__ = listvalue_getitem
ListValue.__len__ = listvalue_len
ListValue.__repr__ = listvalue_repr


# =========================
# Message
# =========================

def msg_getitem(self, item):
    v: Value = self.fields[item]
    return v.__get__(v, item)


def message_contains(self, item):
    return item in self.fields


def message_repr(self):
    # Used message_to_dict to get more human readable repr output.
    return pformat(message_to_dict(self))


Message.__getitem__ = msg_getitem
Message.__contains__ = message_contains
Message.__repr__ = message_repr
