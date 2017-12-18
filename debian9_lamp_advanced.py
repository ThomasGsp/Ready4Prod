#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from libs.debian9.system import *
from libs.debian9.process import *


def deploy_lamp():
    """ 
    **********************
    * Configuration R4P  *
    **********************
    """
    # Just init var, do not change
    PARAMS = {}
    CONFR4P = {}

    # Directory structure
    PROJECT_ROOT = os.path.dirname(__file__)
    CONFR4P["CONF_ROOT"] = os.path.join(PROJECT_ROOT, 'lamp-debian9')
    # INI file
    CONFR4P["CONF_FILE"] = "debian9_lamp_advanced.ini"
    # specific dir for files configurations
    CONFR4P["FILEDIR"] = "ADVANCED"

    # VM env access
    env.user = 'root'
    env.key_filename = 'keys/changeme'

    # Log output
    CONFR4P["LOGFILE"] = "/tmp/logsinstallr4p"

    # Exit ON error (stop program on error) - True or False (CASE!)
    CONFR4P["EXITONERROR"] = True

    logger = Logs(CONFR4P["LOGFILE"])
    system = System(CONFR4P, PARAMS, logger)

    """ 
    **********************
    * Configuration Zone *
    **********************
    """

    # SYSTEM INFORMATION
    # THIS VALUE ARE USED TO SET THE AUTOMATICS PARAMETERS IN THE SOFTWARES
    PARAMS['HARDWARE'] = \
        {
            'VM': {
                "CPU": 2,
                "RAM": 8096
            }
        }

    PARAMS['SOFTS'] = \
        {
            # Composants list:
            # You have the possibility to select specifics composants
            # UPGRADE, HOSTNAME, SSHHOSTKEY, DNS, USERBASHRC,
            # NETWORK, MOTD ,FW ( Firewall), VIM (Vim configuration)
            # SSH (sshd + sshguard), SMTP (postfix conf), LOGS, USERS
            # MUST BE A LIST
            'BASE':
                [
                    "UPGRADE", "HOSTNAME",
                    "SSHHOSTKEY", "DNS",
                    "USERBASHRC", "NETWORK",
                    "MOTD", "FW",
                    "VIM", "SSH",
                    "SMTP", "LOGS",
                    "USERS"
                ],

            #  Select lamp type (or keep empty for none installation)
            # LAMP_BASE (Apache, mariadb, phpmod)  OR
            # LAMP_ADVANCED (Apache, mariadb, php-fpm, ssl, varnish)
            # MUST BE A LIST
            'LAMP': ["LAMP_ADVANCED"],

            # List: "VHOSTS", "VARNISH", "APACHE", "FPM",  "HITCH", "SSL"
            'EXCLUDES': []
        }

    PARAMS['CONF'] = \
        {

            # VHOSTS configuration
            'VHOSTS':
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
                ],

            # DNS Servers
            # MUST BE A LIST
            'NETWORK_DNS': ["208.67.222.222", "8.8.8.8"],

            # VM HOSTNAME
            # MUST BE A STRING
            'HOSTNAME': "prdweb01",

            # SSH PORT
            # MUST BE A STRING
            'PORT_SSH_NUMBER': "22",


            # GENERAL WHITELIST IP (SSH, FIREWALL, SOFT...)
            # MUST BE A LIST
            'WHITELITSTIPS': ["192.168.1.1", "172.16.10.5", "127.0.0.1"],


            # NETWORK configuration
            'CONF_INTERFACES':
                [
                    {
                        "NETWORK_IP": "172.16.0.220",
                        "NETWORK_MASK": "255.255.255.0",
                        "NETWORK_GW": "172.16.0.254",
                        "MODE": "static",
                        "DEVISE": system.getinsterfacesname()
                        # getinsterfacesname() = Autoselection OR interface name
                    }
                ],

            # USERS configuration
            'USERS':
            [
                {
                    "USER": "prod",
                    "PASSWORD": "afinDLMLzef55fds", # CLEAR PW
                    "KEY": [""]     # Public Key (LIST)
                }
            ],

            # Mysql users and databases configurations
            'MYSQL_CONF':
            [
                {
                    "username": "produser",
                    "password": "qzf5gr2", # CLEAR PW
                    "database": "prodbase"
                }
            ]
        }

    # main task, do not change
    process(CONFR4P, PARAMS, logger)



