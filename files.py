# coding=UTF-8
import os
import logging
from datetime import datetime

log = logging.getLogger(__name__)


class Watch(object):
    file_name: str
    file_stat_time: float

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.file_stat_time = 0

    # noinspection PyUnusedLocal,SpellCheckingInspection
    def watch(self) -> bool:
        tmp_stat_time: float = os.stat(self.file_name).st_mtime
        if tmp_stat_time != self.file_stat_time:
            self.file_stat_time = tmp_stat_time
            str_lastmodify_time = datetime.fromtimestamp(self.file_stat_time) \
                .strftime("%Y-%m-%d %H:%M:%S")
            log.info(f"{self.file_name} 发生了变更，变更时间:{str_lastmodify_time}")
            return True
        return False
