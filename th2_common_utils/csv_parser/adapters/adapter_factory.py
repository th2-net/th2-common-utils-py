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
from th2_grpc_common.common_pb2 import EventID

from th2_common_utils.csv_parser.adapters.abstact_adapter import AbstractCsvStreamAdapter
from th2_common_utils.csv_parser.adapters.input_adapter import InputCsvStreamAdapter
from th2_common_utils.csv_parser.adapters.prediction_adapter import PredictionCsvStreamAdapter


def create_adapter(filename: str, root_event_id: EventID, csv_version: str) -> AbstractCsvStreamAdapter:
    if filename.endswith("matrix.csv") or filename.endswith("Matrix.csv"):
        return PredictionCsvStreamAdapter(root_event_id, csv_version)
    if filename.endswith("input.csv") or filename.endswith("Input.csv"):
        return InputCsvStreamAdapter(root_event_id, csv_version)
