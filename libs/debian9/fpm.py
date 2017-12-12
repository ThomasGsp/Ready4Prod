"""
Class : php-fpm
Version : 7.0
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""
# Imports
import os
from fabric.api import *
from libs.transverse import *
from libs.debian9.system import *
from libs.debian9.services import *
from libs.debian9.apache import *
from libs.debian9.maria import  *


class Fpm:

    def __init__(self, confr4p, logger):
        self.conf_root = confr4p["CONF_ROOT"]
        self.exitonerror = confr4p["EXITONERROR"]
        self.logger = logger
        self.transverse = self.transverse(confr4p, logger)
        self.services = self.services(confr4p, logger)


    def conf_fpm(self, vm_c):
        ramalloc = int(vm_c['RAM'] / 8)
        if ramalloc > 256:
            ramalloc = 256
        self.transverse.sedvalue("{RAMALLOC}", ramalloc, "/etc/php/7.0/fpm/php.ini")
        self.services.management("php7.0-fpm", "restart")
