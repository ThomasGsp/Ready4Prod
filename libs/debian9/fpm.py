"""
Class : php-fpm
Version : 7.0
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""


class Fpm:
    def __init__(self, conf_root):
        self.conf_root = conf_root

    def conf_fpm(self, vm_c):
        ramalloc = int(vm_c['RAM'] / 8)
        if ramalloc > 256:
            ramalloc = 256
        sedvalue("{RAMALLOC}", ramalloc, "/etc/php/7.0/fpm/php.ini")
        service_gestion("php7.0-fpm", "restart")
