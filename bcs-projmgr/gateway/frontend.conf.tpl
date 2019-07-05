server {
  listen "80";
  server_name "__DEVOPS_HOST__";
  client_max_body_size 5G;

  access_log $log_dir/frontend.devops.access.log devops_format;
  error_log ./logs/frontend.devops.error.log;

  #设置通用变量
  include set.conf;

#  ### ssl config begin ###
#  listen 443 ssl;
#  include ./conf/conf/devops.ssl;
#  # force https-redirects
#  if ($scheme = http) {
#   return 301 https://$server_name$request_uri;
#  }
#  ### ssl config end ###

  gzip on;
  gzip_min_length 1k;
  gzip_buffers 4 16k;
  gzip_comp_level 5;
  gzip_types text/plain application/javascript application/x-javascript text/css application/xml text/javascript application/x-httpd-php image/jpeg image/gif image/png;

  #将错误统一处理成json格式返回
  include error.json.conf;

  #前端导航
  root $static_dir;
  index index.html index.htm;

  location = / {
    header_filter_by_lua_file './conf/lua/cors_filter.lua';
    add_header Cache-Control no-cache;
    rewrite ^/(.*) http://$host/console/ redirect;
  }

  location / {
    header_filter_by_lua_file './conf/lua/cors_filter.lua';
    add_header Cache-Control max-age=2592000;
    try_files $uri  @fallback;
  }

  location ~ ^/(console)/(.*)$ {
    header_filter_by_lua_file './conf/lua/cors_filter.lua';
    add_header Cache-Control max-age=2592000;
    try_files $uri  @fallback;
  }

  location ~ ^/(console)$ {
    header_filter_by_lua_file './conf/lua/cors_filter.lua';
    add_header Cache-Control max-age=2592000;
    try_files $uri  @fallback;
  }

  location @fallback {
    add_header Cache-Control max-age=2592000;
    try_files /console$uri  @fallback_index ;
  }
  location @fallback_index {
    add_header Cache-Control no-cache;
    try_files $uri/index.html /console$uri/index.html  @fallback_default ;
  }

  # html文件不缓存
  location @fallback_default {
    add_header Cache-Control no-cache;
    set $try_path "/console/404.html";
    if ($uri ~ ^/(console)/(.*)) { 
      set $try_path "/$1/index.html";
    }
    rewrite .* $try_path break;
  }



}
