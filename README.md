# Ready4Prod

Build your linux LAMP server.

* Author : Tlams
* Date : Nov 2017
* Status: Stable
* Website: https://www.ready4prod.com/


##### Stack available:
* Basic LAMP

### Features
* Upgrade VM
* Change hostname
* Change hosts file
* Change ssh host key
* Change DNS
* New motd (see example on bottom)
* Add an IPTABLES firewall
* Configure VIM
* Configure network
* Configure ssh server (port & others)
* Install a ssh guard (brute force...)
* New bashrc
* Install lamp stack (basic stack or avanced stack)
* Configure LAMP softwares (apache, mariadb, php...)
* Configure smtp server (postfix)
* Configure log rotation
* Create basic vhosts

##### Next features:
* New stack with cache, ssl and fpm-pools

## Quick start

### Limitations
* Do not use on a existent server (in production)!

### Requirement:
* Linux (Debian 9) server, with full root access
* Python with fabric (http://www.fabfile.org/)


### Clone repository:
``` bash
git clone git@github.com:ThomasGsp/Ready4Prod.git
```

### Edit/configure with yours settings:
``` bash

vi install_packages.py
    (....)


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

    (....)

```

### Play Fabric's file:
``` bash
fab -f install_packages.py deploy_base_lamp -H <ip_srv>
```



### Results:
#### bashrc 
![bashrc](./img/lamp_base_bashrc.png)
#### iptables rules 
![iptables](./img/lamp_base_iptables.png)
#### motd
![motd](./img/lamp_base_motd.png)
#### netstat (base lamp)
![netstat](./img/lamp_base_netstat.png)




##### External sources:
* bashrc : http://mindnugget.com/bashrc/.bashrc
* motd www.tomzone.fr/creation-dun-motd-dynamique/
* awk script for network configuration https://github.com/JoeKuan/Network-Interfaces-Script
