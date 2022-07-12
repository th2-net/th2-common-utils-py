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

from th2_grpc_common.common_pb2 import ConnectionID, Direction, Message, MessageID, MessageMetadata, Value


message = Message(
    metadata=MessageMetadata(id=MessageID(connection_id=ConnectionID(session_alias='VDnEgqeb'),
                                          direction=Direction.SECOND),
                             message_type='NewOrderSingle',
                             protocol='FIX'),
    fields={
        'Account': Value(simple_value='CLIENT1'),
        'OrderQty': Value(simple_value='4'),
        'OrdType': Value(simple_value='2'),
        'Price': Value(simple_value='2'),
        'trailer': Value(
            message_value=Message(
                fields={
                    'CheckSum': Value(simple_value='127')
                }
            )
        )
    }
)

json_message = '''
{
  "metadata":{
    "id":{
      "connectionId":{
        "sessionAlias":"VDnEgqeb"
      },
      "direction":"SECOND"
    },
    "messageType":"NewOrderSingle",
    "protocol":"FIX"
  },
  "fields":{
    "Account":{
      "simpleValue":"CLIENT1"
    },
    "OrderQty":{
      "simpleValue":"4"
    },
    "OrdType":{
      "simpleValue":"2"
    },
    "Price":{
      "simpleValue":"2"
    },
    "trailer":{
      "messageValue":{
        "fields":{
          "CheckSum":{
            "simpleValue":"127"
          }
        }
      }
    }
  }
}
'''
