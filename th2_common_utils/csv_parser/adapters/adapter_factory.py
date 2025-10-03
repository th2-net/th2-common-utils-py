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

from th2_common_utils.csv_parser.adapters.abstact_adapter import AbstractCsvStreamAdapter
from th2_common_utils.csv_parser.adapters.input_adapter import InputCsvStreamAdapter
from th2_common_utils.csv_parser.adapters.prediction_adapter import PredictionCsvStreamAdapter


def create_adapter(path: str, csv_version: str) -> AbstractCsvStreamAdapter:
    # TODO - to be honest I think it's bad idea to have file name dependency.
    #   These wiles can have any names.

    if path.endswith("matrix.csv") or path.endswith("Matrix.csv"):
        return PredictionCsvStreamAdapter(
            path=path,
            csv_version=csv_version
        )
    if path.endswith("input.csv") or path.endswith("Input.csv"):
        return InputCsvStreamAdapter(
            path=path,
            csv_version=csv_version
        )
    raise ValueError("Failed to identify adapter for this file")

