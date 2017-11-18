#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import ConfigParser
import os
from fabric.api import *
import datetime

def deploy_base_lamp():
    # Var list

    # Directory structure
    PROJECT_ROOT = os.path.dirname(__file__)
    CONF_ROOT = os.path.join(PROJECT_ROOT, 'lamp-debian9')


    env.user = 'root'
    env.key_filename = '~/.ssh/id_rsa'

    """ 
    **********************
    * Configuration Zone *
    **********************
    """

    VHOSTS = \
        [
            {
                "SERVER_NAME": "sitedemo.com",
                "SERVER_NAME_ALIAS": ["www.sitedemo.com", "www.sitedemo.fr"]
            },
            {
                "SERVER_NAME": "sitedemo1.com",
                "SERVER_NAME_ALIAS": ["www.sitedemo1.com", "www.sitedemo1.fr"]
            }
        ]

    # Not implemented
    NETWORK_DNS = "208.67.222.222"

    HOSTNAME = "prdweb01"
    PORT_SSH_NUMBER = "22"

    CONF_INTERFACES = {}
    CONF_INTERFACES["NETWORK_IP"] = "172.16.0.207"
    CONF_INTERFACES["NETWORK_MASK"] = "255.255.255.0"
    CONF_INTERFACES["NETWORK_GW"] = "172.16.0.254"
    CONF_INTERFACES["mode"] = "static"
    CONF_INTERFACES["DEVISE"] = getinsterfacesname()

    USERS = \
        [
            {
                "USER": "prod",
                "PASSWORD": "afinDLMLzef55fds",
                "ROOT": "test",
                "KEY": [""]
            }
    ]

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

    upgrade()
    changehostname(HOSTNAME)
    changehostkey()

    """ Apply system base configuration """
    # File Source, Dest, filemode
    files_list = [
        ['/conf/SYSTEM/sources.list', '/etc/apt/sources.list', '0640'],
        ['/conf/SYSTEM/firewall.sh', '/etc/init.d/firewall', '0740'],
        ['/conf/SYSTEM/sshd_config', '/etc/ssh/sshd_config', '0640'],
    ]

    copyfiles(CONF_ROOT, files_list)

    # Firewall
    print("Configure firewall...")
    sedvalue("{PUBLIC_IP}", CONF_INTERFACES["NETWORK_IP"], "/etc/init.d/firewall")
    print("Apply Firewall")
    run("bash /etc/init.d/firewall")

    # Update port ssh
    print("Change ssh port...")
    sedvalue("{PORT_NUMBER}", PORT_SSH_NUMBER, "/etc/ssh/sshd_config")
    print("update firewall...")
    sedvalue("{PORT_NUMBER}", PORT_SSH_NUMBER, "/etc/init.d/firewall")
    print("Restart sshd service")
    run("systemctl restart sshd")

    """ Add user key """
    for USER in USERS:
        confuser(USER)

    """ Install packages """
    SERVER_ROLES = ['base', 'additionnal']
    env.roledefs = dict.fromkeys(SERVER_ROLES, [])
    install_packages(CONF_ROOT, SERVER_ROLES)

    """ Install lamp """
    SERVER_ROLES = ['http', 'php', 'cache', 'database']
    env.roledefs = dict.fromkeys(SERVER_ROLES, [])
    install_packages(CONF_ROOT, SERVER_ROLES)

    """ Configure apache base """
    files_list = [
        ['/conf/APACHE/2.4/ports.conf', '/etc/apache2/ports.conf', '0640'],
        ['/conf/APACHE/2.4/apache2.conf', '/etc/apache2/apache2.conf', '0640'],
        ['/conf/APACHE/2.4/sites-available/000-default.conf', '/etc/apache2/sites-available/000-default.conf', '0640'],
        ['/conf/APACHE/2.4/conf-available/security.conf', '/etc/apache2/conf-available/security.conf', '0640'],
        ['/conf/APACHE/2.4/conf-available/badbot.conf', '/etc/apache2/conf-available/badbot.conf', '0640'],
        ['/conf/PHP/7.0/php.ini', '/etc/php/7.0/apache2/php.ini', '0640'],
    ]
    copyfiles(CONF_ROOT, files_list)
    sedvalue("{servername}", HOSTNAME, "/etc/apache2/apache2.conf")
    apache_modactivation(["headers"])
    apache_confactivation(["security.conf", "badbot.conf"])

    """ Configure apache vhosts """
    print("configure vhost...")
    for VHOST in VHOSTS:
        copyfiles(CONF_ROOT, [
            ['/conf/APACHE/2.4/sites-available/010-mywebsite.com.conf', '/etc/apache2/sites-available/010.{servername}.conf'
                  .format(servername=VHOST["SERVER_NAME"]), '0640']
        ])
        sedvalue("{domain_name}", VHOST["SERVER_NAME"], "/etc/apache2/sites-available/010.{servername}.conf"
                 .format(servername=VHOST["SERVER_NAME"]))
        sedvalue("{domain_name_alias}", ''.join(VHOST["SERVER_NAME_ALIAS"]), "/etc/apache2/sites-available/010.{servername}.conf"
                 .format(servername=VHOST["SERVER_NAME"]))

        run('mkdir -p /var/www/{servername}/prod/'.format(servername=VHOST["SERVER_NAME"]))
        run('chown 33:33 -R /var/www/{servername}/prod/'.format(servername=VHOST["SERVER_NAME"]))
        run('mkdir -p /var/log/apache2/{servername}/'.format(servername=VHOST["SERVER_NAME"]))
        apache_siteactivation(["010.{servername}.conf".format(servername=VHOST["SERVER_NAME"])])

    apache_gestion("restart")

    """ Configure mysql """
    for db in MYSQL_CONF:
        mysql_base("create", db)
        mysql_user("create", db)

    changeinterface(CONF_ROOT, CONF_INTERFACES)


# ------------------------------------------ #

#  MYSQL  #
def mysql_iniconf():
    run("mysql -e 'DROP USER ''@'localhost';'")
    run("mysql -e 'DROP USER ''@'$(hostname)';'")
    run("mysql -e 'DROP DATABASE test;'")
    run("mysql -e 'FLUSH PRIVILEGES;'")
    return


def mysql_user(action, value):
    if action == "create":
        run('mysql -e "CREATE USER IF NOT EXISTS  \'{username}\'@\'localhost\' IDENTIFIED BY \'{password}\';"'
            .format(username=value["username"], password=value["password"]))
    elif action == "delete":
        run('mysql -e "DROP USER {username};"'.format(username=value["username"]))
    run('mysql -e "FLUSH PRIVILEGES;"')
    return


def mysql_base(action, value):
    if action == "create":
        run('mysql -e "CREATE  DATABASE IF NOT EXISTS  {dbname};"'.format(dbname=value["database"]))
    elif action == "delete":
        run('mysql -e "DROP  DATABASE  {dbname};"'.format(dbname=value["database"]))
    return


#  TRANSVERSE  #
def sedvalue(str_src, str_dest, conf_file):
    run('sed -i "s/{0}/{1}/g" {2}'.format(str_src, str_dest, conf_file))


def copyfiles(conf_root, files_list):
    for file in files_list:
        put(conf_root+file[0], file[1], mode=file[2])


#  APACHE  #
def apache_gestion(action):
    run("systemctl {actiontype} apache2".format(actiontype=action))


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


def changehostkey():
    print("Remove old ssh key...")
    run("/bin/rm -v /etc/ssh/ssh_host_*")
    print("Generate new key...")
    run("dpkg-reconfigure openssh-server")
    print("Restart sshd service")
    run("systemctl restart sshd")


def confuser(user):
    # Create the new admin user (default group=username); add to admin group
    run('getent passwd {username}  || adduser {username} --disabled-password --gecos ""'.format(
        username=user["PASSWORD"]))

    # Set the password for the new user
    run('echo "{username}:{password}" | chpasswd'.format(
        username=user["USER"],
        password=user["PASSWORD"]))

    run("mkdir -p /home/{username}/.ssh/".format(username=user["USER"]))
    run("echo '' > /home/{username}/.ssh/authorized_keys".format(username=user["USER"]))
    for key in user["KEY"]:
        run("echo {keyv} >> /home/{username}/.ssh/authorized_keys".format(keyv=key, username=user["USER"]))
        run("chown {username}: -R /home/{username}/.ssh/".format(username=user["USER"]))
        run("chmod 600 -R /home/{username}/.ssh/authorized_keys".format(username=user["USER"]))
    return


def changehostname(hostname):
    run("echo {0}> /etc/hostname".format(hostname))
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
    config_file = os.path.join(conf_root, u'debian9.ini' % env)
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)
    for role in roles:
        for package in config.get(role, 'packages').split(' '):
            print('Install {0}'.format(package))
            run("apt-get install -y {0}".format(package))
