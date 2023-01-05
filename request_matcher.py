# coding=UTF-8
import json
import logging

from constants import *
from request import RequestParam, RequestItem
from tools import validate_json, json_equals
from frozen_json import FrozenJSON
from antpm import AntPathMatcher

# import json
log = logging.getLogger(__name__)


class BaseRequestMatcher(object):

    def request_match(self, req_param: RequestParam, requests: list[RequestItem]):
        pass


class DefaultRequestMatcher(BaseRequestMatcher):

    def __init__(self):
        self.ant_url_matcher: AntPathMatcher = AntPathMatcher()

    # noinspection PyTypeChecker
    def request_match(self, req_param: RequestParam, requests: list[RequestItem]) -> RequestItem:
        url_path: str = req_param.url_path
        http_method: str = req_param.http_method
        req_body_json: str = req_param.http_body
        if requests is None or len(requests) == 0:
            log.info("配置的请求列表为空")
            return None

        def __url_equals(req: RequestItem):
            """
            url支持ant path风格
            """
            return self.ant_url_matcher.match(pattern=req.url_path, path=url_path)

        def __http_method_equals(req: RequestItem):
            return http_method.lstrip() == req.http_method.lstrip()

        # noinspection PyBroadException
        def __req_body_equals(req: RequestItem):
            """
            目前只支持json格式报文
            """
            # ANY-> 任意REQ_BODY匹配成功
            match_rules: str = req.match_rules
            if match_rules == MATCH_ANY:
                return True
            if match_rules == MATCH_ALL or match_rules is None:
                if not validate_json(req_body_json) or not validate_json(req.req_body):
                    log.info("请求不是json格式，将直接使用字符串相等来匹配")
                    return req_body_json.lstrip() == req.req_body.lstrip()
                return json_equals(req_body_json, req.req_body)
            # eval 表达式: global 变量
            if match_rules is not None and validate_json(req_body_json):
                # 有可能是dict,有可能是list
                req_obj = json.loads(req_body_json)
                # 转换成可以用.访问的对象
                f = FrozenJSON(req_obj)
                # 定义一个req全局对象
                try:
                    if eval(match_rules, {"req": f}):
                        return True
                except Exception as ex:
                    log.error(f"使用规则={match_rules} 匹配出错，错误信息:{ex}")
                    return False
            return False

        # 首先url 完全匹配
        u_list: list[RequestItem] = list(filter(__url_equals, requests))
        h_list: list[RequestItem] = list(filter(__http_method_equals, u_list))
        r_list: list[RequestItem] = list(filter(__req_body_equals, h_list))
        if r_list is None or len(r_list) == 0:
            log.error("未匹配到任何请求配置.")
            return None
        return h_list[0]
