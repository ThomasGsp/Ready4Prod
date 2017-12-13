"""
Class : Services
Version : 1
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""

from fabric.api import *


class Services:

    def __init__(self, confr4p, params, logger):
        self.confr4p = confr4p
        self.logger = logger

    def management(self, service, action):
        try:
            run("systemctl {actiontype} {servicename}".format(actiontype=action, servicename=service))
        except BaseException as e:
            self.logger.writelog("[ERROR] action {actiontype}, on service {servicename} ({error})".format(
                actiontype=action, servicename=service, error=e
                )
            )
            if self.confr4p['EXITONERROR']:
                print("Error found: {error}".format(error=e))
                exit(1)
