#!/bin/bash

# Process count
PROCCOUNT=$( ps -Afl | wc -l )
PROCCOUNT=$( expr $PROCCOUNT - 5 )

# Uptime
UPTIME=$(</proc/uptime)
UPTIME=${UPTIME%%.*}
SECONDS=$(( UPTIME%60 ))
MINUTES=$(( UPTIME/60%60 ))
HOURS=$(( UPTIME/60/60%24 ))
DAYS=$(( UPTIME/60/60/24 ))

# SYSTEM INFO
# Hostname (UPPERCASE)
HOSTNAME=$( echo $(hostname)  | tr '[a-z]' '[A-Z]' )
# IP Address (list all ip addresses)
IP_ADDRESS=$(echo $(ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' |  sed ':a;N;$!ba;s/\n/ , /g') )
# System : Description of the distribution
SYSTEM=$(echo $(lsb_release -d | awk -F':' '{print $2}' | sed 's/^\s*//g') )
# Kernel release
KERNEL=$( echo $(uname -r) )
# CPU Info
CPU_INFO=$(echo $(more /proc/cpuinfo | grep processor | wc -l ) "x" $(more /proc/cpuinfo | grep 'model name' | uniq |awk -F":"  '{print $2}') )
# Total Memory
MEMORY=$(echo $(free -m |grep Mem: | awk -F " " '{print $2}') MO)
# Memory Used
MEMORY_USED=$(echo $(free -m |grep Mem: | awk -F " " '{print $3}') MO)
# User home
USERL=$(whoami)
HOMEDIR=$(getent passwd "$USERL" | cut -d: -f6 )

echo -e "
################################ ALERT! ###################################
#                                                                         #
#  You are entering into a restricted area! Your IP, Login Time,          #
#  Username has been noted and has been sent to the server administrator. #
#  This service is restricted to authorized users only. All activities on #
#  this system are logged.                                                #
#                                                                         #
#  Unauthorized access will be fully investigated and reported to the     #
#  appropriate law enforcement agencies.                                  #
#                                                                         #
###########################################################################

\033[1;31m+++++++++++++++++: \033[0;37mSystem Data\033[1;31m :+++++++++++++++++++
+ \033[0;37mHostname \033[1;31m= \033[1;32m$HOSTNAME
\033[1;31m+ \033[0;37mAddress \033[1;31m= \033[1;32m$IP_ADDRESS
\033[1;31m+ \033[0;37mSystem \033[1;31m= \033[1;32m$SYSTEM
\033[1;31m+ \033[0;37mKernel \033[1;31m= \033[1;32m$KERNEL
\033[1;31m+ \033[0;37mUptime \033[1;31m= \033[1;32m$DAYS days, $HOURS hours, $MINUTES minutes, $SECONDS seconds
\033[1;31m+ \033[0;37mCPU Info \033[1;31m= \033[1;32m$CPU_INFO
\033[1;31m+ \033[0;37mMemory \033[1;31m= \033[1;32m$MEMORY
\033[1;31m+ \033[0;37mMemory Used \033[1;31m= \033[1;32m$MEMORY_USED
\033[1;31m+++++++++++++++++: \033[0;37mUser Data\033[1;31m :+++++++++++++++++++++
+ \033[0;37mUsername \033[1;31m= \033[1;32m`whoami`
\033[1;31m+ \033[0;37mUser home dir \033[1;31m= \033[1;32m$HOMEDIR
\033[1;31m+++++++++++++++++: \033[0;37mInformation/Role\033[1;31m :++++++++++++++
\033[1;31m+ \033[0;37mServer \033[1;31m= \033[1;32m- LAMP Server
\033[1;31m+++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m"
