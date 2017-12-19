"""
Class : System functions
Version : 1
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""

import ConfigParser
import os
import datetime
from fabric.api import *
from libs.transverse import *
from libs.debian9.services import *


class System:
    def __init__(self, confr4p, params, logger):
        self.confr4p = confr4p
        self.params = params
        self.logger = logger
        self.transverse = Transverse(confr4p, params, logger)
        self.services = Services(confr4p, params, logger)

    #  SYSTEM  #
    def upgrade(self):
        run("apt-get update")
        self.logger.writelog("[OK] update package database")
        run("DEBIAN_FRONTEND=noninteractive apt-get upgrade -y")
        self.logger.writelog("[OK] VM upgraded")

    def conf_dns(self):
        run("echo > /etc/resolv.conf")
        self.logger.writelog("[OK] FLush resolv dns file")
        for ip in self.params['CONF']['NETWORK_DNS']:
            run("echo nameserver {dnsip} >> /etc/resolv.conf ".format(dnsip=ip))
            self.logger.writelog("[OK] IP {dnsip} added in resolv file".format(dnsip=ip))

    def conf_hostkey(self):
        try:
            run("/bin/rm -v /etc/ssh/ssh_host_*")
            self.logger.writelog("[OK] Remove old ssh host key")
            run("dpkg-reconfigure openssh-server")
            self.logger.writelog("[OK] host ssh key has been updated")
        except BaseException as e:
            self.logger.writelog("[ERROR] while update ssh host key {error}".format(error=e))
            if self.confr4p['EXITONERROR']:
                print("Error found: {error}".format(error=e))
                exit(1)

            self.services.management("sshd", "restart")

    def conf_firewall(self):
        self.transverse.sedvalue("{PUBLIC_IP}", self.params['CONF']['CONF_INTERFACES'][0]["NETWORK_IP"], "/etc/init.d/firewall")
        self.logger.writelog("[OK] Set public IP in firewall file")
        self.transverse.sedvalue("{PORT_NUMBER}", self.params['CONF']['PORT_SSH_NUMBER'], "/etc/init.d/firewall")
        self.logger.writelog("[OK] Set ssh port in firewall file")
        try:
            run("bash /etc/init.d/firewall")
            self.logger.writelog("[OK] Apply firewall file)")
        except BaseException as e:
            self.logger.writelog("[ERROR] in the firewall files: {error}".format(error=e))
            if self.confr4p['EXITONERROR']:
                print("Error found: {error}".format(error=e))
                exit(1)

    def conf_ssh(self):
        self.transverse.sedvalue("{PORT_NUMBER}", self.params['CONF']['PORT_SSH_NUMBER'], "/etc/ssh/sshd_config")
        self.logger.writelog("[OK] Change ssh port")
        self.services.management("sshd", "restart")

    def conf_sshguard(self):
        run("echo > /etc/sshguard/whitelist")
        self.logger.writelog("[OK] Flush whitelist sshguard")
        for ip in self.params['CONF']['WHITELITSTIPS']:
            run("echo {sshguardip} >> /etc/sshguard/whitelist ".format(sshguardip=ip))
            self.logger.writelog("[OK] New ip added in the sshguard whitelist: {sshguardip} ".format(sshguardip=ip))
        self.services.management("sshguard.service", "restart")

    def conf_postfix(self):
        # No try necessary here
        self.transverse.sedvalue("{servername}", self.params['CONF']['HOSTNAME'], "/etc/postfix/main.cf")
        self.logger.writelog("[OK] Set hostname in postfix file")
        self.services.management("postfix", "restart")

    def conf_dynmotd(self):
        try:
            run('if [ ! -d "/etc/update-motd.d/" ];then mkdir /etc/update-motd.d; chmod +x /etc/update-motd.d; fi')
            self.logger.writelog("[OK] Prepare motd file dir")
            run('rm -f /etc/motd')
            run('rm -f /etc/update-motd.d/*')
            self.logger.writelog("[OK] Clean motd existants files")
            run('ln -sf /var/run/motd.dynamic.new /etc/motd')
            self.logger.writelog("[OK] Set new motd")
            self.logger.writelog("[INFO] You can view this new motd at the new ssh connection")
        except BaseException as e:
            self.logger.writelog("[ERROR] while motd setting ({error})".format(error=e))
            if self.confr4p['EXITONERROR']:
                print("Error found: {error}".format(error=e))
                exit(1)

    def conf_user(self):
        for user in self.params['CONF']['USERS']:
            try:
                run('getent passwd {username}  || adduser {username} --disabled-password --gecos ""'.format(username=user["USER"]))
                self.logger.writelog("[OK] Create the new user {username}".format(username=user["USER"]))

                run('echo "{username}:{password}" | chpasswd'.format(username=user["USER"], password=user["PASSWORD"]))
                self.logger.writelog("[OK] Set password for the new user {username}".format(username=user["USER"]))

                run("mkdir -p /home/{username}/.ssh/".format(username=user["USER"]))
                self.logger.writelog("[OK] Create root dir for new user {username}".format(username=user["USER"]))

                run("echo '' > /home/{username}/.ssh/authorized_keys".format(username=user["USER"]))
                for key in user["KEY"]:
                    run("echo {keyv} >> /home/{username}/.ssh/authorized_keys".format(keyv=key, username=user["USER"]))
                    run("chmod 600 -R /home/{username}/.ssh/authorized_keys".format(username=user["USER"]))

                self.logger.writelog("[OK] Set ssh keys for {username}".format(username=user["USER"]))

                if "USERBASHRC" in self.params['SOFTS']['BASE']:
                    files_list = [
                        ['/conf/SYSTEM/bashrc', '/home/{username}/.bashrc'.format(username=user["USER"]), '0640'],
                        ['/conf/SYSTEM/bash_profile', '/home/{username}/.bash_profile'.format(username=user["USER"]), '0640']
                    ]
                    self.transverse.copyfiles(files_list)
                    self.logger.writelog("[OK] Set new bashrc for the new user {username}".format(username=user["USER"]))

                run("chown {username}: -R /home/{username}/".format(username=user["USER"]))
                self.logger.writelog("[OK] Set right for the rootdir to {username}".format(username=user["USER"]))

            except BaseException as e:
                self.logger.writelog("[ERROR] while  setting new user ({error})".format(error=e))
                if self.confr4p['EXITONERROR']:
                    print("Error found: {error}".format(error=e))
                    exit(1)

    def conf_hostname(self):
        try:
            run("echo {0}> /etc/hostname".format(self.params['CONF']['HOSTNAME']))
            self.logger.writelog("[OK] Set new hostname for {0})".format(self.params['CONF']['HOSTNAME']))
            self.logger.writelog("[INFO] To apply this new hostname, you must reboot")
        except BaseException as e:
            self.logger.writelog("[ERROR] while hostfile settings ({error})".format(error=e))
            if self.confr4p['EXITONERROR']:
                print("Error found: {error}".format(error=e))
                exit(1)

    def conf_hostsfile(self):
        try:
            run("echo > /etc/hosts")
            self.logger.writelog("[OK] Flush hosts file")
            run("echo 127.0.0.1 localhost >> /etc/hosts")
            self.logger.writelog("[OK] Set localhost in host file")
            run("echo {0} {1} >> /etc/hosts".format(self.params['CONF']['CONF_INTERFACES'][0]["NETWORK_IP"], self.params['CONF']['HOSTNAME']))
            self.logger.writelog("[OK] Change hostfile with {0} {1})".format(self.params['CONF']['CONF_INTERFACES'][0]["NETWORK_IP"], self.params['CONF']['HOSTNAME']))
        except BaseException as e:
            self.logger.writelog("[ERROR] while hostfile settings ({error})".format(error=e))
            if self.confr4p['EXITONERROR']:
                print("Error found: {error}".format(error=e))
                exit(1)

    def host_type(self):
        # No try necessary here
        run('uname -s')

    def getinsterfacesname(self):
        nameint = run("dmesg |grep renamed.*eth|awk -F' ' '{print substr($5,0,length($5))}'")
        self.logger.writelog("[OK] Get interface name {0}".format(nameint))
        return nameint

    def conf_interfaces(self):
        currentdate = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')
        run("cp /etc/network/interfaces /etc/network/interfaces.{date}".format(date=currentdate))

        self.transverse.copyfiles([
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
                device=self.params['CONF']['CONF_INTERFACES'][0]["DEVISE"],
                mode=self.params['CONF']['CONF_INTERFACES'][0]["MODE"],
                action="add",
                address=self.params['CONF']['CONF_INTERFACES'][0]["NETWORK_IP"],
                netmask=self.params['CONF']['CONF_INTERFACES'][0]["NETWORK_MASK"],
                gateway=self.params['CONF']['CONF_INTERFACES'][0]["NETWORK_GW"]
            )
        )

    def install_packages(self, roles):
        config_file = os.path.join(self.confr4p['CONF_ROOT']+"/"+self.confr4p["CONF_FILE"])
        config = ConfigParser.SafeConfigParser()
        config.read(config_file)
        print(config_file)
        for role in roles:
            for package in config.get(role, 'packages').split(' '):
                try:
                    run("DEBIAN_FRONTEND=noninteractive apt-get install -y {0}".format(package))
                    self.logger.writelog("[OK] Installation package {package}".format(package=package))
                except BaseException as e:
                    self.logger.writelog("[ERROR] Installation package {package} ({error})".format(
                        package=package, error=e
                        )
                    )
                    if self.confr4p['EXITONERROR']:
                        print("Error found: {error}".format(error=e))
                        exit(1)
