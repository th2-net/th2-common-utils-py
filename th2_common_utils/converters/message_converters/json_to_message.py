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

import json
from pathlib import Path
from typing import Union

from google.protobuf.json_format import ParseDict
from th2_grpc_common.common_pb2 import Message


def json_to_message(json_path: Union[str, Path]) -> Message:
    """Read json file and convert its content to th2-message.

    Args:
        json_path: Path to json file.

    Returns:
        th2-message
    """

    with open(json_path, 'r') as read_content:
        json_dict = json.load(read_content)

    return ParseDict(json_dict, Message())
