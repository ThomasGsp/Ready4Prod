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
from libs.debian9.system import *
from libs.debian9.services import *
from libs.debian9.apache import *
from libs.debian9.maria import  *


class Hitch:

    def __init__(self, confr4p, logger):
        self.conf_root = confr4p["CONF_ROOT"]
        self.exitonerror = confr4p["EXITONERROR"]
        self.logger = logger
        self.transverse = self.transverse(confr4p, logger)
        self.services = self.services(confr4p, logger)


    def conf_hitch(self, VM_C):
        try:
            cpualloc = int(VM_C['CPU'] / 2) + (VM_C['CPU'] % 2 > 0)
            self.transverse.sedvalue("{CPUALLOC}", cpualloc, "/etc/default/varnish")
            run('chown _hitch:_hitch -R /etc/hitch/')
            self.logger.writelog("[OK] Hitch configurations are applied")
        except BaseException as e:
            self.logger.writelog("[ERROR] while Hitch configuration ({error})".format(error=e))
            if self.exitonerror:
                print("Error found: {error}".format(error=e))
                exit(1)

        self.services.management("hitch", "restart")
