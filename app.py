# coding=UTF-8
import argparse
import logging.config
import sched
import threading
import time

import uvicorn
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from files import Watch
from reader import JsonRequestReader, BaseRequestReader, DbRequestReader
from request import RequestParam, RequestItem, AddRequestItemParam
from request_matcher import BaseRequestMatcher, DefaultRequestMatcher

logging.config.fileConfig('logging.conf')
log = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
req_items: list[RequestItem] = []
file_reader: BaseRequestReader
scheduled = sched.scheduler(timefunc=time.time, delayfunc=time.sleep)
req_matcher: BaseRequestMatcher = DefaultRequestMatcher()

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, default=8000, help='启动端口号，默认8000')
parser.add_argument('-j', '--json', type=str, help='请求配置文件，默认json格式')
parser.add_argument('-d', '--db', type=str, help='请求数据库位置,目前支持本地sqlite')
args = parser.parse_args()


def load_req_items(file_watcher: Watch):
    global req_items
    if file_watcher is not None and file_watcher.watch() and isinstance(file_reader, JsonRequestReader):
        req_items = file_reader.read_requests()
    else:
        req_items = file_reader.read_requests()
    scheduled.enter(10, 0, load_req_items, (file_watcher,))


# noinspection PyTypeChecker
def run_load_req_items(file_path1: str, data_file: str):
    global file_reader
    file_watcher: Watch = None
    if file_path1 is not None:
        log.info(f"使用json格式的请求配置文件. {file_path1}")
        file_reader = JsonRequestReader(file_path=file_path1)
        file_watcher = Watch(file_path1)
    else:
        log.info(f"使用db管理请求配置文件. {db_file}")
        file_reader = DbRequestReader(db_file=data_file)
    scheduled.enter(0, 0, load_req_items, (file_watcher,))
    # scheduled.run(blocking=True)
    scheduled.run()


def match_request_param(req_param: RequestParam) -> RequestItem:
    matched_req_item = req_matcher.request_match(req_param=req_param, requests=req_items)
    if matched_req_item is None:
        log.error(f"请求参数:{req_param} 无法匹配请求参数，请求失败.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="request not found")
    log.info(f"匹配到的请求如下: {matched_req_item}")
    return matched_req_item


# noinspection PyUnboundLocalVariable
@app.get("/ui", response_class=HTMLResponse)
async def ui(request: Request):
    """
    ui配置管理页面
    """
    # 获取所有的请求配置
    # print(await request.form())
    data_dict = {}
    for key in request.query_params.keys():
        data_dict[key] = request.query_params[key]
    if len(data_dict.keys()) > 0:
        try:
            add_param = AddRequestItemParam(**data_dict)
            r = {'url_path': add_param.url_path, 'http_method': add_param.http_method, 'req_body': add_param.req_body,
                 'res_body': add_param.res_body, 'match_rules': add_param.match_method
                if add_param.match_method == 'ALL' or add_param.match_method == 'ANY' else add_param.match_rules}
            file_reader.add_request(r)
            global req_items
            req_items = file_reader.read_requests()
        except ValidationError as e:
            log.error(f"参数校验失败.{e}")
    # 清空query params参数
    # todo 跳转清空原先输入的参数？？？
    return templates.TemplateResponse("app.html", {
        "request": request,
        "req_items": req_items
    })


# 历史版本中，使用api.route来捕获所有的url path,新版本中改成api.api_route
@app.api_route("/{full_path:path}", methods=["GET", "POST"], response_class=JSONResponse)
async def catch_all(request: Request, full_path: str):
    """
    全局的JSON接口捕获入口
    """
    body = str(await request.body(), encoding="utf-8")
    req_param = RequestParam()
    req_param.url_path = f"/{full_path}"
    req_param.http_method = request.method
    req_param.http_body = body
    matched_req_item: RequestItem = match_request_param(req_param)
    return matched_req_item.res_body


if __name__ == '__main__':
    # 读取请求列表配置
    file_path = args.json
    db_file = "conf/mock-man.db"
    if file_path is None and db_file is None:
        file_path = "conf/requests.json"
    thread: threading.Thread = threading.Thread(target=run_load_req_items, args=(file_path, db_file))
    thread.daemon = True
    thread.start()

    # todo 开启reload 会导致无法进行pycharm debug功能
    # uvicorn.run("app:app", reload=True)
    uvicorn.run(app, port=args.port)
