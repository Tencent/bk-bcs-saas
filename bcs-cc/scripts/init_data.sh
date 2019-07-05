#!/bin/bash
# 仅限本地开发测试使用


DB_NAME=bcs-cc
CURR_TIME=$(date "+%Y-%m-%d %H:%M:%S")


# 从社区版获取配置信息
# 在中控机上执行如下命令，获取相应的配置
# 获取区域配置
# ssh $BCS_CC_IP 'cat /data/bkce/etc/bcs/cc-area.json'|tr -d '\n
# 获取zk配置
# ssh $BCS_CC_IP 'cat /data/bkce/etc/bcs/cc-zk.json'|tr -d '\n
# 获取k8s版本
# echo $K8S_VERSION
# 获取k8s版本配置
# ssh $BCS_CC_IP 'cat /data/bkce/etc/bcs/cc-k8s.json'|tr -d '\n
# 获取mesos版本
# echo $MESOS_VERSION
# 获取mesos版本配置
# ssh $BCS_CC_IP 'cat /data/bkce/etc/bcs/cc-mesos.json'|tr -d '\n

# 填写区域配置信息
AREA_CONFIG=''
# 填写zk配置信息
ZK_CONFIG=''
# 填写k8s版本配置
K8S_CONFIG=''
# 填写k8s版本
K8S_VERSION=''
# 填写mesos配置
MESOS_CONFIG=''
# 填写mesos版本配置
MESOS_VERSION=''

# 检查配置是否为空
function check_param_empty() {
    if [ ! $1 ] || [ ! $2 ] || [ ! $3 ] || [ ! $4 ] || [ ! $5 ] || [ ! $6 ]; then
        echo "params is empty, please check AREA_CONFIG/ZK_CONFIG/K8S_CONFIG/K8S_VERSION/MESOS_CONFIG/MESOS_VERSION"
        exit 1
    fi
}

function insert_data(){
    INSERT_AREA="INSERT INTO areas (created_at, updated_at, name, chinese_name, configuration) VALUES('$CURR_TIME', '$CURR_TIME', 'area', '区域', '$AREA_CONFIG') ON DUPLICATE KEY UPDATE configuration='$AREA_CONFIG',created_at='$CURR_TIME', updated_at='$CURR_TIME'";
    INSERT_ZK="INSERT INTO zookeeper_configs (created_at, updated_at, name, zookeeper, bcs_zookeeper, environment, creator) VALUES('$CURR_TIME', '$CURR_TIME', 'zk', '$ZK_CONFIG', '$ZK_CONFIG', 'prod', 'admin') ON DUPLICATE KEY UPDATE zookeeper='$ZK_CONFIG', bcs_zookeeper='$ZK_CONFIG',created_at='$CURR_TIME', updated_at='$CURR_TIME';"
    INSERT_K8S="INSERT INTO base_versions (created_at, updated_at, creator, version, configure, environment, kind) VALUES('$CURR_TIME', '$CURR_TIME', 'admin', '$K8S_VERSION', '$K8S_CONFIG', 'prod', 'k8s') ON DUPLICATE KEY UPDATE configure='$K8S_CONFIG', created_at='$CURR_TIME', updated_at='$CURR_TIME';"
    INSERT_MESOS="INSERT INTO base_versions (created_at, updated_at, creator, version, configure, environment, kind) VALUES('$CURR_TIME', '$CURR_TIME', 'admin', '$MESOS_VERSION', '$MESOS_CONFIG', 'prod', 'mesos') ON DUPLICATE KEY UPDATE configure='$MESOS_CONFIG', created_at='$CURR_TIME', updated_at='$CURR_TIME';"

    docker-compose exec svr-mariadb mysql -uroot -e "use $DB_NAME;$INSERT_AREA" || exit 1
    docker-compose exec svr-mariadb mysql -uroot -e "use $DB_NAME;$INSERT_ZK" || exit 1
    docker-compose exec svr-mariadb mysql -uroot -e "use $DB_NAME;$INSERT_K8S" || exit 1
    docker-compose exec svr-mariadb mysql -uroot -e "use $DB_NAME;$INSERT_MESOS" || exit 1

    echo "success!"
}

check_param_empty $AREA_CONFIG $ZK_CONFIG $K8S_CONFIG $K8S_VERSION $MESOS_CONFIG $MESOS_VERSION

insert_data