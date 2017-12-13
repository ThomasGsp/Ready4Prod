"""
Class : Hitch
Version : 1
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""

# Imports
import os
from fabric.api import *
from libs.transverse import *
from libs.debian9.services import *


class Hitch:

    def __init__(self, confr4p, params, logger):
        self.confr4p = confr4p
        self.params = params
        self.logger = logger
        self.transverse = Transverse(confr4p, params, logger)
        self.services = Services(confr4p, params, logger)

    def conf_hitch(self):
        try:
            cpualloc = int(self.params['HARDWARE']['VM']['CPU'] / 2) + (self.params['HARDWARE']['VM']['CPU'] % 2 > 0)
            self.transverse.sedvalue("{CPUALLOC}", cpualloc, "/etc/hitch/hitch.conf")
            run('chown _hitch:_hitch -R /etc/hitch/')
            self.logger.writelog("[OK] Hitch configurations are applied")
        except BaseException as e:
            self.logger.writelog("[ERROR] while Hitch configuration ({error})".format(error=e))
            if self.confr4p['EXITONERROR']:
                print("Error found: {error}".format(error=e))
                exit(1)

        self.services.management("hitch", "restart")
