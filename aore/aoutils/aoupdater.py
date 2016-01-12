# -*- coding: utf-8 -*-

from aore.aoutils.aodataparser import AoDataParser
from aore.aoutils.aorar import AoRar
from aore.aoutils.aoxmltableentry import AoXmlTableEntry
from aore.dbutils.dbhandler import DbHandler
from aore.dbutils.dbschemas import allowed_tables
from aore.aoutils.importer import Importer
from os import walk, path
import logging

class AoUpdater:
    # Source: "http", directory (as a full path to unpacked xmls)
    def __init__(self, source="http"):
        logging.basicConfig(format='%(asctime)s %(message)s')
        self.db_handler = DbHandler()
        self.mode = source
        self.updalist_generator = None
        self.allowed_tables = None

    def __get_entries_from_folder(self, path_to_xmls):
        for (dirpath, dirnames, filenames) in walk(path_to_xmls):
            for filename in filenames:
                if filename.endswith(".XML"):
                    xmltable = AoXmlTableEntry.from_dir(filename, dirpath.replace("\\", "/") + "/")
                    if xmltable.table_name in allowed_tables:
                        yield xmltable
            break

    def __get_updates_from_folder(self, foldername):
        # TODO: Вычислять версию, если берем данные из каталога
        yield dict(intver=0, textver="Unknown", url=foldername)

    def __init_update_entries(self, full_base):
        if self.mode == "http":
            imp = Importer()
            self.updalist_generator = None
            if full_base:
                self.updalist_generator = imp.get_full()
            else:
                self.updalist_generator = imp.get_updates()
        else:
            assert path.isdir(self.mode), "Invalid directory {}".format(self.mode)
            self.updalist_generator = self.__get_updates_from_folder(self.mode)

    def process_single_entry(self, table_xmlentry, chunck_size=50000):
        aoparser = AoDataParser(table_xmlentry, chunck_size)
        aoparser.parse(lambda x: self.db_handler.bulk_csv(chunck_size, table_xmlentry.table_name, x))

    def create(self):
        self.__init_update_entries(True)
        self.db_handler.pre_create()

        for update_entry in self.updalist_generator:
            for table_entry in self.__get_entries_from_folder(update_entry['url']):
                self.process_single_entry(table_entry)

        logging.warning("Create success")

    def update(self, count=1):
        self.__init_update_entries(False)
        self.db_handler.pre_update()

        counter = 0
        for update_entry in self.updalist_generator:
            counter += 1
            if counter > count:
                logging.warning("Maximum count of updates are processed - exit")
                break

            aorar = AoRar()
            fname = aorar.download(update_entry['url'])
            for table_entry in aorar.get_table_entries(fname, allowed_tables):
                self.process_single_entry(table_entry)

        logging.warning("Update success")
