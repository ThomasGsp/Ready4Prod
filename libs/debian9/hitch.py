"""
Class : Hitch
Version : 1
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""


class Hitch:
    def __init__(self, conf_root):
        self.conf_root = conf_root

    def conf_hitch(self, VM_C):
        try:
            cpualloc = int(VM_C['CPU'] / 2) + (VM_C['CPU'] % 2 > 0)
            sedvalue("{CPUALLOC}", cpualloc, "/etc/default/varnish")
            run('chown _hitch:_hitch -R /etc/hitch/')
            Logger.writelog("[OK] Hitch configurations are applied")
        except BaseException as e:
            Logger.writelog("[ERROR] while Hitch configuration ({error})".format(error=e))
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)

        service_gestion("hitch", "restart")
