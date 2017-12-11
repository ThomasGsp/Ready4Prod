#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# Global var
global Logger, EXITONERROR

# Imports
import os
from fabric.api import *
from libs.transverse import *
from libs.debian9.system import *
from libs.debian9.services import *
from libs.debian9.apache import *
from libs.debian9.maria import *


def deploy_base_lamp():
    """ 
    **********************
    * Configuration R4P  *
    **********************
    """

    # Directory structure
    PROJECT_ROOT = os.path.dirname(__file__)
    CONF_ROOT = os.path.join(PROJECT_ROOT, 'lamp-debian9')
    ACTIONS = []

    # VM env access
    env.user = 'root'
    env.key_filename = '~/.ssh/id_rsa'

    # Log output
    LOGFILE = "/tmp/logsinstallr4p"
    Logger = Logs(LOGFILE)
    # Exit ON error (stop program on error) - True or False (CASE!)
    EXITONERROR = True

    # SYSTEM INFORMATION
    # THIS VALUE ARE USED TO SET THE AUTOMATICS PARAMETERS IN THE SOFTWARES
    VM_C = {
        "CPU": 4,
        "RAM": 8096
    }

    """ 
    **********************
    * Configuration Zone *
    **********************
    """
    # Composants list:
    # You have the possibility to select specifics composants
    # UPGRADE, HOSTNAME, SSHHOSTKEY, DNS, USERBASHRC,
    # NETWORK, MOTD ,FW ( Firewall), VIM (Vim configuration)
    # SSH (sshd + sshguard), SMTP (postfix conf), LOGS, USERS
    # MUST BE A LIST

    BASE = [
        "UPGRADE", "HOSTNAME",
        "SSHHOSTKEY", "DNS",
        "USERBASHRC", "NETWORK",
        "MOTD", "FW",
        "VIM", "SSH",
        "SMTP", "LOGS",
        "USERS"
    ]

    # Select lamp type (or keep empty for none installation)
    # LAMP_BASE (Apache, mariadb, phpmod)  OR
    # LAMP_AVANCED (Apache, mariadb, php-fpm, ssl, varnish)
    # MUST BE A LIST
    LAMP = ["LAMP_BASE"]

    # List: "VHOSTS", "VARNISH", "APACHE", "PHP",  "HITCH", "SSL"

    SOFT = [
        "VHOSTS",
        "APACHE",
        "PHP",
    ]

    # VHOSTS configuration
    #  MUST BE A DICT
    VHOSTS = \
        [
            {
                # Main domain name
                "SERVER_NAME": "sitedemo.com",
                # Secondary domain name
                "SERVER_NAME_ALIAS": ["www.sitedemo.com", "www.sitedemo.fr"],
                # File for this domain ( zip, tar, tar.gz, tar.bz2, direct files)
                "FILES": "/data/sitedemo.com/*",
            },
            {
                "SERVER_NAME": "sitedemo1.com",
                "SERVER_NAME_ALIAS": ["www.sitedemo1.com", "www.sitedemo1.fr"],
                "FILES": "/data/sitedemo1.com/startbootstrap-resume-gh-pages.zip"
            }
        ]

    # DNS Servers
    # MUST BE A LIST
    NETWORK_DNS = ["208.67.222.222", "8.8.8.8"]

    # VM HOSTNAME
    # MUST BE A STRING
    HOSTNAME = "prdweb01"

    # SSH PORT
    # MUST BE A STRING
    PORT_SSH_NUMBER = "22"

    # GENERAL WHITELIST IP (SSH, FIREWALL, SOFT...)
    # MUST BE A LIST
    WHITELITSTIPS = ["192.168.1.1", "172.16.10.5", "127.0.0.1"]

    # NETWORK configuration
    # MUST BE A STRING
    CONF_INTERFACES = {}
    CONF_INTERFACES["NETWORK_IP"] = "172.16.0.207"
    CONF_INTERFACES["NETWORK_MASK"] = "255.255.255.0"
    CONF_INTERFACES["NETWORK_GW"] = "172.16.0.254"
    CONF_INTERFACES["mode"] = "static"
    # getinsterfacesname() = Autoselection OR interface name
    CONF_INTERFACES["DEVISE"] = System.getinsterfacesname()

    # USERS configuration
    # MUST BE DICT
    USERS = \
        [
            {
                "USER": "prod",
                "PASSWORD": "afinDLMLzef55fds", # CLEAR PW
                "KEY": [""]     # Public Key (LIST)
            }
    ]

    # Mysql users and databases configurations
    MYSQL_CONF = \
        [
            {
                "username": "produser",
                "password": "qzf5gr2", # CLEAR PW
                "database": "prodbase"
            }
        ]



    """ 
    ************
    * Proccess *
    ************
    """
    ACTIONS.extend(BASE)
    ACTIONS.extend(LAMP)
    ACTIONS.extend(SOFT)

    CONF_FILE = CONF_ROOT+"/debian9_lamp_basic.ini"
    FILEDIR = "BASE"

    if "MOTD" in ACTIONS: System.conf_dynmotd()

    files_list = [
        ['/conf/SYSTEM/sources.list', '/etc/apt/sources.list', '0640'],
        ['/conf/SYSTEM/cpb.bash', '/usr/local/bin/cpb', '0755'],
        ['/conf/SYSTEM/bash_profile', '/root/.bash_profile', '0640'],
        ['/conf/SYSTEM/motd.bash', '/etc/update-motd.d/10-sysinfo', '0755'],
    ]

    if "USERBASHRC" in ACTIONS: files_list.append(
        ['/conf/SYSTEM/bashrc', '/root/.bashrc', '0640'])
    if "SSH" in ACTIONS: files_list.append(
        ['/conf/SYSTEM/sshd_config', '/etc/ssh/sshd_config', '0640'])
    if "FW" in ACTIONS: files_list.append(
        ['/conf/SYSTEM/firewall.sh', '/etc/init.d/firewall', '0740'])
    if "VIM" in ACTIONS: files_list.append(
        ['/conf/SYSTEM/defaults.vim', '/usr/share/vim/vim80/defaults.vim', '0644'])

    copyfiles(CONF_ROOT, files_list)

    # Firewall
    if "FW" in ACTIONS: System.conf_firewall(PORT_SSH_NUMBER, CONF_INTERFACES)
    if "SSH" in ACTIONS: System.conf_ssh(PORT_SSH_NUMBER)
    if "UPGRADE" in ACTIONS: System.upgrade()
    if "HOSTNAME" in ACTIONS: System.conf_hostname(HOSTNAME)
    if "HOSTNAME" in ACTIONS: System.conf_hostsfile(HOSTNAME, CONF_INTERFACES["NETWORK_IP"])
    if "SSHHOSTKEY" in ACTIONS: System.conf_hostkey()
    if "DNS" in ACTIONS: System.conf_dns(NETWORK_DNS)

    """ Add user key """
    if "USERS" in ACTIONS:
        for USER in USERS:
            System.conf_user(CONF_ROOT, ACTIONS, USER)

    """ Install packages """
    SERVER_ROLES = ['base', 'additionnal']
    env.roledefs = dict.fromkeys(SERVER_ROLES, [])
    System.install_packages(CONF_FILE, SERVER_ROLES)

    """ SSHguard configuration """
    if "SSH" in ACTIONS:
        System.conf_sshguard(WHITELITSTIPS)

    """  Configure postfix """
    if "SMTP" in ACTIONS:
        files_list = [
            ['/conf/POSTFIX/main.cf', '/etc/postfix/main.cf', '0640'],
        ]
        copyfiles(CONF_ROOT, files_list)
        System.conf_postfix(HOSTNAME)

    """ Install lamp """
    APACHELISTEN = "0.0.0.0:80"
    SERVER_ROLES = ['http', 'php', 'cache', 'database']

    env.roledefs = dict.fromkeys(SERVER_ROLES, [])
    System.install_packages(CONF_FILE, SERVER_ROLES)

    """ Configure apache base """
    files_list = [
        ['/conf/APACHE/2.4/ports.conf', '/etc/apache2/ports.conf', '0640'],
        ['/conf/APACHE/2.4/apache2.conf', '/etc/apache2/apache2.conf', '0640'],
        ['/conf/APACHE/2.4/sites-available/000-default.conf', '/etc/apache2/sites-available/000-default.conf', '0640'],
        ['/conf/APACHE/2.4/conf-available/security.conf', '/etc/apache2/conf-available/security.conf', '0640'],
        ['/conf/APACHE/2.4/conf-available/badbot.conf', '/etc/apache2/conf-available/badbot.conf', '0640'],
    ]

    if "LOGS" in ACTIONS:
        LOGFILES = [
            ['/conf/LOGROTATE/apache2.conf', '/etc/logrotate.d/apache2', '0640'],
            ['/conf/RSYSLOG/apache2.conf', '/etc/rsyslog.d/10-apache.conf', '0640']
        ]
        for LOGFILE in LOGFILES:
            files_list.append(LOGFILE)

    if "APACHE" in ACTIONS:
        copyfiles(CONF_ROOT, files_list)
        Apache.conf_general(HOSTNAME, APACHELISTEN)

    """ Configure php for apache """
    if "LAMP_BASE" in ACTIONS and "PHP" in ACTIONS:
        copyfiles(CONF_ROOT, [
            ['/conf/PHP/7.0/php.ini', '/etc/php/7.0/apache2/php.ini', '0640']
        ])
        Apache.conf_php(VM_C)

    """ Configure apache vhosts """
    if "VHOSTS" in ACTIONS:
        for VHOST in VHOSTS:
            Apache.conf_vhost(CONF_ROOT, FILEDIR, APACHELISTEN, VHOST)
        Services.management("apache2", "reload")

    """ Configure mysql """
    MariaDB.conf_init()
    for db in MYSQL_CONF:
        MariaDB.conf_base("create", db)
        MariaDB.conf_user("create", db)

    if "NETWORK" in ACTIONS:
        System.conf_interfaces(CONF_ROOT, CONF_INTERFACES)

    # END
    Logger.closefile()
    with open(LOGFILE, 'r') as searchfile:
        for line in searchfile:
            if '[ERROR]' in line or '[INFO]' in line:
                print(line)
    print("All logs availables in {logfile}".format(logfile=LOGFILE))