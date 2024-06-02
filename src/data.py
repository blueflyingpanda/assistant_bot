import json


class JSONBackedMapping:

    def __init__(self, filename: str):
        self.filename = filename
        with open(self.filename) as fr:
            self.data: dict = json.load(fr)

    def save(self):
        """Should be called after any modifications in self.data"""
        with open(self.filename, 'w') as fw:
            json.dump(self.data, fw)


backed_data = JSONBackedMapping('data.json')
