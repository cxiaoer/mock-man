# coding=UTF-8
import json


def validate_json(json_data: str) -> bool:
    """
    判断是否是json格式
    """
    try:
        json.loads(json_data)
    except ValueError as err:
        return False
    return True


def json_equals(json1: str, json2: str) -> bool:
    """
    json比较，忽略顺序
    """
    json_obj_1 = json.loads(json1)
    json_obj_2 = json.loads(json2)
    return __ordered(json_obj_1) == __ordered(json_obj_2)


def __ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, __ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(__ordered(x) for x in obj)
    else:
        return obj


def get_cls_props(cls):
    """
    获取某个类所有的属性
    """
    return [i for i in cls.__dict__.keys() if i[:1] != '_']
