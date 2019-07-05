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

package com.tencent.devops.common.service;

import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.core.appender.ConsoleAppender;
import org.apache.logging.log4j.core.config.builder.api.*;
import org.apache.logging.log4j.core.config.builder.impl.BuiltConfiguration;
import org.springframework.context.ApplicationContextInitializer;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.io.ClassPathResource;

import java.io.File;
import java.net.URI;

public class Log4j2Initializer implements ApplicationContextInitializer<ConfigurableApplicationContext> {
    private String CONFIG_FILE = "log4j2.xml";
    private String CONFIG_SPRING_FILE = "log4j2-spring.xml";

    @Override
    public void initialize(ConfigurableApplicationContext applicationContext) {
        try {
            ConfigurableEnvironment environment = applicationContext.getEnvironment();

            String loggerFileName = System.getProperty("logger.config.file");
            if (isFileExisted(loggerFileName)) {
                setConfigLocation(new File(loggerFileName).toURI());
                return;
            }

            String sysLoggerFileName = System.getProperty("logger.config.file");
            if (isFileExisted(sysLoggerFileName)) {
                setConfigLocation(new File(sysLoggerFileName).toURI());
                return;
            }

            ClassPathResource configFileClasspathRes = new ClassPathResource(CONFIG_FILE);
            if (configFileClasspathRes.exists()) {
                setConfigLocation(configFileClasspathRes.getURI());
                return;
            }

            ClassPathResource configSpringFileClasspathRes = new ClassPathResource(CONFIG_SPRING_FILE);
            if (configSpringFileClasspathRes.exists()) {
                setConfigLocation(configSpringFileClasspathRes.getURI());
                return;
            }

            configLog4j2(environment);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private boolean isFileExisted(String fileName) {
        if (fileName != null) {
            File file = new File(fileName);
            return file.exists();
        }
        return false;
    }

    private void setConfigLocation(URI uri) {
        LoggerContext loggerContext = (LoggerContext)LogManager.getContext(false);
        loggerContext.setConfigLocation(uri);
    }

    private void configLog4j2(ConfigurableEnvironment environment) {
        String appName = environment.getProperty("spring.application.name");

        ConfigurationBuilder<BuiltConfiguration> builder = ConfigurationBuilderFactory.newConfigurationBuilder();
        builder.setStatusLevel(Level.ERROR);
        builder.setConfigurationName("Config");
        builder.setPackages(ExceptionAppender.class.getPackage().getName());

        LayoutComponentBuilder consoleLayoutBuilder = builder.newLayout("PatternLayout")
                .addAttribute("pattern", "%d{yyyy-MM-dd HH:mm:ss,SSS}m %blue{[%12.12t]} %highlight{%5level} %cyan{%-40.40c{1.} %-3.3L} %msg%n%throwable")
                .addAttribute("charset", "UTF-8");

        // console日志输出
        AppenderComponentBuilder appenderBuilder = builder.newAppender("Stdout", "CONSOLE").addAttribute("target",
                ConsoleAppender.Target.SYSTEM_OUT)
                .add(consoleLayoutBuilder);
        // 异常日志输出
        AppenderComponentBuilder exceptionAppender = builder.newAppender("Exception", "Exception")
                .add(consoleLayoutBuilder);

        builder.add(appenderBuilder);
        builder.add(exceptionAppender);

        // 过滤hibernate输出
        builder.add(builder.newLogger("org.hibernate", Level.ERROR)
                .add(builder.newAppenderRef("Stdout"))
                .addAttribute("additivity", false ));

        // 有profile时才将日志输出到文件中
        if (environment.getActiveProfiles().length == 0 || appName.equals("bootstrap")) {
            builder.add(builder.newRootLogger(Level.INFO)
                    .add(builder.newAppenderRef("Exception"))
                    .add(builder.newAppenderRef("Stdout")));
        } else {
            LayoutComponentBuilder rollingLayoutBuilder = builder.newLayout("PatternLayout")
                    .addAttribute("pattern", "%d{yyyy.MM.dd HH:mm:ss,SSS} [%12.12t] %5level %-40.40c{1.} %-3.3L %msg%n%throwable")
                    .addAttribute("charset", "UTF-8");

            ComponentBuilder triggeringPolicy = builder.newComponent("Policies")
                    .addComponent(builder.newComponent("CronTriggeringPolicy").addAttribute("schedule", "0 0 0 * * ?"))
                    .addComponent(builder.newComponent("SizeBasedTriggeringPolicy").addAttribute("size", "100 MB"));

            appenderBuilder = builder.newAppender("Rolling", "RollingFile")
                    .addAttribute("fileName", "/data1/logs/bkdevops/" + appName + "/" + appName + ".log")
                    .addAttribute("filePattern", "/data1/logs/bkdevops/" +appName + "/" + appName + "-%d{MM-dd-yy}.log.gz")
                    .add(rollingLayoutBuilder)
                    .addComponent(triggeringPolicy);
            builder.add(appenderBuilder);

            builder.add(builder.newRootLogger(Level.INFO )
                    .add(builder.newAppenderRef("Exception"))
                    .add(builder.newAppenderRef("Rolling")));

            builder.add(builder.newLogger("org.activiti.engine", Level.INFO)
                    .add(builder.newAppenderRef("Rolling"))
                    .addAttribute("additivity", false ));


        }

        LoggerContext loggerContext = (LoggerContext) LogManager.getContext(false);
        loggerContext.start(builder.build());
    }
}
