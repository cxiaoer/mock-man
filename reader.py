# coding=UTF-8
import json
import logging

from models import RequestItemsModel, init
from request import RequestItem
from tools import get_cls_props

log = logging.getLogger(__name__)


class BaseRequestReader(object):

    def read_requests(self) -> list[RequestItem]:
        """
        加载配置参数列表
        """
        pass

    def add_request(self, reqeust_item: dict) -> None:
        pass

    def remove_request(self) -> None:
        pass


class JsonRequestReader(BaseRequestReader):
    file_path: str

    def __init__(self, file_path: str):
        self.file_path = file_path

    @staticmethod
    def __dic_to_request(x: dict) -> RequestItem:
        req = RequestItem()
        for k in x.keys():
            if not hasattr(req, k):
                continue
            # req.k = x[k]
            setattr(req, k, x[k])
        return req

    # noinspection PyBroadException
    def read_requests(self) -> list[RequestItem]:
        with open(file=self.file_path) as f:
            try:
                json_obj = json.load(f)
                if isinstance(json_obj, list):
                    dic_list = [x for x in json_obj if isinstance(x, dict)]
                    requests: list[RequestItem] = list(map(self.__dic_to_request, dic_list))
                    return requests
            except Exception as ex:
                log.error("读取请求配置json文件出错.", ex)

        return list()

    def add_request(self, reqeust_item: dict) -> None:
        dic_list = []
        with open(file=self.file_path) as f:
            json_obj = json.load(f)
            if isinstance(json_obj, list):
                dic_list = [x for x in json_obj if isinstance(x, dict)]
        for item in dic_list:
            if item['url_path'] == reqeust_item['url_path'] and item['http_method'] == reqeust_item['http_method'] and \
                    item['req_body'] == reqeust_item['req_body'] and item['res_body'] == reqeust_item['res_body'] and \
                    item['match_rules'] == reqeust_item['match_rules']:
                log.info(f"请求配置文件中存在相同的记录，不插入. {reqeust_item}")
                return
        # items.append(reqeust_item)
        dic_list.append(reqeust_item)
        flds = get_cls_props(RequestItem)
        # l_d = []
        with open(file=self.file_path, mode='w') as f:
            # for ob in items:
            #     d = {}
            #     for fld in flds:
            #         d[fld] = ob.__getattribute__(fld)
            #     l_d.append(d)
            s = json.dumps(dic_list)
            f.write(s)


class DbRequestReader(BaseRequestReader):

    def __init__(self, db_file: str):
        init(db_file=db_file)

    def read_requests(self) -> list[RequestItem]:
        models = RequestItemsModel()
        res: list[RequestItem] = []
        try:
            for item in models.select():
                tmp = RequestItem()
                tmp.res_body = item.res_body
                tmp.url_path = item.url_path
                tmp.http_method = item.http_method
                tmp.req_body = item.req_body
                tmp.match_rules = item.match_rules
                res.append(tmp)
        except Exception as ex:
            log.error("从db中读取请求配置列表出错.", ex)
        return res

    def add_request(self, reqeust_item: dict) -> None:
        # 重复记录不插入，url_path+res_body+req_body+match_rules+http_method
        exist: int = RequestItemsModel \
            .select(RequestItemsModel.id) \
            .where(
            (RequestItemsModel.url_path == reqeust_item['url_path']) &
            (RequestItemsModel.http_method == reqeust_item['http_method']) &
            (RequestItemsModel.req_body == reqeust_item['req_body']) &
            (RequestItemsModel.res_body == reqeust_item['res_body']) &
            (RequestItemsModel.match_rules == reqeust_item['match_rules'])) \
            .count()
        if exist > 0:
            log.warn(f"表里存在相同的记录，不插入.")
            return
        item = RequestItemsModel()
        item.url_path = reqeust_item['url_path']
        item.res_body = reqeust_item['res_body']
        item.req_body = reqeust_item['req_body']
        item.http_method = reqeust_item['http_method']
        item.match_rules = reqeust_item['match_rules']
        item.save()
