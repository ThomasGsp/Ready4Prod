"""
Class : Mysql/MariaDB
Version : 1
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""
import os
from fabric.api import *
from libs.transverse import *
from libs.debian9.services import *


class MariaDB:
    def __init__(self, confr4p, params, logger):
        self.confr4p = confr4p
        self.params = params
        self.Logger = logger
        self.transverse = Transverse(confr4p, params, logger)
        self.services = Services(confr4p, params, logger)

    def conf_init(self):
        try:
            run("mysql -e 'DROP USER ''@'localhost';'")
            run("mysql -e 'DROP USER ''@'$(hostname)';'")
            run("mysql -e 'DROP DATABASE test;'")
            run("mysql -e 'FLUSH PRIVILEGES;'")
            self.logger.writelog("[OK] Mysql clean installation")
        except BaseException as e:
            self.logger.writelog("[ERROR] Mysql execution error ({error})".format(error=e))
            if self.confr4p['EXITONERROR']:
                print("Error found: {error}".format(error=e))
                exit(1)

    def conf_user(self, action, value):
        try:
            if action == "create":
                run('mysql -e "CREATE USER IF NOT EXISTS  \'{username}\'@\'localhost\' IDENTIFIED BY \'{password}\';"'
                    .format(username=value["username"], password=value["password"]))
                self.logger.writelog("[OK] Create user )".format(username=value["username"]))
            elif action == "delete":
                run('mysql -e "DROP USER {username};"'.format(username=value["username"]))
                self.logger.writelog("[OK] DROP user {username})".format(username=value["username"]))
            run('mysql -e "FLUSH PRIVILEGES;"')
            self.logger.writelog("[OK] Apply mysql USERS privileges )".format(username=value["username"]))
        except BaseException as e:
            self.logger.writelog("[ERROR] Mysql execution error ({error})".format(error=e))
            if self.confr4p['EXITONERROR']:
                print("Error found: {error}".format(error=e))
                exit(1)

    def conf_base(self, action, value):
        try:
            if action == "create":
                run('mysql -e "CREATE  DATABASE IF NOT EXISTS  {dbname};"'.format(dbname=value["database"]))
                self.logger.writelog("[OK] Create database: {dbname};".format(dbname=value["database"]))
            elif action == "delete":
                run('mysql -e "DROP  DATABASE  {dbname};"'.format(dbname=value["database"]))
                self.logger.writelog("[OK] DROP database {dbname};".format(dbname=value["database"]))
        except BaseException as e:
            self.logger.writelog("[ERROR] Mysql execution error ({error})".format(error=e))
            if self.confr4p['EXITONERROR']:
                print("Error found: {error}".format(error=e))
                exit(1)
