#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import ConfigParser
import os
from fabric.api import *
import datetime


def deploy_base_lamp():
    # Global var
    global Logger, exiterror

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
    logfile = "/tmp/logsinstallr4p"

    # Exit ON error (stop program on error)
    exiterror = False

    # SYSTEM INFORMATION
    # THIS VALUE ARE USED IN CALCUL TO SET THE AUTOMATICS PARAMETERS IN THE SOFTWARES
    # CHANGES WITHOUT KNOW CAN DEGRADE SYSTEMS PERFORMANCES
    SMALL_VM = {
        "CPU": 1,
        "RAM": 2048
    }

    STANDARD_VM = {
        "CPU": 2,
        "RAM": 4048
    }

    STRONG_VM = {
        "CPU": 4,
        "RAM": 8096
    }


    """ 
    **********************
    * Configuration Zone *
    **********************
    """

    # SELECT YOU VM TYPE (SMALL_VM,  STANDARD_VM, STRONG_VM)
    # VM_TYPE = STANDARD_VM # CURRENTLY NOT IMPLEMENTED

    # Composants list:
    # You have the possibility to select specifics composants
    # UPGRADE, HOSTNAME, SSHHOSTKEY, DNS, USERBASHRC,
    # NETWORK, MOTD ,FW ( Firewall), VIM (Vim configuration)
    # SSH (sshd + sshguard), SMTP (postfix conf), LOGS, VHOSTS, USERS
    # MUST BE A LIST

    BASE = [
        "UPGRADE", "HOSTNAME",
        "SSHHOSTKEY", "DNS",
        "USERBASHRC", "NETWORK",
        "MOTD", "FW",
        "VIM", "SSH",
        "SMTP", "LOGS",
        "USERS", "VHOSTS"
    ]

    # Select lamp type (or keep empty for none installation)
    # LAMP_BASE (Apache, mariadb, phpmod)  OR
    # LAMP_AVANCED (Apache, mariadb, php-fpm, ssl, varnish)
    # MUST BE A LIST
    LAMP = ["LAMP_ADVANCED"]


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
                "FILES": "/data/sitedemo.com/index.html",
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
    CONF_INTERFACES["DEVISE"] = getinsterfacesname()

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
    Logger = Logs(logfile)

    ACTIONS.extend(BASE)
    ACTIONS.extend(LAMP)
    CONF_FILE = ""
    if "LAMP_ADVANCED" in ACTIONS:
        CONF_FILE = CONF_ROOT+"/debian9_lamp_advanced.ini"
        FILEDIR = "ADVANCED"
    else:
        CONF_FILE = CONF_ROOT+"/debian9_lamp_basic.ini"
        FILEDIR = "BASE"

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
    if "FW" in ACTIONS: conffirewall(PORT_SSH_NUMBER, CONF_INTERFACES)
    if "SSH" in ACTIONS: confssh(PORT_SSH_NUMBER)
    if "UPGRADE" in ACTIONS: upgrade()
    if "HOSTNAME" in ACTIONS: changehostname(HOSTNAME)
    if "HOSTNAME" in ACTIONS: changehostsfile(HOSTNAME, CONF_INTERFACES["NETWORK_IP"])
    if "SSHHOSTKEY" in ACTIONS: changehostkey()
    if "DNS" in ACTIONS: changedns(NETWORK_DNS)
    if "MOTD" in ACTIONS: dynmotd()

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
        sshguard(WHITELITSTIPS)

    """  Configure postfix """
    if "SMTP" in ACTIONS:
        files_list = [
            ['/conf/POSTFIX/main.cf', '/etc/postfix/main.cf', '0640'],
        ]
        copyfiles(CONF_ROOT, files_list)
        confpostfix(HOSTNAME)

    """ Install lamp """
    APACHELISTEN = "0.0.0.0:80"
    if "LAMP_BASE" in ACTIONS:
        SERVER_ROLES = ['http', 'php', 'cache', 'database']
    elif "LAMP_ADVANCED" in ACTIONS:
        APACHELISTEN = "127.0.0.1:8080"
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
        files_list.append(['/conf/PHP/7.0/php.ini', '/etc/php/7.0/apache2/php.ini', '0640'])
        copyfiles(CONF_ROOT, files_list)
        confapache(HOSTNAME, APACHELISTEN)

    """ Configure apache vhosts """
    if "VHOSTS" in ACTIONS:
        for VHOST in VHOSTS:
            confvhosts(CONF_ROOT, FILEDIR, APACHELISTEN, VHOST)
        service_gestion("apache2", "reload")

    """ Configure mysql """
    for db in MYSQL_CONF:
        mysql_base("create", db)
        mysql_user("create", db)

    """ SPECIFICS TASK FOR ADVANCED """
    if "LAMP_ADVANCED" in ACTIONS:
        """ Configure VARNISH """
        files_list = [
            ['/conf/VARNISH/includes/acls.vcl', '/etc/varnish/includes/acls.vcl', '0640'],
            ['/conf/VARNISH/includes/backends.vcl', '/etc/varnish/includes/backends.vcl', '0640'],
            ['/conf/VARNISH/includes/directors.vcl', '/etc/varnish/includes/directors.vcl', '0640'],
            ['/conf/VARNISH/includes/probes.vcl', '/etc/varnish/includes/probes.vcl', '0640'],
            ['/conf/VARNISH/production.vcl', '/etc/varnish/production.vcl', '0640'],
            ['/conf/VARNISH/varnish', '/etc/default/varnish', '0640'],
            ['/conf/VARNISH/varnish.service', '/lib/systemd/system/varnish.service', '0640'],
        ]

        if "LOGS" in ACTIONS:
            LOGFILES = [
                ['/conf/LOGROTATE/varnish.conf', '/etc/logrotate.d/varnish', '0640']
            ]
            for LOGFILE in LOGFILES:
                files_list.append(LOGFILE)

        run('mkdir -p /etc/varnish/includes/')
        copyfiles(CONF_ROOT, files_list)
        confvarnish()

        """ Configure letsencrypt """
        files_list = [
            ['/conf/LETSENCRYPT/certbot_cron', '/etc/cron.d/certbot', '0640'],
            ['/conf/LETSENCRYPT/certbot_renew.sh', '/usr/local/bin/certbot_renew.sh', '0750'],
            ['/conf/LETSENCRYPT/certbot_create.sh', '/usr/local/bin/certbot_create.sh', '0750'],
        ]
        copyfiles(CONF_ROOT, files_list)

        """ Configure php-fpm (pools) """
        files_list = [
            ['/conf/PHP/FPM/www.conf', '/etc/php/7.0/fpm/pool.d/www.conf', '0640']
        ]
        copyfiles(CONF_ROOT, files_list)
        confphpfpm()

        """ Hitch configuration """
        run('mkdir -p /etc/hitch/defaultssl/')
        files_list = [
            ['/conf/HITCH/hitch.conf', '/etc/hitch/hitch.conf', '0640'],
            ['/data/ssl/default.pem', '/etc/hitch/defaultssl/default.pem', '0640']
        ]
        copyfiles(CONF_ROOT, files_list)
        confhitch()

    if "NETWORK" in ACTIONS:
        changeinterface(CONF_ROOT, CONF_INTERFACES)
# ------------------------------------------ #

#  MYSQL  #
def mysql_iniconf():
    try:
        run("mysql -e 'DROP USER ''@'localhost';'")
        run("mysql -e 'DROP USER ''@'$(hostname)';'")
        run("mysql -e 'DROP DATABASE test;'")
        run("mysql -e 'FLUSH PRIVILEGES;'")
        Logger.writelog("[OK] Mysql clean installation")
    except BaseException as e:
        Logger.writelog("[ERROR] Mysql execution error ({error})".format(error=e))
        if exiterror:
            print("Error found: {error}".format(error=e))
            exit(1)


def mysql_user(action, value):
    try:
        if action == "create":
            run('mysql -e "CREATE USER IF NOT EXISTS  \'{username}\'@\'localhost\' IDENTIFIED BY \'{password}\';"'
                .format(username=value["username"], password=value["password"]))
            Logger.writelog("[OK] Create user )".format(username=value["username"]))
        elif action == "delete":
            run('mysql -e "DROP USER {username};"'.format(username=value["username"]))
            Logger.writelog("[OK] DROP user {username})".format(username=value["username"]))
        run('mysql -e "FLUSH PRIVILEGES;"')
        Logger.writelog("[OK] Apply mysql USERS privileges )".format(username=value["username"]))
    except BaseException as e:
        Logger.writelog("[ERROR] Mysql execution error ({error})".format(error=e))
        if exiterror:
            print("Error found: {error}".format(error=e))
            exit(1)

def mysql_base(action, value):
    try:
        if action == "create":
            run('mysql -e "CREATE  DATABASE IF NOT EXISTS  {dbname};"'.format(dbname=value["database"]))
            Logger.writelog("[OK] Create database: {dbname};".format(dbname=value["database"]))
        elif action == "delete":
            run('mysql -e "DROP  DATABASE  {dbname};"'.format(dbname=value["database"]))
            Logger.writelog("[OK] DROP database {dbname};".format(dbname=value["database"]))
    except BaseException as e:
        Logger.writelog("[ERROR] Mysql execution error ({error})".format(error=e))
        if exiterror:
            print("Error found: {error}".format(error=e))
            exit(1)

#  TRANSVERSE  #
def sedvalue(str_src, str_dest, conf_file):
    run('sed -i "s/{src_string}/{dest_string}/g" {filedir}'
        .format(src_string=str_src, dest_string=str_dest, filedir=conf_file)
    )
    Logger.writelog("[OK] Sed {src_string}, to {dest_string}, in {filedir}"
        .format(src_string=str_src, dest_string=str_dest, filedir=conf_file)
    )

def copyfiles(conf_root, files_list):
    for file in files_list:
        try:
            put(conf_root+file[0], file[1], mode=file[2])
            Logger.writelog("[OK] Copy {srcfile}, to {destfile}, with chmod {chmod}".format(
                srcfile=conf_root+file[0], destfile=file[1], chmod=file[2]
                )
            )
        except BaseException as e:
            Logger.writelog("[ERROR] Copy {srcfile}, to {destfile}, with chmod {chmod} ({error})".format(
                srcfile=conf_root+file[0], destfile=file[1], chmod=file[2], error=e
                )
            )
            if exiterror:
                print("Error found: {error}".format(error=e))
                exit(1)


def service_gestion(service, action):
    try:
        run("systemctl {actiontype} {servicename}"
            .format(actiontype=action, servicename=service)
        )
    except BaseException as e:
        Logger.writelog("[ERROR] action {actiontype}, on service {servicename} ({error})".format(
            actiontype=action, servicename=service, error=e
            )
        )
        if exiterror:
            print("Error found: {error}".format(error=e))
            exit(1)


#  APACHE  #
def confapache(HOSTNAME, APACHELISTEN):
        sedvalue("{servername}", HOSTNAME, "/etc/apache2/apache2.conf")
        sedvalue("{APACHE_LISTEN}", APACHELISTEN, "/etc/apache2/ports.conf")
        sedvalue("{APACHE_LISTEN}", APACHELISTEN, "/etc/apache2/sites-available/000-default.conf")
        apache_confactivation(["security.conf", "badbot.conf"])
        apache_modactivation(["headers"])
        service_gestion("apache2", "restart")


def apache_modactivation(modslist):
    for mod in modslist:
        try:
            run("a2enmod {modname}".format(modname=mod))
            Logger.writelog("[OK] Activate apache module {modname}".format(modname=mod))
        except BaseException as e:
            Logger.writelog("[ERROR]  Activate apache module {modname} ({error})".format(
                modname=mod, error=e
                )
            )
            if exiterror:
                print("Error found: {error}".format(error=e))
                exit(1)

def apache_confactivation(conflist):
    for conf in conflist:
        try:
            run("a2enconf {confname}".format(confname=conf))
            Logger.writelog("[OK] Activate apache configuration {confname}".format(confname=conf))
        except BaseException as e:
            Logger.writelog("[ERROR]  Activate apache configuration {confname} ({error})".format(
                confname=conf, error=e
                )
            )
            if exiterror:
                print("Error found: {error}".format(error=e))
                exit(1)

def apache_siteactivation(sitelist):
    for site in sitelist:
        try:
            run("a2ensite {sitename}".format(sitename=site))
            Logger.writelog("[OK] Activate apache web site {sitename}".format(sitename=site))
        except BaseException as e:
            Logger.writelog("[ERROR]  Activate apache web site {sitename} ({error})".format(
                sitename=site, error=e
                )
            )
            if exiterror:
                print("Error found: {error}".format(error=e))
                exit(1)

def confvhosts(CONF_ROOT, FILEDIR, APACHELISTEN, VHOST):
    run('mkdir -p /var/www/{servername}/prod/'.format(servername=VHOST["SERVER_NAME"]))
    run('mkdir -p /var/log/apache2/{servername}/'.format(servername=VHOST["SERVER_NAME"]))

    filename, file_extension = os.path.splitext(CONF_ROOT + VHOST["FILES"])

    copyfiles(CONF_ROOT, [
        ['/conf/APACHE/2.4/sites-available/{filedir}/010-mywebsite.com.conf'.format(filedir=FILEDIR),
         '/etc/apache2/sites-available/010.{servername}.conf'
              .format(servername=VHOST["SERVER_NAME"]), '0640'],
        ['{files}'.format(files=VHOST["FILES"]), '/var/www/{servername}/prod/site_tmp{fileexten}'
              .format(servername=VHOST["SERVER_NAME"], fileexten=file_extension), '0640']
    ])
    sedvalue("{domain_name}", VHOST["SERVER_NAME"], "/etc/apache2/sites-available/010.{servername}.conf"
             .format(servername=VHOST["SERVER_NAME"]))
    sedvalue("{domain_name_alias}", ''.join(VHOST["SERVER_NAME_ALIAS"]),
             "/etc/apache2/sites-available/010.{servername}.conf"
             .format(servername=VHOST["SERVER_NAME"]))

    sedvalue("{APACHE_LISTEN}", APACHELISTEN, "/etc/apache2/sites-available/010.{servername}.conf"
             .format(servername=VHOST["SERVER_NAME"]))

    if VHOST["FILES"]:
        sitefile = "/var/www/{servername}/prod/site_tmp{fileexten}".format(servername=VHOST["SERVER_NAME"],
                                                                           fileexten=file_extension)
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


def confvarnish():
    run('rm /etc/varnish/default.vcl')
    run('ln -sf /etc/varnish/production.vcl /etc/varnish/default.vcl')
    run('chown varnish:varnish -R /etc/varnish/')
    run('systemctl daemon-reload')
    service_gestion("varnish", "restart")


def confphpfpm():
    service_gestion("php7.0-fpm", "restart")


def confhitch():
    run('chown _hitch:_hitch -R /etc/hitch/')
    service_gestion("hitch", "restart")

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


def conffirewall(PORT_SSH_NUMBER, CONF_INTERFACES):
    print("Configure firewall...")
    sedvalue("{PUBLIC_IP}", CONF_INTERFACES["NETWORK_IP"], "/etc/init.d/firewall")
    sedvalue("{PORT_NUMBER}", PORT_SSH_NUMBER, "/etc/init.d/firewall")
    print("Apply Firewall")
    run("bash /etc/init.d/firewall")


def confssh(PORT_SSH_NUMBER):
    print("Change ssh port...")
    sedvalue("{PORT_NUMBER}", PORT_SSH_NUMBER, "/etc/ssh/sshd_config")
    print("Restart sshd service")
    service_gestion("sshd", "restart")

def sshguard(ips):
    run("echo > /etc/sshguard/whitelist")
    for ip in ips:
        run("echo {sshguardip} >> /etc/sshguard/whitelist ".format(sshguardip=ip))
    service_gestion("sshguard.service", "restart")

def confpostfix(HOSTNAME):
    sedvalue("{servername}", HOSTNAME, "/etc/postfix/main.cf")
    service_gestion("postfix", "restart")


def dynmotd():
    run('if [ ! -d "/etc/update-motd.d/" ];then mkdir /etc/update-motd.d; chmod +x /etc/update-motd.d; fi')
    run('rm -f /etc/motd')
    run('rm -f /etc/update-motd.d/*')
    run('ln -sf /var/run/motd.dynamic.new /etc/motd')


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
    try:
        run("echo {0}> /etc/hostname".format(hostname))
        Logger.writelog("[OK] Set new hostname for {0})".format(hostname))
        Logger.writelog("[INFO] To apply this new hostname, you must reboot")
    except BaseException as e:
        Logger.writelog("[ERROR] while hostfile settings ({error})".format(error=e))
        if exiterror:
            print("Error found: {error}".format(error=e))
            exit(1)

def changehostsfile(hostname, ip):
    try:
        run("echo > /etc/hosts")
        run("echo 127.0.0.1 localhost >> /etc/hosts")
        run("echo {0} {1} >> /etc/hosts".format(ip, hostname))
        Logger.writelog("[OK] Change hostfile with {0} {1})".format(ip, hostname))
    except BaseException as e:
        Logger.writelog("[ERROR] while hostfile settings ({error})".format(error=e))
        if exiterror:
            print("Error found: {error}".format(error=e))
            exit(1)


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
            try:
                run("apt-get install -y {0}".format(package))
                Logger.writelog("[OK] Installation package {package})".format(package=package))
            except BaseException as e:
                Logger.writelog("[ERROR] Installation package {package} ({error})".format(
                    package=package, error=e
                    )
                )
                if exiterror:
                    print("Error found: {error}".format(error=e))
                    exit(1)
class Logs:
    def __init__(self, logfiledir):
        self.logfiles = logfiledir
        self.file = open(self.logfiles, "w")

    def writelog(self, text):
        self.file.write(text+"\n")

    def closefile(self):
        self.file.close()
