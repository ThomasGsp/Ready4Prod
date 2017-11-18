# Ready4Prod


* Author : Tlams
* Date : 2017/2018
* Status: Dev
* Object :   Massive LXC CT / KVM deploy system for proxmox hypervisor.

## Quick start

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

    (....)

```

### Play Fabric's file:
``` bash
fab -f install_packages.py deploy_base_lamp -H 172.16.0.207
```