#!/usr/bin/env bash

# VAR
PUBLICIP={PUBLIC_IP}
IPWHITELIST=""

#### GENERIC RULES ####
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Ne pas casser les connexions etablies
iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT

#Interdire toute connexion
iptables -t filter -P INPUT DROP
iptables -t filter -P FORWARD ACCEPT
iptables -t filter -P OUTPUT DROP

# Autoriser loopback
iptables -t filter -A INPUT -i lo -j ACCEPT
iptables -t filter -A OUTPUT -o lo -j ACCEPT

# ICMP (Ping) Limite
iptables -A INPUT -p icmp --icmp-type echo-request -m recent --set
iptables -A INPUT -p icmp --icmp-type echo-request -m recent --update --seconds 10 --hitcount 5 -j ACCEPT

# SSH
iptables -t filter -A INPUT -p tcp --dport {PORT_NUMBER} -j ACCEPT

# DNS
iptables -t filter -A OUTPUT -p udp --dport 53 -j ACCEPT

# FTP Sortant
iptables -t filter -A OUTPUT -p tcp --dport 21 -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --dport 20 -j ACCEPT

#UPDATE
iptables -t filter -A OUTPUT -p tcp --dport 80 -j ACCEPT
iptables -t filter -A OUTPUT -p tcp --dport 443 -j ACCEPT

# OUTPUT FTP
iptables -t filter  -A OUTPUT -p tcp -m tcp --dport 21 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
iptables -t filter  -A OUTPUT -p tcp -m tcp --dport 20 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
iptables -t filter  -A OUTPUT -p tcp -m tcp --sport 1024:65535 --dport 20:65535 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT

# INPUT FTP
iptables -t filter  -A INPUT -p tcp -m tcp --dport 21 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
iptables -t filter  -A INPUT -p tcp -m tcp --dport 20 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
iptables -t filter  -A INPUT -p tcp -m tcp --sport 1024:65535 --dport 20:65535 -m conntrack --ctstate NEW,ESTABLISHED -j ACCEPT
