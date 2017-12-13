"""
Class : self.apache
Version : 2.4
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""

import os
from fabric.api import *
from libs.transverse import *
from libs.debian9.system import *
from libs.debian9.services import *
from libs.debian9.maria import  *


class Apache:

    def __init__(self, confr4p, params, logger):
        self.confr4p = confr4p
        self.params = params
        self.logger = logger
        self.transverse = Transverse(confr4p, params, logger)
        self.services = Services(confr4p, params, logger)

    def conf_general(self, apachelisten):
        # No try necessary here
        self.transverse.sedvalue("{SERVERNAME}", self.params['CONF']['HOSTNAME'], "/etc/apache2/apache2.conf")
        self.logger.writelog("[OK] Set hostname in apache configuration")
        self.transverse.sedvalue("{APACHE_LISTEN}", apachelisten, "/etc/apache2/ports.conf")
        self.logger.writelog("[OK] Set ports in apache configuration")
        self.transverse.sedvalue("{APACHE_LISTEN}", apachelisten, "/etc/apache2/sites-available/000-default.conf")
        self.logger.writelog("[OK] Set interface in apache default")
        Apache.conf_management(self, ["security.conf", "badbot.conf"])
        Apache.mod_management(self, ["headers"])
        self.services.management("apache2", "restart")

    def conf_php(self):
        ramalloc = int(self.params['VM']['RAM'] / 8)
        if ramalloc > 256:
            ramalloc = 256
        self.transverse.sedvalue("{RAMALLOC}", ramalloc, "/etc/php/7.0/apache2/php.ini")
        self.logger.writelog("[OK] configure php for apache2")
        self.services.management("apache2", "restart")

    def mod_management(self, modslist):
        for mod in modslist:
            try:
                run("a2enmod {modname}".format(modname=mod))
                self.logger.writelog("[OK] Activate apache module {modname}".format(modname=mod))
            except BaseException as e:
                self.logger.writelog("[ERROR]  Activate apache module {modname} ({error})".format(
                    modname=mod, error=e
                    )
                )
                if self.confr4p['EXITONERROR']:
                    print("Error found: {error}".format(error=e))
                    exit(1)

    def conf_management(self, conflist):
        for conf in conflist:
            try:
                run("a2enconf {confname}".format(confname=conf))
                self.logger.writelog("[OK] Activate apache configuration {confname}".format(confname=conf))
            except BaseException as e:
                self.logger.writelog("[ERROR]  Activate apache configuration {confname} ({error})".format(
                    confname=conf, error=e
                    )
                )
                if self.confr4p['EXITONERROR']:
                    print("Error found: {error}".format(error=e))
                    exit(1)

    def site_management(self, sitelist):
        for site in sitelist:
            try:
                run("a2ensite {sitename}".format(sitename=site))
                self.logger.writelog("[OK] Activate apache web site {sitename}".format(sitename=site))
            except BaseException as e:
                self.logger.writelog("[ERROR]  Activate apache web site {sitename} ({error})".format(
                    sitename=site, error=e
                    )
                )
                if self.confr4p['EXITONERROR']:
                    print("Error found: {error}".format(error=e))
                    exit(1)

    def conf_vhost(self, apachelisten):
        for VHOST in self.params['CONF']['VHOSTS']:
            try:
                run('mkdir -p /var/www/{servername}/prod/'.format(servername=VHOST["SERVER_NAME"]))
                self.logger.writelog("[OK] Create file dir for new vhost {servername}".format(servername=VHOST["SERVER_NAME"]))
                run('mkdir -p /var/log/apache2/{servername}/'.format(servername=VHOST["SERVER_NAME"]))
                self.logger.writelog("[OK] Create logs dir for new vhost {servername}".format(servername=VHOST["SERVER_NAME"]))

                self.transverse.copyfiles([
                    ['/conf/APACHE/2.4/sites-available/{filedir}/010-mywebsite.com.conf'.format(filedir=self.confr4p["FILEDIR"]),
                     '/etc/apache2/sites-available/010.{servername}.conf'
                          .format(servername=VHOST["SERVER_NAME"]), '0640']
                ])

                self.transverse.sedvalue("{domain_name}", VHOST["SERVER_NAME"], "/etc/apache2/sites-available/010.{servername}.conf"
                         .format(servername=VHOST["SERVER_NAME"]))
                self.transverse.sedvalue("{domain_name_alias}", ''.join(VHOST["SERVER_NAME_ALIAS"]),
                         "/etc/apache2/sites-available/010.{servername}.conf"
                         .format(servername=VHOST["SERVER_NAME"]))
                self.transverse.sedvalue("{APACHE_LISTEN}", apachelisten, "/etc/apache2/sites-available/010.{servername}.conf"
                         .format(servername=VHOST["SERVER_NAME"]))
                self.logger.writelog("[OK] Push new vhost and files for {servername}".format(servername=VHOST["SERVER_NAME"]))

                if VHOST["FILES"]:
                    filename, file_extension = os.path.splitext(self.confr4p["CONF_ROOT"] + VHOST["FILES"])
                    sitedir = "/var/www/{servername}/prod/".format(servername=VHOST["SERVER_NAME"])

                    # Delete currents files
                    run("rm -rf {sitedir}*".format(sitedir=sitedir))

                    if file_extension:
                        self.transverse.copyfiles([
                            ['{files}'.format(files=VHOST["FILES"]), '/var/www/{servername}/prod/site_tmp{fileexten}'
                                  .format(servername=VHOST["SERVER_NAME"], fileexten=file_extension), '0640']
                        ])
                        sitefile = "/var/www/{servername}/prod/site_tmp{fileexten}".format(servername=VHOST["SERVER_NAME"],
                                                                                          fileexten=file_extension)
                        if file_extension == ".zip":
                            run("unzip {0} -d {1}".format(sitefile, sitedir))
                            run("rm {0}".format(sitefile))
                        elif file_extension == ".tar":
                            run("tar -xvf  {0} {1}".format(sitefile, sitedir))
                            run("rm {0}".format(sitefile))
                        elif file_extension == ".tar.gz":
                            run("tar -xzvf  {0} {1}".format(sitefile, sitedir))
                            run("rm {0}".format(sitefile))
                        elif file_extension == ".tar.bz2":
                            run("tar -xjvf  {0} {1}".format(sitefile, sitedir))
                            run("rm {0}".format(sitefile))
                        else:
                            self.logger.writelog(
                                "[ERROR] File format not supported {0} {1}".format(sitefile, sitedir))
                    else:
                        put(self.confr4p["CONF_ROOT"] + VHOST["FILES"], sitedir)

                run('chown 33:33 -R /var/www/{servername}'.format(servername=VHOST["SERVER_NAME"]))
                run('find /var/www/{servername} -type d -exec chmod 750 -v {{}} \;'.format(servername=VHOST["SERVER_NAME"]))
                run('find /var/www/{servername} -type f -exec chmod 640 -v {{}} \;'.format(servername=VHOST["SERVER_NAME"]))
                self.logger.writelog("[OK] Set chmod / chown for {servername}".format(servername=VHOST["SERVER_NAME"]))

                Apache.site_management(self, ["010.{servername}.conf".format(servername=VHOST["SERVER_NAME"])])
                self.logger.writelog("[OK] Active vhost {servername}".format(servername=VHOST["SERVER_NAME"]))

            except BaseException as e:
                self.logger.writelog("[ERROR] while apache vhost configuration ({error})".format(error=e))
                if self.confr4p['EXITONERROR']:
                    print("Error found: {error}".format(error=e))
                    exit(1)
