# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .common import *

sphinx_conf.listen = "192.168.0.37:9312"
sphinx_conf.var_dir = "C:\\Sphinx"

db_conf.database = "postgres"
db_conf.host = "192.168.0.37"
db_conf.port = 5432
db_conf.user = "postgres"
db_conf.password = "intercon"

unrar_config.path = "C:\\Program Files (x86)\\WinRAR\\unrar.exe"
folders.temp = "E:\\!TEMP"

basic.logging = True
