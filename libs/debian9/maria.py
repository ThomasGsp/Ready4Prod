"""
Class : Mysql/MariaDB
Version : 1
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""


class MariaDB:
    def __init__(self, conf_root):
        self.conf_root = conf_root

    def conf_init(self):
        try:
            run("mysql -e 'DROP USER ''@'localhost';'")
            run("mysql -e 'DROP USER ''@'$(hostname)';'")
            run("mysql -e 'DROP DATABASE test;'")
            run("mysql -e 'FLUSH PRIVILEGES;'")
            Logger.writelog("[OK] Mysql clean installation")
        except BaseException as e:
            Logger.writelog("[ERROR] Mysql execution error ({error})".format(error=e))
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)


    def conf_user(self, action, value):
        try:
            if action == "create":
                run('mysql -e "CREATE USER IF NOT EXISTS  \'{username}\'@\'localhost\' IDENTIFIED BY \'{password}\';"'
                    .format(username=value["username"], password=value["password"]))
                Logger.writelog("[OK] Create user )".format(username=value["username"]))
            elif action == "delete":
                run('mysql -e "DROP USER {username};"'.format(username=value["username"]))
                Logger.writelog("[OK] DROP user {username})".format(username=value["username"]))
            run('mysql -e "FLUSH PRIVILEGES;"')
            Logger.writelog("[OK] Apply mysql USERS privileges )".format(username=value["username"]))
        except BaseException as e:
            Logger.writelog("[ERROR] Mysql execution error ({error})".format(error=e))
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)


    def conf_base(self, action, value):
        try:
            if action == "create":
                run('mysql -e "CREATE  DATABASE IF NOT EXISTS  {dbname};"'.format(dbname=value["database"]))
                Logger.writelog("[OK] Create database: {dbname};".format(dbname=value["database"]))
            elif action == "delete":
                run('mysql -e "DROP  DATABASE  {dbname};"'.format(dbname=value["database"]))
                Logger.writelog("[OK] DROP database {dbname};".format(dbname=value["database"]))
        except BaseException as e:
            Logger.writelog("[ERROR] Mysql execution error ({error})".format(error=e))
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)