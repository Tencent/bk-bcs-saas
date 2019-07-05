ssl_certificate __DEVOPS_CRT__;
ssl_certificate_key __DEVOPS_KEY__;
ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_ciphers HIGH:!aNULL:!MD5;
error_page 497  https://$host$uri?$args;
#add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
