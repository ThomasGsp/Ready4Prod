"""
Class : Varnish
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


class Varnish:

    def __init__(self, confr4p, params, logger):
        self.confr4p = confr4p
        self.params = params
        self.logger = logger
        self.transverse = Transverse(confr4p, params, logger)
        self.services = Services(confr4p, params, logger)

    def conf_varnish(self):
        try:
            ramalloc = int(self.params['VM']['RAM'] / 4)
            run('rm /etc/varnish/default.vcl')
            self.logger.writelog("[OK] Clean old varnish configuration")
            run('ln -sf /etc/varnish/production.vcl /etc/varnish/default.vcl')
            self.transverse.sedvalue("{RAMALLOC}", ramalloc, "/etc/default/varnish")
            self.logger.writelog("[OK] Link new varnish configuration")
            run('chown varnish:varnish -R /etc/varnish/')
            self.logger.writelog("[OK] Apply rights on varnish configuration")
            run('systemctl daemon-reload')
            self.logger.writelog("[OK] Update systemd service")
            self.logger.writelog("[OK] Varnish configurations are applied")
            self.services.management("varnish", "restart")
        except BaseException as e:
            self.logger.writelog("[ERROR] while varnish configuration ({error})".format(error=e))
            if self.confr4p['EXITONERROR']:
                print("Error found: {error}".format(error=e))
                exit(1)
