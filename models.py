# encoding=UTF-8

from peewee import *

# noinspection PyTypeChecker
db: SqliteDatabase = None


# noinspection PyProtectedMember
def init(db_file: str):
    global db
    # db = SqliteDatabase("conf/mock-man.db")
    db = SqliteDatabase(db_file)
    db.connect()
    # 手动管理db属性
    RequestItemsModel._meta.__setattr__("database", db)
    db.create_tables([RequestItemsModel])


class BaseModel(Model):
    class Meta:
        database = db


class RequestItemsModel(BaseModel):
    id = AutoField()  # 自增
    url_path = CharField()
    http_method = CharField()
    req_body = TextField(null=True)
    res_body = TextField()
    match_rules = CharField()

    class Meta:
        table_name = "request_items"

#
# def init_tables():
#     db.create_tables([RequestItemsModel])


# if __name__ == "__main__":
#     init_tables()
#     model = RequestItemsModel()
#     model.match_rules = "hello"
#     model.url_path = "/hello"
#     model.http_method = "POST"
#     model.req_body = "{}"
#     model.res_body = "{}"
#     model.save()
#     items = model.select()
#     model.delete().where(RequestItemsModel.id == 1)
#     for item in items:
#         print(item.req_body)
