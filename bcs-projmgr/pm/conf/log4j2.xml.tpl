<?xml version="1.0" encoding="utf-8"?>
<configuration status="error">
    <properties>
        <property name="CONSOLE_PATTERN">%d{yyyy-MM-dd HH:mm:ss} %blue{[%12.12t]} %highlight{%5level} %cyan{%-40.40c{1.}} %msg%n%throwable</property>
        <property name="FILE_PATTERN">%d{yyyy-MM-dd HH:mm:ss} [%12.12t] %5level %-40.40c{1.} %msg%n%throwable</property>
    </properties>

    <appenders>
        <Console name="Console" target="SYSTEM_OUT">
            <PatternLayout pattern="${CONSOLE_PATTERN}" />
        </Console>
        <RollingFile name="RollingFile" fileName="__LOGGER_PATH__/project.log" filePattern="__LOGGER_PATH__/project-%d{MM-dd-yy}.log.gz">
            <PatternLayout pattern="${FILE_PATTERN}"/>
            <Policies>
                <SizeBasedTriggeringPolicy size="250MB"/>
                <CronTriggeringPolicy schedule="0 0 0 * * ?"/>
            </Policies>
        </RollingFile>
    </appenders>

    <loggers>
        <logger name="org.hibernate" level="error" additivity="false">
            <appender-ref ref="Console"/>
        </logger>
        <root level="info">
            <appender-ref ref="Console" />
            <appender-ref ref="RollingFile" />
        </root>
    </loggers>
</configuration>