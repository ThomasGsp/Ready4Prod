#!/usr/bin/env bash

DOMAIN=$1

certbot certonly --standalone --preferred-challenges http --http-01-port 54321 -d ${DOMAIN}
cat /etc/letsencrypt/live/${DOMAIN}/fullchain.pem /etc/letsencrypt/live/${DOMAIN}/privkey.pem > /opt/certbot/${DOMAIN}.pem