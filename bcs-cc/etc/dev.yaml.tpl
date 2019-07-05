version: v1.0.0
location: Local
debug: true
run_env: "dev"
available_environment_flags:
    - prod
database:
  type: mysql
  host: svr-mariadb
  port: 3306
  user: root
  password: "open-bcs-saas"
  db_name: "bcs-cc"
  charset: utf8
  max_idle_conns: 10
  max_open_conns: 100
confcenter:
  host: 0.0.0.0
  port: 8080
logging:
  level: info
  file_dir: "/data/logs/bcs-cc"
  stderr: true
  log_to_redis: false
authconf:
  host: "__IAM_HOST__"
  proxy: "__HTTP_PROXY__"
  auth_token_path: "/bkiam/api/v1/auth/access-tokens"
  auth_project_path: "/bkiam/api/v1/perm/scope_type/project/authorized-scopes/"
  auth_verify_path: "/bkiam/api/v1/auth/access-tokens/verify"
apigwconf:
  identity_from_jwt: false
  host: "__APIGW_HOST__"
  proxy: "__HTTP_PROXY__"
interval: 300
disable_encrypt: true
app_code: "bk_bcs"
app_secret: "__BCS_CC_APP_TOKEN__"
jwt_path: ""