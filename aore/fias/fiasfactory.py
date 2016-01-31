# -*- coding: utf-8 -*-
import psycopg2
from bottle import template

from aore.dbutils.dbimpl import DBImpl
from aore.fias.search import SphinxSearch
from aore.config import db_conf
from uuid import UUID
import re


class FiasFactory:
    def __init__(self):
        self.db = DBImpl(psycopg2, db_conf)
        self.searcher = SphinxSearch(self.db)
        self.expand_templ = template('aore/templates/postgre/expand_query.sql', aoid="//aoid")
        self.normalize_templ = template('aore/templates/postgre/normalize_query.sql', aoid="//aoid")

    # Проверка, что строка является действительым UUID v4
    def __check_uuid(self, guid):
        try:
            UUID(guid)
        except ValueError:
            return False

        return True

    # Проверяет входящий параметр на соотвествие
    # param - сам параметр
    # rule - "boolean", "uuid", "text"
    def __check_param(self, param, rule):
        if rule == "boolean":
            assert type(param) is bool, "Invalid parameter type"
        if rule == "uuid":
            assert (type(param) is str or type(param) is unicode) and self.__check_uuid(param), "Invalid parameter value"
        if rule == "text":
            assert type(param) is str or type(param) is unicode, "Invalid parameter type"
            assert len(param) > 3, "Text too short"
            pattern = re.compile("[A-za-zА-Яа-я \-,.#№]+")
            assert pattern.match(param), "Invalid parameter value"

    # text - строка поиска
    # strong - строгий поиск (True) или "мягкий" (False) (с допущением ошибок, опечаток)
    # Строгий используется при импорте из внешних систем (автоматически), где ошибка критична
    def find(self, text, strong=False):
        try:
            self.__check_param(text, "text")
            self.__check_param(strong, "boolean")

            results = self.searcher.find(text, strong)
        except Exception, err:
            return dict(error=err.message)

        return results

    # Нормализует подаваемый AOID или AOGUID в актуальный AOID
    def normalize(self, aoid_guid):
        try:
            self.__check_param(aoid_guid, "uuid")

            sql_query = self.normalize_templ.replace("//aoid", aoid_guid)
            rows = self.db.get_rows(sql_query, True)
        except Exception, err:
            return dict(error=err.message)

        if len(rows) == 0:
            return []
        else:
            return rows[0]

    # Разворачивает AOID в представление (перед этим нормализует)
    def expand(self, aoid_guid):
        try:
            self.__check_param(aoid_guid, "uuid")

            normalized_id = self.normalize(aoid_guid)
            assert 'aoid' in normalized_id, "AOID or AOGUID not found in DB"
            normalized_id = normalized_id['aoid']

            sql_query = self.expand_templ.replace("//aoid", normalized_id)
            rows = self.db.get_rows(sql_query, True)
        except Exception, err:
            return dict(error=err.message)

        return rows