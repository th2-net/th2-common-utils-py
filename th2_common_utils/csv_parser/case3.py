from typing import List, Iterable, Any

from th2_data_services.data import Data
from th2_data_services.interfaces import IStreamAdapter
from th2_data_services.data_source.lwdp.stub_builder import http_event_stub_builder


class PredictionCsvStreamAdapter(IStreamAdapter):
    def __init__(self, party_column_names: List[str], csv_version='1.0'):
        # party_column_names -- will be handled as str to obj (dict or list)
        self.csv_version = csv_version

    def handle(self, stream: Iterable) -> dict:
        if self.csv_version == '1.0':
            yield from self.handler_1_0(stream)
        else:
            raise Exception('unknown csv file version')

    def handler_1_0(self, stream):
        # Read from TEST_CASE_START to TEST_CASE_END
        # 1st line -- test case start block
        # 2nd line -- header (can be different)
        # last line -- test case end block
        # some actions start from # e.g. #sleep
        # empty lines should be skiped

        yield http_event_stub_builder.build({'eventId': 123})


if __name__ == '__main__':
    data = Data.from_any_file('predictions.csv').map_stream(PredictionCsvStreamAdapter())
    print(data.metadata)
    print(data.len)
    print(data)
