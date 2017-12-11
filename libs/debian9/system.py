"""
Class : System
Version : 1
Author : Tlams
Revision : 1.0
Last update : Dec 2017
"""

import ConfigParser

class System:

    #  SYSTEM  #
    def upgrade(self):
        run("apt-get update")
        Logger.writelog("[OK] update package database")
        run("apt-get upgrade -y")
        Logger.writelog("[OK] VM upgraded")


    def conf_dns(self, ips):
        run("echo > /etc/resolv.conf")
        Logger.writelog("[OK] FLush resolv dns file")
        for ip in ips:
            run("echo nameserver {dnsip} >> /etc/resolv.conf ".format(dnsip=ip))
            Logger.writelog("[OK] IP {dnsip} added in resolv file".format(dnsip=ip))


    def conf_hostkey(self):
        try:
            run("/bin/rm -v /etc/ssh/ssh_host_*")
            Logger.writelog("[OK] Remove old ssh host key")
            run("dpkg-reconfigure openssh-server")
            Logger.writelog("[OK] host ssh key has been updated")
        except BaseException as e:
            Logger.writelog("[ERROR] while update ssh host key {error}".format(error=e))
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)

        service_gestion("sshd", "restart")


    def conf_firewall(self, PORT_SSH_NUMBER, CONF_INTERFACES):
        sedvalue("{PUBLIC_IP}", CONF_INTERFACES["NETWORK_IP"], "/etc/init.d/firewall")
        Logger.writelog("[OK] Set public IP in firewall file")
        sedvalue("{PORT_NUMBER}", PORT_SSH_NUMBER, "/etc/init.d/firewall")
        Logger.writelog("[OK] Set ssh port in firewall file")
        try:
            run("bash /etc/init.d/firewall")
            Logger.writelog("[OK] Apply firewall file)")
        except BaseException as e:
            Logger.writelog("[ERROR] in the firewall files: {error}".format(error=e))
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)


    def conf_ssh(self, PORT_SSH_NUMBER):
        sedvalue("{PORT_NUMBER}", PORT_SSH_NUMBER, "/etc/ssh/sshd_config")
        Logger.writelog("[OK] Change ssh port")
        service_gestion("sshd", "restart")

    def conf_sshguard(self, ips):
        run("echo > /etc/sshguard/whitelist")
        Logger.writelog("[OK] Flush whitelist sshguard")
        for ip in ips:
            run("echo {sshguardip} >> /etc/sshguard/whitelist ".format(sshguardip=ip))
            Logger.writelog("[OK] New ip added in the sshguard whitelist: {sshguardip} ".format(sshguardip=ip))
        service_gestion("sshguard.service", "restart")


    def conf_postfix(self, HOSTNAME):
        # No try necessary here
        sedvalue("{servername}", HOSTNAME, "/etc/postfix/main.cf")
        Logger.writelog("[OK] Set hostname in postfix file")
        service_gestion("postfix", "restart")


    def conf_dynmotd():
        try:
            run('if [ ! -d "/etc/update-motd.d/" ];then mkdir /etc/update-motd.d; chmod +x /etc/update-motd.d; fi')
            Logger.writelog("[OK] Prepare motd file dir")
            run('rm -f /etc/motd')
            run('rm -f /etc/update-motd.d/*')
            Logger.writelog("[OK] Clean motd existants files")
            run('ln -sf /var/run/motd.dynamic.new /etc/motd')
            Logger.writelog("[OK] Set new motd")
            Logger.writelog("[INFO] You can view this new motd at the new ssh connection")
        except BaseException as e:
            Logger.writelog("[ERROR] while motd setting ({error})".format(error=e))
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)


    def conf_user(self, CONF_ROOT, ACTIONS, user):
        try:
            run('getent passwd {username}  || adduser {username} --disabled-password --gecos ""'.format(username=user["USER"]))
            Logger.writelog("[OK] Create the new user {username}".format(username=user["USER"]))

            run('echo "{username}:{password}" | chpasswd'.format(username=user["USER"], password=user["PASSWORD"]))
            Logger.writelog("[OK] Set password for the new user {username}".format(username=user["USER"]))

            run("mkdir -p /home/{username}/.ssh/".format(username=user["USER"]))
            Logger.writelog("[OK] Create root dir for new user {username}".format(username=user["USER"]))

            run("echo '' > /home/{username}/.ssh/authorized_keys".format(username=user["USER"]))
            for key in user["KEY"]:
                run("echo {keyv} >> /home/{username}/.ssh/authorized_keys".format(keyv=key, username=user["USER"]))
                run("chmod 600 -R /home/{username}/.ssh/authorized_keys".format(username=user["USER"]))

            Logger.writelog("[OK] Set ssh keys for {username}".format(username=user["USER"]))

            if "USERBASHRC" in ACTIONS:
                files_list = [
                    ['/conf/SYSTEM/bashrc', '/home/{username}/.bashrc'.format(username=user["USER"]), '0640'],
                    ['/conf/SYSTEM/bash_profile', '/home/{username}/.bash_profile'.format(username=user["USER"]), '0640']
                ]
                copyfiles(CONF_ROOT, files_list)
                Logger.writelog("[OK] Set new bashrc for the new user {username}".format(username=user["USER"]))

            run("chown {username}: -R /home/{username}/".format(username=user["USER"]))
            Logger.writelog("[OK] Set right for the rootdir to {username}".format(username=user["USER"]))

        except BaseException as e:
            Logger.writelog("[ERROR] while  setting new user ({error})".format(error=e))
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)


    def conf_hostname(self, hostname):
        try:
            run("echo {0}> /etc/hostname".format(hostname))
            Logger.writelog("[OK] Set new hostname for {0})".format(hostname))
            Logger.writelog("[INFO] To apply this new hostname, you must reboot")
        except BaseException as e:
            Logger.writelog("[ERROR] while hostfile settings ({error})".format(error=e))
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)


    def conf_hostsfile(self, hostname, ip):
        try:
            run("echo > /etc/hosts")
            Logger.writelog("[OK] Flush hosts file")
            run("echo 127.0.0.1 localhost >> /etc/hosts")
            Logger.writelog("[OK] Set localhost in host file")
            run("echo {0} {1} >> /etc/hosts".format(ip, hostname))
            Logger.writelog("[OK] Change hostfile with {0} {1})".format(ip, hostname))
        except BaseException as e:
            Logger.writelog("[ERROR] while hostfile settings ({error})".format(error=e))
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)


    def host_type():
        # No try necessary here
        run('uname -s')


    def getinsterfacesname():
        nameint = run("dmesg |grep renamed.*eth|awk -F' ' '{print substr($5,0,length($5)-1)}'")
        Logger.writelog("[OK] Get interface name {0}".format(nameint))
        return nameint


    def conf_interfaces(self, CONF_ROOT, CONF_INTERFACES):
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


    def install_packages(self, conf_root, roles):
        config_file = os.path.join(conf_root % env)
        config = ConfigParser.SafeConfigParser()
        config.read(config_file)
        for role in roles:
            for package in config.get(role, 'packages').split(' '):
                try:
                    run("apt-get install -y {0}".format(package))
                    Logger.writelog("[OK] Installation package {package}".format(package=package))
                except BaseException as e:
                    Logger.writelog("[ERROR] Installation package {package} ({error})".format(
                        package=package, error=e
                        )
                    )
                    if EXITONERROR:
                        print("Error found: {error}".format(error=e))
                        exit(1)
