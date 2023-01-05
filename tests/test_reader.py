# encoding=UTF-8

import unittest
from reader import BaseRequestReader, DbRequestReader, JsonRequestReader
from request import RequestItem


class TestBaseReader(unittest.TestCase):

    def test_db_read(self):
        db_reader: BaseRequestReader = DbRequestReader("../conf/mock-man.db")
        items = db_reader.read_requests()
        self.assertTrue(len(items) > 0)

    def test_json_reader(self):
        json_path = "../conf/requests.json"
        request_reader = JsonRequestReader(file_path=json_path)
        reqs: list[RequestItem] = request_reader.read_requests()
        self.assertTrue(len(reqs) > 0)

    def test_add_request(self):
        json_path = "../conf/requests.json"
        request_reader = JsonRequestReader(file_path=json_path)
        a = RequestItem()
        a.url_path = '/man'
        a.http_method = 'GET'
        request_reader.add_request(a)
