"""
Class : Transversal
Version : 1
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""

from fabric.api import *


class Transverse:

    def __init__(self, confr4p, logger):
        self.conf_root = confr4p["CONF_ROOT"]
        self.exitonerror = confr4p["EXITONERROR"]
        self.Logger = logger

    def sedvalue(self, str_src, str_dest, conf_file):
        try:
            run('sed -i "s/{src_string}/{dest_string}/g" {filedir}'.format(
                src_string=str_src, dest_string=str_dest, filedir=conf_file
            ))
            self.Logger.writelog("[OK] Sed {src_string}, to {dest_string}, in {filedir}".format(
                src_string=str_src, dest_string=str_dest, filedir=conf_file
            ))
        except BaseException as e:
            self.Logger.writelog("[ERROR] Sed {src_string}, to {dest_string}, in {filedir} ({error})".format(
                src_string=str_src, dest_string=str_dest, filedir=conf_file, error=e
            ))
            if self.exitonerror:
                print("Error found: {error}".format(error=e))
                exit(1)

    def copyfiles(self, files_list):
        for file in files_list:
            try:
                put(self.conf_root+file[0], file[1], mode=file[2])
                self.Logger.writelog("[OK] Copy {srcfile}, to {destfile}, with chmod {chmod}".format(
                    srcfile=self.conf_root+file[0], destfile=file[1], chmod=file[2]
                    ))
            except BaseException as e:
                self.Logger.writelog("[ERROR] Copy {srcfile}, to {destfile}, with chmod {chmod} ({error})".format(
                    srcfile=self.conf_root+file[0], destfile=file[1], chmod=file[2], error=e
                    ))
                if self.exitonerror:
                    print("Error found: {error}".format(error=e))
                    exit(1)


class Logs:

    def __init__(self, logfiledir):
        self.logfiles = logfiledir
        self.file = open(self.logfiles, "w")

    def writelog(self, text):
        self.file.write(text+"\n")

    def closefile(self):
        self.file.close()
