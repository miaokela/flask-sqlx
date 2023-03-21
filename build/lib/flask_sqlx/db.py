import copy
import re

import typing
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.sql import compiler, text
from sqlalchemy import text

from flask_sqlx.exceptions import (
    SQLFormatError,
    SQLExecuteError
)
from flask_sqlx.sql_loader import sql_loader


SHOW_SQL = False


class DBData(dict):
    """
    Set data or get data with point and bracket.
    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"Query object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


class DataBaseHelper:
    db = None

    @classmethod
    def get_params_without_paginated(cls, params: typing.Dict):
        if not params:
            return {}
        params_cp = copy.deepcopy(params)
        if 'pageNum' in params:
            del params_cp['pageNum']
        if 'pageSize' in params:
            del params_cp['pageSize']
        return params_cp

    @classmethod
    def set_where_phrase(cls, sql, where):
        """
        生成where语句
        """
        if not where:
            return sql
        where_str = " WHERE "
        for key in where.keys():
            where_str += key + " = :" + "_where_%s" % key + " and "
        where_str = where_str[0:-5]
        sql += where_str
        return sql

    @classmethod
    def fullfilled_data(cls, data, where):
        """
        删除/更新操作,对传入的data 在where条件中的字段都新增一个 _where_${field} 字段,用于where条件的赋值
        """
        if not where:
            return data
        
        for k, v in where.items():
            if k.startswith("_where_"):
                raise SQLFormatError("where条件中不能包含 _where_ 开头的字段")
            data.update(**{
                "_where_%s" % k: v
            })

        return data

    # 需求:更新 插入 删除 不需要编写sql 传入表名、数据、条件即可
    @classmethod
    def execute_update(cls, tb_name, data, where, app=None, bind=None):
        """
        更新数据
            UPDATE可能存在的问题:where与data字段名称相同,值不相同的问题
            处理:            
            删除/更新操作,对传入的data 在where条件中的字段都新增一个 _where_${field} 字段,用于where条件的赋值,
            where条件的value通过这个方式转化::field => :_where_${field}

            where就是where data就是data 处理时 对转化后的where 更新到data里 data.update(**where)
        :param tb_name: 表名
        :param data: 数据
        :param where: 过滤条件
        :return: 更新数量
        """
        sql = "UPDATE " + tb_name + " SET "
        for key in data.keys():
            sql += key + " = :" + key + ","
        sql = sql[0:-1]

        data = cls.fullfilled_data(data, where)
        sql = cls.set_where_phrase(sql, where)
        try:
            if app and bind:
                bind = cls.db.get_engine(app, bind=bind)
                result = cls.db.session.execute(text(sql), data, bind=bind)
            else:
                result = cls.db.session.execute(text(sql), data)
            return result.rowcount
        except SQLExecuteError as e:
            print("execute sql: < %s %s > failed! Readon: %s" % (sql, str(data), str(e)))
            return None

    @classmethod
    def allow_sharp(cls):
        """
        允许使用#号出现在字段名称中
        """
        compiler.BIND_PARAMS = re.compile(r"(?<![:\w\$\x5c]):([\w\$\#]+)(?![:\w\$])", re.UNICODE)
        TextClause._bind_params_regex = re.compile(r'(?<![:\\w\\x5c]):([\w\#]+)(?!:)', re.UNICODE)

    @classmethod
    def execute_create(cls, tb_name, data, app=None, bind=None):
        """
        插入数据
        :param tb_name: 表名
        :param data: 数据
        :return: 插入数据的id
        """
        # cls.allow_sharp()
        sql = "INSERT INTO " + tb_name + " ("
        for key in data.keys():
            sql += "`%s`" % key + ","
        sql = sql[0:-1]
        sql += ") VALUES ("
        for key in data.keys():
            sql += ":" + key + ","
        sql = sql[0:-1]
        sql += ")"
        try:
            if app and bind:
                bind = cls.db.get_engine(app, bind=bind)
                result = cls.db.session.execute(text(sql), data, bind=bind)
            else:
                result = cls.db.session.execute(text(sql), data)
            return result.lastrowid
        except SQLExecuteError as e:
            print("execute sql: < %s %s > failed! Reason: %s" % (sql, str(data), str(e)))
            return None

    @classmethod
    def execute_delete(cls, tb_name, where, logic=False, app=None, bind=None):
        """
        删除数据
        :param tb_name: 表名
        :param where: 过滤条件
        :return: 删除数量
        """
        sql = "DELETE FROM " + tb_name
        if logic:
            sql = "UPDATE %s SET delete_flag=1" % tb_name
        sql = cls.set_where_phrase(sql, where)
        where = cls.fullfilled_data({}, where)

        try:
            if app and bind:
                bind = cls.db.get_engine(app, bind=bind)
                result = cls.db.session.execute(text(sql), where, bind=bind)
            else:
                result = cls.db.session.execute(text(sql), where)
            return result.rowcount
        except SQLExecuteError as e:
            print("执行sql: < %s %s > 失败！ 原因: %s" % (sql, str(where), str(e)))
            return None

    @classmethod
    def execute_sql(cls, sql_id, params=None, options: typing.Dict[str, str] = None, app=None, bind=None):
        """
        动态sql通用方法
        :param sql_id:
        :param params: 查询条件
        :param options: 动态sql条件
        :return:
        """
        preloaded_sql = sql_loader.preload_sql(sql_id, options=options)
        try:
            # 支持多数据库|指定数据库执行sql
            if app and bind:
                bind = cls.db.get_engine(app, bind=bind)
                result = cls.db.session.execute(text(preloaded_sql), params, bind=bind).fetchall()
            else:
                # print('execute <%s>, params: %s' % (sql_id, str(params)))
                result = cls.db.session.execute(text(preloaded_sql), params).fetchall()
        except SQLExecuteError as e:
            print("执行sql: %s %s 失败！ 原因:%s" % (preloaded_sql, str(params), str(e)))
            return []
        if SHOW_SQL:
            print("当前执行的sql: %s %s" % (preloaded_sql, str(params)))
        return [DBData(zip(item.keys(), item)) for item in result]

    @classmethod
    def select_one(cls, sql_id, params=None, options: typing.Dict[str, str] = None, app=None, bind=None):
        options = cls.get_params_without_paginated(options)  # 不需要分页
        result = cls.execute_sql(sql_id, params, options, app=app, bind=bind)
        return DBData(result[0] if result else {})

    @classmethod
    def select_all(cls, sql_id, params=None, options: typing.Dict[str, typing.Union[str, int, None]] = None, app=None, bind=None):
        return cls.execute_sql(sql_id, params, options, app=app, bind=bind)

    @classmethod
    def commit(cls):
        cls.db.session.commit()

    @classmethod
    def rollback(cls):
        cls.db.session.rollback()

    @classmethod
    def close(cls):
        cls.db.session.close()
