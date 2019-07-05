/*
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*
*/

subprojects {
    def moduleName = name.split('-')[1]
    def databaseName = moduleName
    def mysqlEnv = System.getProperty("mysqlEnv")
    apply plugin: 'nu.studer.jooq'

    dependencies {
        compile "org.jooq:jooq"
        jooqRuntime "mysql:mysql-connector-java"
    }

    jooq {
        genenrate(sourceSets.main) {

            jdbc {
                driver = 'com.mysql.jdbc.Driver'
                def mysqlURL = System.getProperty("mysqlURL")


                def mysqlUser = ""
                def mysqlPasswd = ""
                if (mysqlURL == null) {
                    println "use default local mysql database."
                    mysqlURL = "__MYSQL_IP__:__MYSQL_PORT__"
                    mysqlUser = '__MYSQL_USER__'
                    mysqlPasswd = '__MYSQL_PASS__'
                }
                else {
                    mysqlUser = System.getProperty("mysqlUser")
                    mysqlPasswd = System.getProperty("mysqlPasswd")
                }

                url = "jdbc:mysql://${mysqlURL}/devops_${databaseName}?useSSL=false"
                user = mysqlUser
                password = mysqlPasswd
            }

            generator {
                name = 'org.jooq.util.DefaultGenerator'

                database {
                    name = 'org.jooq.util.mysql.MySQLDatabase'
                    inputSchema = "devops_${databaseName}"
                }

                strategy {
                    name = 'org.jooq.util.DefaultGeneratorStrategy'
                }

                generate {
                    relations = false
                    deprecated = false
                    fluentSetters = true
                    generatedAnnotation = false
                    javaTimeTypes = true
                }

                target {
                    packageName = "com.tencent.devops.model.${moduleName}"
                }
            }
        }
    }
}