# coding=UTF-8
import json

from pydantic import BaseModel, validator

from tools import validate_json


class RequestParam(object):
    url_path: str
    http_method: str
    http_body: str

    def __str__(self):
        """
        类似java的toString
        """
        return f"url_path:{self.url_path},http_method:{self.http_method},req_body:{self.http_body}"


class RequestItem(object):

    def __init__(self):
        self.__match_rules = None
        self.__res_body = None
        self.__http_method = None
        self.__req_body = None
        self.__url_path = None

    @property
    def url_path(self):
        return self.__url_path

    @url_path.setter
    def url_path(self, value):
        self.__url_path = value

    @property
    def req_body(self):
        return self.__req_body

    @req_body.setter
    def req_body(self, value):
        self.__req_body = value

    @property
    def http_method(self):
        return self.__http_method

    @http_method.setter
    def http_method(self, value):
        self.__http_method = value

    @property
    def res_body(self):
        if self.__res_body is None:
            return self.__res_body
        if not validate_json(self.__res_body):
            return self.__res_body
        return json.loads(self.__res_body)

    @res_body.setter
    def res_body(self, value):
        self.__res_body = value

    @property
    def match_rules(self):
        return self.__match_rules

    @match_rules.setter
    def match_rules(self, value):
        self.__match_rules = value

    def __str__(self):
        return f"url_path:{self.__url_path},http_method:{self.__http_method},req_body:{self.__req_body}," \
               f"res_body:{self.__res_body},match_rules:{self.__match_rules} "

    # def get_res_body(self):
    #     if self.res_body is None:
    #         return self.res_body
    #     if not validate_json(self.res_body):
    #         return self.res_body
    #     return json.loads(self.res_body)

    # def __getitem__(self, item):
    #     if self.__getattribute__(item):
    #         return False
    #     return True


# noinspection PyMethodParameters
class AddRequestItemParam(BaseModel):
    url_path: str
    http_method: str
    req_body: str
    res_body: str
    match_method: str
    match_rules: str

    # @validator("http_method")
    # def http_method_notblank(cls, v):
    #     if v is None:
    #         raise ValueError("the http_method can't be empty.")
    #     return v

    @validator("url_path")
    def url_path_notblank(cls, v):
        if v is None or len(str.strip(v)) == 0:
            raise ValueError("the url_path can't be empty.")
        return v

    @validator("req_body")
    def req_body_notblank(cls, v):
        if v is None or len(str.strip(v)) == 0:
            raise ValueError("the req_body can't be empty.")
        return v

    @validator("res_body")
    def res_body_notblank(cls, v):
        if v is None or len(str.strip(v)) == 0:
            raise ValueError("the res_body can't be empty.")
        return v

    @validator("match_rules")
    def match_rules_valid(cls, v, values, **kwargs):
        match_method = values["match_method"]
        if match_method == "CUSTOM" and (v is None or len(str.strip(v)) == 0):
            raise ValueError("the match_rules can't be empty if the match_method equals CUSTOM")
        return v
