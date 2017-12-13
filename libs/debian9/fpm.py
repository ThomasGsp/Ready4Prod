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
from libs.debian9.services import *


class Fpm:

    def __init__(self, confr4p, params, logger):
        self.confr4p = confr4p
        self.params = params
        self.logger = logger
        self.transverse = Transverse(confr4p, params, logger)
        self.services = Services(confr4p, params, logger)

    def conf_fpm(self):
        ramalloc = int(self.params['VM']['RAM'] / 8)
        if ramalloc > 256:
            ramalloc = 256
        self.transverse.sedvalue("{RAMALLOC}", ramalloc, "/etc/php/7.0/fpm/php.ini")
        self.services.management("php7.0-fpm", "restart")
