"""
Class : Services
Version : 1
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""


class Services:
    def __init__(self, conf_root):
        self.conf_root = conf_root


    def management(self, service, action):
        try:
            run("systemctl {actiontype} {servicename}"
                .format(actiontype=action, servicename=service)
            )
        except BaseException as e:
            Logger.writelog("[ERROR] action {actiontype}, on service {servicename} ({error})".format(
                actiontype=action, servicename=service, error=e
                )
            )
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)