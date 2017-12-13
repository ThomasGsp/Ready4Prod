"""
Class : Main Process
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
from libs.debian9.maria import *
from libs.debian9.hitch import *
from libs.debian9.fpm import *
from libs.debian9.varnish import *


def process(confr4p, params, logger):

    transverse = Transverse(confr4p, params, logger)
    system = System(confr4p, params, logger)
    apache = Apache(confr4p, params, logger)
    services = Services(confr4p, params, logger)
    mariadb = MariaDB(confr4p, params, logger)


    if "MOTD" in params['SOFTS']['BASE']:
        system.conf_dynmotd()

    files_list = [
        ['/conf/SYSTEM/sources.list', '/etc/apt/sources.list', '0640'],
        ['/conf/SYSTEM/cpb.bash', '/usr/local/bin/cpb', '0755'],
        ['/conf/SYSTEM/bash_profile', '/root/.bash_profile', '0640'],
        ['/conf/SYSTEM/motd.bash', '/etc/update-motd.d/10-sysinfo', '0755'],
    ]

    if "USERBASHRC" in params['SOFTS']['BASE']:
        files_list.append(['/conf/SYSTEM/bashrc', '/root/.bashrc', '0640'])

    if "SSH" in params['SOFTS']['BASE']:
        files_list.append(['/conf/SYSTEM/sshd_config', '/etc/ssh/sshd_config', '0640'])

    if "FW" in params['SOFTS']['BASE']:
        files_list.append(['/conf/SYSTEM/firewall.sh', '/etc/init.d/firewall', '0740'])

    if "VIM" in params['SOFTS']['BASE']:
        files_list.append(['/conf/SYSTEM/defaults.vim', '/usr/share/vim/vim80/defaults.vim', '0644'])

    transverse.copyfiles(files_list)

    # Firewall
    if "FW" in params['SOFTS']['BASE']:
        system.conf_firewall()

    if "SSH" in params['SOFTS']['BASE']:
        system.conf_ssh()

    if "UPGRADE" in params['SOFTS']['BASE']:
        system.upgrade()

    if "HOSTNAME" in params['SOFTS']['BASE']:
        system.conf_hostname()

    if "HOSTNAME" in params['SOFTS']['BASE']:
        system.conf_hostsfile()

    if "SSHHOSTKEY" in params['SOFTS']['BASE']:
        system.conf_hostkey()

    if "DNS" in params['SOFTS']['BASE']:
        system.conf_dns()

    """ Add user key """
    if "USERS" in params['SOFTS']['BASE']:
        system.conf_user()

    """ Install packages """
    server_roles = ['base', 'additionnal']
    system.install_packages(server_roles)

    """ SSHguard configuration """
    if "SSH" in params['SOFTS']['BASE']:
        system.conf_sshguard()

    """  Configure postfix """
    if "SMTP" in params['SOFTS']['BASE']:
        files_list = [
            ['/conf/POSTFIX/main.cf', '/etc/postfix/main.cf', '0640'],
        ]
        transverse.copyfiles(files_list)
        system.conf_postfix()

    """ Install lamp """
    apachelisten = "0.0.0.0:80"
    if "LAMP_BASE" in params['SOFTS']['LAMP']:
        server_roles = ['http', 'php', 'cache', 'database']
    elif "LAMP_ADVANCED" in params['SOFTS']['LAMP']:
        apachelisten = "127.0.0.1:8080"
        server_roles = ['http', 'php', 'cache', 'database', 'ssl']

    system.install_packages(server_roles)

    if "LOGS" in params['SOFTS']['BASE']:
        transverse.copyfiles([
            ['/conf/LOGROTATE/apache2.conf', '/etc/logrotate.d/apache2', '0640'],
            ['/conf/RSYSLOG/apache2.conf', '/etc/rsyslog.d/10-apache.conf', '0640']
        ])

    if "APACHE" not in params['SOFTS']['EXCLUDES']:
        """ Configure apache base """
        files_list = [
            ['/conf/APACHE/2.4/ports.conf', '/etc/apache2/ports.conf', '0640'],
            ['/conf/APACHE/2.4/apache2.conf', '/etc/apache2/apache2.conf', '0640'],
            ['/conf/APACHE/2.4/sites-available/000-default.conf', '/etc/apache2/sites-available/000-default.conf',
             '0640'],
            ['/conf/APACHE/2.4/conf-available/security.conf', '/etc/apache2/conf-available/security.conf', '0640'],
            ['/conf/APACHE/2.4/conf-available/badbot.conf', '/etc/apache2/conf-available/badbot.conf', '0640'],
        ]
        transverse.copyfiles(files_list)
        apache.conf_general(apachelisten)

    """ Configure php for apache """
    if "LAMP_BASE" in params['SOFTS']['LAMP'] and "PHP" not in params['SOFTS']['EXCLUDES']:
        transverse.copyfiles([
            ['/conf/PHP/7.0/php.ini', '/etc/php/7.0/apache2/php.ini', '0640']
        ])
        apache.conf_php()

    """ Configure apache vhosts """
    if "VHOSTS" not in params['SOFTS']['EXCLUDES']:
        apache.conf_vhost(apachelisten)
        services.management("apache2", "reload")

    """ Configure mysql """
    # mariadb.conf_init()
    for db in params['CONF']['MYSQL_CONF']:
        mariadb.conf_base("create", db)
        mariadb.conf_user("create", db)

    """ SPECIFICS TASK FOR ADVANCED """
    if "LAMP_ADVANCED" in params['SOFTS']['LAMP']:

        if "LOGS" in params['SOFTS']['BASE']:
            files_list = [
                ['/conf/LOGROTATE/varnish.conf', '/etc/logrotate.d/varnish', '0640']
            ]
            transverse.copyfiles(files_list)

        if "VARNISH" not in params['SOFTS']['EXCLUDES']:
            """ Configure VARNISH """
            varnish = Varnish(confr4p, params, logger)
            files_list = [
                ['/conf/VARNISH/includes/acls.vcl', '/etc/varnish/includes/acls.vcl', '0640'],
                ['/conf/VARNISH/includes/backends.vcl', '/etc/varnish/includes/backends.vcl', '0640'],
                ['/conf/VARNISH/includes/directors.vcl', '/etc/varnish/includes/directors.vcl', '0640'],
                ['/conf/VARNISH/includes/probes.vcl', '/etc/varnish/includes/probes.vcl', '0640'],
                ['/conf/VARNISH/production.vcl', '/etc/varnish/production.vcl', '0640'],
                ['/conf/VARNISH/varnish', '/etc/default/varnish', '0640'],
                ['/conf/VARNISH/varnish.service', '/lib/systemd/system/varnish.service', '0640'],
            ]

            run('mkdir -p /etc/varnish/includes/')
            transverse.copyfiles(files_list)
            varnish.conf_varnish()

        if "SSL" not in params['SOFTS']['EXCLUDES']:
            """ Configure letsencrypt """
            files_list = [
                ['/conf/LETSENCRYPT/certbot_cron', '/etc/cron.d/certbot', '0640'],
                ['/conf/LETSENCRYPT/certbot_renew.sh', '/usr/local/bin/certbot_renew.sh', '0750'],
                ['/conf/LETSENCRYPT/certbot_create.sh', '/usr/local/bin/certbot_create.sh', '0750'],
            ]
            transverse.copyfiles(files_list)

        if "FPM" not in params['SOFTS']['EXCLUDES']:
            """ Configure php-fpm (pools) """
            fpm = Fpm(confr4p, params, logger)
            files_list = [
                ['/conf/PHP/FPM/www.conf', '/etc/php/7.0/fpm/pool.d/www.conf', '0640'],
                ['/conf/PHP/7.0/php.ini', '/etc/php/7.0/fpm/php.ini', '0640']
            ]
            transverse.copyfiles(files_list)
            fpm.conf_fpm()

        if "HITCH" not in params['SOFTS']['EXCLUDES']:
            """ Hitch configuration """
            hitch = Hitch(confr4p, params, logger)
            run('mkdir -p /etc/hitch/defaultssl/')
            files_list = [
                ['/conf/HITCH/hitch.conf', '/etc/hitch/hitch.conf', '0640'],
                ['/data/ssl/default.pem', '/etc/hitch/defaultssl/default.pem', '0640']
            ]
            transverse.copyfiles(files_list)
            hitch.conf_hitch()
            services.management("hitch", "restart")

    if "NETWORK" in params['SOFTS']['BASE']:
        system.conf_interfaces()

    # END
    logger.closefile()
    with open(confr4p["LOGFILE"], 'r') as searchfile:
        for line in searchfile:
            if '[ERROR]' in line or '[INFO]' in line:
                print(line)
    print("All logs availables in {logfile}".format(logfile=confr4p["LOGFILE"]))
