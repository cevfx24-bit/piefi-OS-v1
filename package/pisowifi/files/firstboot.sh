#!/bin/sh
[ -f /etc/piefi-configured ] && exit 0
uci set system.@system[0].hostname='pieFI-OS'
uci commit system
mkdir -p /etc/nginx/conf.d
cat > /etc/nginx/conf.d/pisowifi.conf <<'NGINX'
server { listen 80 default_server; location / { return 302 http://10.0.0.1:8080/; } }
server { listen 10.0.0.1:80; location /admin { proxy_pass http://127.0.0.1:8081/; } }
NGINX
touch /etc/piefi-configured
exit 0
