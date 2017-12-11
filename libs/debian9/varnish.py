"""
Class : Varnish
Version : 1
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""


class Varnish:
    def __init__(self, conf_root):
        self.conf_root = conf_root

    def conf_varnish(self, VM_C):
        try:
            ramalloc = int(VM_C['RAM'] / 4)
            run('rm /etc/varnish/default.vcl')
            Logger.writelog("[OK] Clean old varnish configuration")
            run('ln -sf /etc/varnish/production.vcl /etc/varnish/default.vcl')
            sedvalue("{RAMALLOC}", ramalloc, "/etc/default/varnish")
            Logger.writelog("[OK] Link new varnish configuration")
            run('chown varnish:varnish -R /etc/varnish/')
            Logger.writelog("[OK] Apply rights on varnish configuration")
            run('systemctl daemon-reload')
            Logger.writelog("[OK] Update systemd service")
            Logger.writelog("[OK] Varnish configurations are applied")
            service_gestion("varnish", "restart")
        except BaseException as e:
            Logger.writelog("[ERROR] while varnish configuration ({error})".format(error=e))
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)