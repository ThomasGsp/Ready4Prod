#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import ConfigParser
import os
from fabric.api import *
import datetime

def deploy_base_lamp():
    # Directory structure
    PROJECT_ROOT = os.path.dirname(__file__)
    CONF_ROOT = os.path.join(PROJECT_ROOT, 'lamp-debian9')

    ACTIONS = []

    env.user = 'root'
    env.key_filename = '~/.ssh/id_rsa'

    """ 
    **********************
    * Configuration Zone *
    **********************
    """

    # Composants list
    # ALL ( All composants = default)
    # UPGRADE, HOSTNAME, SSHHOSTKEY, DNS, USERBASHRC, NETWORK, MOTD ,FW ( Firewall) ,VIM (Vim configuration)
    # SSH (sshd + sshguard), SMTP (postfix conf), LOGS, VHOSTS, USERS

    BASE = [
        "UPGRADE", "HOSTNAME",
        "SSHHOSTKEY", "DNS",
        "USERBASHRC", "NETWORK",
        "MOTD", "FW",
        "VIM", "SSH",
        "SMTP", "LOGS",
        "USERS"
    ]

    # LAMP_BASE (Apache, mariadb, phpmod)  OR
    # LAMP_AVANCED (Apache, mariadb, php-fpm, ssl, varnish) // not avalaible
    LAMP = ["LAMP_BASE"]


    # Vhost apache2.4 configuration
    VHOSTS = \
        [
            {
                "SERVER_NAME": "sitedemo.com",
                "SERVER_NAME_ALIAS": ["www.sitedemo.com", "www.sitedemo.fr"],
                "FILES": "/data/sitedemo.com/index.html"
            },
            {
                "SERVER_NAME": "sitedemo1.com",
                "SERVER_NAME_ALIAS": ["www.sitedemo1.com", "www.sitedemo1.fr"],
                "FILES": "/data/sitedemo1.com/startbootstrap-resume-gh-pages.zip"
            }
        ]

    # DNS Servers
    NETWORK_DNS = ["208.67.222.222", "8.8.8.8"]

    # VM HOSTNAME
    HOSTNAME = "prdweb01"

    # SSH PORT
    PORT_SSH_NUMBER = "22"

    # SSHGUARD ip white list
    SSHGUARD_WL_IP = ["192.168.1.1", "172.16.10.5"]

    # NETWORK configuration
    CONF_INTERFACES = {}
    CONF_INTERFACES["NETWORK_IP"] = "172.16.0.207"
    CONF_INTERFACES["NETWORK_MASK"] = "255.255.255.0"
    CONF_INTERFACES["NETWORK_GW"] = "172.16.0.254"
    CONF_INTERFACES["mode"] = "static"
    CONF_INTERFACES["DEVISE"] = getinsterfacesname()

    # USERS configuration
    USERS = \
        [
            {
                "USER": "prod",
                "PASSWORD": "afinDLMLzef55fds",
                "ROOT": "test",
                "KEY": [""]
            }
    ]

    # Mysql users and databases configurations
    MYSQL_CONF = \
        [
            {
                "username": "produser",
                "password": "qzf5gr2",
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
    CONF_FILE = ""
    if "LAMP_ADVANCED" in ACTIONS:
        CONF_FILE = CONF_ROOT+"/debian9_lamp_advanced.ini"
    elif "LAMP_BASE" in ACTIONS:
        CONF_FILE = CONF_ROOT+"/debian9_lamp_basic.ini"

    if "UPGRADE" in ACTIONS: upgrade()
    if "HOSTNAME" in ACTIONS: changehostname(HOSTNAME)
    if "HOSTNAME" in ACTIONS: changehostsfile(HOSTNAME, CONF_INTERFACES["NETWORK_IP"])
    if "SSHHOSTKEY" in ACTIONS: changehostkey()
    if "DNS" in ACTIONS: changedns(NETWORK_DNS)
    if "MOTD" in ACTIONS: dynmotd(CONF_ROOT)

    """ Apply system base configuration """
    # File Source, Dest, filemode

    files_list = [
        ['/conf/SYSTEM/sources.list', '/etc/apt/sources.list', '0640'],
        ['/conf/SYSTEM/cpb.bash', '/usr/local/bin/cpb', '0755'],
        ['/conf/SYSTEM/bash_profile', '/root/.bash_profile', '0640'],
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
    if "FW" in ACTIONS:
        print("Configure firewall...")
        sedvalue("{PUBLIC_IP}", CONF_INTERFACES["NETWORK_IP"], "/etc/init.d/firewall")
        sedvalue("{PORT_NUMBER}", PORT_SSH_NUMBER, "/etc/init.d/firewall")
        print("Apply Firewall")
        run("bash /etc/init.d/firewall")

    # Update port ssh
    if "SSH" in ACTIONS:
        print("Change ssh port...")
        sedvalue("{PORT_NUMBER}", PORT_SSH_NUMBER, "/etc/ssh/sshd_config")
        print("Restart sshd service")
        service_gestion("sshd", "restart")

    """ Add user key """
    if "USERS" in ACTIONS:
        for USER in USERS:
            confuser(CONF_ROOT, ACTIONS, USER)

    """ Install packages """
    SERVER_ROLES = ['base', 'additionnal']
    env.roledefs = dict.fromkeys(SERVER_ROLES, [])
    install_packages(CONF_FILE, SERVER_ROLES)

    """ SSHguard configuration """
    if "SSH" in ACTIONS:
        sshguard(SSHGUARD_WL_IP)

    """  Configure postfix """
    if "SMTP" in ACTIONS:
        files_list = [
            ['/conf/POSTFIX/main.cf', '/etc/postfix/main.cf', '0640'],
        ]
        copyfiles(CONF_ROOT, files_list)
        sedvalue("{servername}", HOSTNAME, "/etc/postfix/main.cf")
        service_gestion("postfix", "restart")

    """ Install lamp """
    if "LAMP_BASE" in ACTIONS:
        SERVER_ROLES = ['http', 'php', 'cache', 'database']
    elif "LAMP_ADVANCED" in ACTIONS:
        SERVER_ROLES = ['http', 'php', 'cache', 'database', 'ssl']

    env.roledefs = dict.fromkeys(SERVER_ROLES, [])
    install_packages(CONF_FILE, SERVER_ROLES)

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

    if "LAMP_BASE" in ACTIONS:
        apache_modactivation(["headers"])
        files_list.append(['/conf/PHP/7.0/php.ini', '/etc/php/7.0/apache2/php.ini', '0640'])
    elif "LAMP_ADVANCED" in ACTIONS:
        apache_modactivation(["headers", "remoteip"])

    copyfiles(CONF_ROOT, files_list)
    sedvalue("{servername}", HOSTNAME, "/etc/apache2/apache2.conf")
    apache_confactivation(["security.conf", "badbot.conf"])

    """ Configure apache vhosts """
    if "VHOSTS" in ACTIONS:
        print("configure vhost...")
        for VHOST in VHOSTS:
            run('mkdir -p /var/www/{servername}/prod/'.format(servername=VHOST["SERVER_NAME"]))
            run('mkdir -p /var/log/apache2/{servername}/'.format(servername=VHOST["SERVER_NAME"]))

            filename, file_extension = os.path.splitext(CONF_ROOT + VHOST["FILES"])

            copyfiles(CONF_ROOT, [
                ['/conf/APACHE/2.4/sites-available/010-mywebsite.com.conf', '/etc/apache2/sites-available/010.{servername}.conf'
                      .format(servername=VHOST["SERVER_NAME"]), '0640'],
                ['{files}'.format(files=VHOST["FILES"]), '/var/www/{servername}/prod/site_tmp{fileexten}'
                      .format(servername=VHOST["SERVER_NAME"], fileexten=file_extension), '0640']
            ])
            sedvalue("{domain_name}", VHOST["SERVER_NAME"], "/etc/apache2/sites-available/010.{servername}.conf"
                     .format(servername=VHOST["SERVER_NAME"]))
            sedvalue("{domain_name_alias}", ''.join(VHOST["SERVER_NAME_ALIAS"]), "/etc/apache2/sites-available/010.{servername}.conf"
                     .format(servername=VHOST["SERVER_NAME"]))

            if VHOST["FILES"]:
                sitefile = "/var/www/{servername}/prod/site_tmp{fileexten}".format(servername=VHOST["SERVER_NAME"], fileexten=file_extension)
                sitedir = "/var/www/{servername}/prod/".format(servername=VHOST["SERVER_NAME"])
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

            run('chown 33:33 -R /var/www/{servername}'.format(servername=VHOST["SERVER_NAME"]))
            run('find /var/www/{servername} -type d -exec chmod 750 -v {{}} \;'.format(servername=VHOST["SERVER_NAME"]))
            run('find /var/www/{servername} -type f -exec chmod 640 -v {{}} \;'.format(servername=VHOST["SERVER_NAME"]))
            apache_siteactivation(["010.{servername}.conf".format(servername=VHOST["SERVER_NAME"])])

    service_gestion("apache2", "restart")

    """ Configure mysql """
    for db in MYSQL_CONF:
        mysql_base("create", db)
        mysql_user("create", db)

    if "NETWORK" in ACTIONS:
        changeinterface(CONF_ROOT, CONF_INTERFACES)


    """ SPECIFICS TASK FOR ADVANCED """
    if "LAMP_ADVANCED" in ACTIONS:
        # Install varnish & configure
        # Install lestencrypt & configure
        # Install hitch & configure
        # Configure php-fpm (pools)
        # Configure apache2 (mod_fastcgi.c)
        pass

# ------------------------------------------ #

#  MYSQL  #
def mysql_iniconf():
    run("mysql -e 'DROP USER ''@'localhost';'")
    run("mysql -e 'DROP USER ''@'$(hostname)';'")
    run("mysql -e 'DROP DATABASE test;'")
    run("mysql -e 'FLUSH PRIVILEGES;'")


def mysql_user(action, value):
    if action == "create":
        run('mysql -e "CREATE USER IF NOT EXISTS  \'{username}\'@\'localhost\' IDENTIFIED BY \'{password}\';"'
            .format(username=value["username"], password=value["password"]))
    elif action == "delete":
        run('mysql -e "DROP USER {username};"'.format(username=value["username"]))
    run('mysql -e "FLUSH PRIVILEGES;"')


def mysql_base(action, value):
    if action == "create":
        run('mysql -e "CREATE  DATABASE IF NOT EXISTS  {dbname};"'.format(dbname=value["database"]))
    elif action == "delete":
        run('mysql -e "DROP  DATABASE  {dbname};"'.format(dbname=value["database"]))


#  TRANSVERSE  #
def sedvalue(str_src, str_dest, conf_file):
    run('sed -i "s/{0}/{1}/g" {2}'.format(str_src, str_dest, conf_file))


def copyfiles(conf_root, files_list):
    for file in files_list:
        try:
            put(conf_root+file[0], file[1], mode=file[2])
        except BaseException as e:
            print(e)

def service_gestion(service, action):
    run("systemctl {actiontype} {servicename}".format(actiontype=action, servicename=service))

#  APACHE  #
def apache_modactivation(modslist):
    for mod in modslist:
        run("a2enmod {modname}".format(modname=mod))


def apache_confactivation(conflist):
    for conf in conflist:
        run("a2enconf {confname}".format(confname=conf))


def apache_siteactivation(sitelist):
    for site in sitelist:
        run("a2ensite {sitename}".format(sitename=site))


#  SYSTEM  #
def upgrade():
    run("apt-get update")
    run("apt-get upgrade -y")

def changedns(ips):
    run("echo > /etc/resolv.conf")
    for ip in ips:
        run("echo nameserver {dnsip} >> /etc/resolv.conf ".format(dnsip=ip))


def changehostkey():
    print("Remove old ssh key...")
    run("/bin/rm -v /etc/ssh/ssh_host_*")
    print("Generate new key...")
    run("dpkg-reconfigure openssh-server")
    print("Restart sshd service")
    service_gestion("sshd", "restart")


def sshguard(ips):
    run("echo > /etc/sshguard/whitelist")
    for ip in ips:
        run("echo {sshguardip} >> /etc/sshguard/whitelist ".format(sshguardip=ip))
    service_gestion("sshguard.service", "restart")



def dynmotd(CONF_ROOT):
    run('if [ ! -d "/etc/update-motd.d/" ];then mkdir /etc/update-motd.d; chmod +x /etc/update-motd.d; fi')
    run('rm -f /etc/motd')
    run('rm -f /etc/update-motd.d/*')
    run('ln -sf /var/run/motd.dynamic.new /etc/motd')

    files_list = [
        ['/conf/SYSTEM/motd.bash', '/etc/update-motd.d/10-sysinfo', '0755'],
    ]

    copyfiles(CONF_ROOT, files_list)


def confuser(CONF_ROOT, ACTIONS, user):
    # Create the new admin user (default group=username); add to admin group
    run('getent passwd {username}  || adduser {username} --disabled-password --gecos ""'.format(
        username=user["USER"]))

    # Set the password for the new user
    run('echo "{username}:{password}" | chpasswd'.format(
        username=user["USER"],
        password=user["PASSWORD"]))

    run("mkdir -p /home/{username}/.ssh/".format(username=user["USER"]))
    run("echo '' > /home/{username}/.ssh/authorized_keys".format(username=user["USER"]))
    for key in user["KEY"]:
        run("echo {keyv} >> /home/{username}/.ssh/authorized_keys".format(keyv=key, username=user["USER"]))
        run("chmod 600 -R /home/{username}/.ssh/authorized_keys".format(username=user["USER"]))

    if "USERBASHRC" in ACTIONS:
        files_list = [
            ['/conf/SYSTEM/bashrc', '/home/{username}/.bashrc'.format(username=user["USER"]), '0640'],
            ['/conf/SYSTEM/bash_profile', '/home/{username}/.bash_profile'.format(username=user["USER"]), '0640']
        ]
        copyfiles(CONF_ROOT, files_list)

    run("chown {username}: -R /home/{username}/".format(username=user["USER"]))

def changehostname(hostname):
    run("echo {0}> /etc/hostname".format(hostname))
    print("To apply change, you must reboot")


def changehostsfile(hostname, ip):
    run("echo > /etc/hosts")
    run("echo 127.0.0.1 localhost >> /etc/hosts")
    run("echo {0} {1} >> /etc/hosts".format(ip, hostname))
    print("To apply change, you must reboot")


def host_type():
    run('uname -s')


def getinsterfacesname():
    nameint = run("dmesg |grep renamed.*eth|awk -F' ' '{print substr($5,0,length($5)-1)}'")
    return nameint


def changeinterface(CONF_ROOT, CONF_INTERFACES):
    currentdate = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')
    run("cp /etc/network/interfaces /etc/network/interfaces.{date}".format(date=currentdate))

    copyfiles(CONF_ROOT, [
        ['/conf/changeInterface.awk', '/tmp/changeinterface.awk', '0700'],
        ['/conf/SYSTEM/interfaces', '/etc/network/interfaces', '0600']
    ])

    run(
        "awk -f /tmp/changeinterface.awk /etc/network/interfaces "
        "device={device} "
        "mode={mode} "
        "action={action} "
        "address={address} "
        "netmask={netmask} "
        "gateway={gateway} "
        ">> /etc/network/interfaces"
        "".format(
            device=CONF_INTERFACES["DEVISE"],
            mode=CONF_INTERFACES["mode"],
            action="add",
            address=CONF_INTERFACES["NETWORK_IP"],
            netmask=CONF_INTERFACES["NETWORK_MASK"],
            gateway=CONF_INTERFACES["NETWORK_GW"]
        )
    )


def install_packages(conf_root, roles):
    config_file = os.path.join(conf_root % env)
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)
    for role in roles:
        for package in config.get(role, 'packages').split(' '):
            print('Install {0}'.format(package))
            run("apt-get install -y {0}".format(package))
