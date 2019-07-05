# -*- coding: utf-8 -*-
#
# Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
# Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
import logging

from backend.apps.paas_monitor import constant
from django.db import models

logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    """Model with 'created' and 'updated' fields.
    """
    creator = models.CharField(u"创建者", max_length=32)
    updator = models.CharField(u"更新者", max_length=32)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        managed = True


class UserGroupManager(models.Manager):
    """Manager for UserGroup
    """

    def get_queryset(self):
        return super(UserGroupManager, self).get_queryset().filter(is_deleted=False)


class UserGroup(BaseModel):
    """用户组
    """
    project_id = models.CharField(u"项目ID", max_length=32)
    name = models.CharField(u"名称", max_length=255)
    users = models.TextField(u"用户", help_text=u"多个用户以分号;隔开", blank=True, null=True)
    desc = models.TextField(u"描述", default='', blank=True, null=True)

    objects = UserGroupManager()
    default_objects = models.Manager()

    @property
    def user_list(self):
        return self.users.split(';') if self.users else []

    class Meta:
        unique_together = ("project_id", "name")
        ordering = ('-id',)


class MetricSource(BaseModel):
    """指标维度静态表
    """
    kind = models.CharField(u"针对的容器编排类型", max_length=32, choices=constant.MetricBelongProjectKindEnum.get_choices())
    category = models.CharField(u"指标分组", max_length=63, choices=constant.MetricCategoryEnum.get_choices())
    dimension = models.CharField(u"维度", max_length=63, choices=constant.DimensionEnum.get_choices())
    name = models.CharField(u"指标名称", max_length=128)
    metric_type = models.CharField(u"基础指标类型", max_length=63, choices=constant.MetricTypeEnum.get_choices())
    data_src = models.CharField(u"数据来源", max_length=32, choices=constant.MonitorDataSrcEnum.get_choices())
    # 以下6个字段，后续可用Json表示，对于不同数据源[bkdata(容器和主机服务可用), es(日志), kafka(事件)]，查询规则可能不同
    result_table_id = models.CharField(u"数据表", max_length=255, blank=True, null=True)
    metric_field = models.CharField(u"指标字段", max_length=255)
    dimension_field = models.CharField(u"维度字段", max_length=255, help_text="多个字段用英文逗号分隔")
    metric_field_value_type = models.CharField(u"指标值数据类型", max_length=32)
    conversion = models.FloatField(u"单位转换除数", blank=True, default=1)
    conversion_unit = models.CharField(u"转换后的单位", max_length=32)
    aggregators = models.CharField(u"可选择聚合函数", max_length=255, default="",
                                   help_text="多个聚合函数（'avg', 'min', 'max', 'sum', 'count'）用英文逗号分隔")
    intervals = models.CharField(u"可选择的聚合时间", max_length=255, default="",
                                 help_text="多个时间用英文逗号分隔")

    def __str__(self):
        return '%s[%s]<%s, %s>' % (self.name, self.kind, self.category, self.dimension)


class AlarmConfigManager(models.Manager):
    """Manager for AlarmConfig
    """

    def get_queryset(self):
        return super(AlarmConfigManager, self).get_queryset().filter(is_deleted=False)


class AlarmConfig(BaseModel):
    """警报策略配置
    """
    cc_biz_id = models.CharField(u"cc业务ID", max_length=32)
    project_id = models.CharField(u"项目ID", max_length=32)
    name = models.CharField(u"名称", max_length=255)
    desc = models.TextField(u"描述")
    # 状态信息由监控后台写入
    status = models.CharField(u"状态", max_length=32, null=True, blank=True, choices=constant.ALARM_STATUS_CHOICE,
                              default='created')
    status_time = models.DateTimeField(u"状态更新时间", null=True, blank=True)

    # 指标分组/指标维度/指标源ID/监控范围/统计源信息
    category = models.CharField(u"指标分组", max_length=255)
    dimension = models.CharField(u"指标维度", max_length=255)
    metric_source_id = models.CharField(u"指标源ID", max_length=255)
    condition = models.TextField(u"监控范围", blank=True, default='')
    stat_source_info = models.TextField('统计源信息（JSON）', blank=True, default='')

    # 警报阈值（算法）
    strategy_id = models.CharField(u"算法id", max_length=10, choices=constant.STRATEGY_CHOICES)
    strategy_option = models.TextField(u"算法参数", help_text=u"json格式")

    # 收敛设置
    rules = models.TextField(u"收敛规则", help_text=u"json格式")

    # 操作
    notify = models.TextField(u"通知配置", default='[]', help_text=u"json格式")

    # 附加设置
    miss_data_action = models.CharField(u"缺失数据处理", max_length=32, choices=constant.MISS_DATA_ACTION_CHOICE)

    # 后台关联表的id
    backend_ids = models.TextField(u"关联的后台表id", default='{}')

    objects = AlarmConfigManager()
    default_objects = models.Manager()

    class Meta:
        unique_together = ("project_id", "name")
        ordering = ('-id',)


class EventConfigManager(models.Manager):
    """Manager for EventConfig
    """

    def get_queryset(self):
        return super(EventConfigManager, self).get_queryset().filter(is_deleted=False)


class EventConfig(BaseModel):
    """事件配置
    """
    cc_biz_id = models.CharField(u"cc业务ID", max_length=32)
    project_id = models.CharField(u"项目ID", max_length=32)
    name = models.CharField(u"名称", max_length=255)
    desc = models.TextField(u"描述")

    is_enabled = models.BooleanField(u"启用状态", default=True)

    # 状态信息由监控后台写入——暂时先没有用
    status = models.CharField(u"状态", max_length=32, null=True, blank=True, choices=constant.ALARM_STATUS_CHOICE,
                              default='insufficient')
    status_time = models.DateTimeField(u"状态更新时间", null=True, blank=True)

    service_name = models.CharField(u"服务名称", max_length=255)
    event_type = models.CharField(u"事件类型", max_length=255)
    condition = models.TextField(u"监控范围", blank=True, default='')
    stat_source_info = models.TextField('统计源信息（JSON）', blank=True,
                                        default='{"aggregator":"count","monitor_field":"*"}',
                                        help_text="使用默认值，不需要填写")

    # 警报阈值（算法）
    strategy_id = models.CharField(u"算法id", max_length=10, default="1000", help_text=u"默认为:静态阈值")
    strategy_option = models.TextField(u"算法参数", default='{"threshold":1,"method":"gte"}')

    # 收敛设置
    rules = models.TextField(u"收敛规则", default='{"count": 1, "converge_id": 4, "continuous": 5}')

    # 汇总设置: 警报基础上新增的字段
    collect = models.TextField(u"汇总规则", default='{}', help_text=u"json格式")

    # 操作
    notify = models.TextField(u"通知配置", default='[]', help_text=u"json格式")

    objects = EventConfigManager()
    default_objects = models.Manager()

    class Meta:
        unique_together = ("project_id", "name")
        ordering = ('-id',)


class MetricGraphStorage(BaseModel):
    """指标存储表
    """
    project_id = models.CharField(u"项目ID", max_length=32)
    name = models.CharField(u"名称", max_length=64)
    content = models.TextField(u"内容", null=True, blank=True)

    class Meta:
        ordering = ('-id',)


class LogGroupsManager(models.Manager):

    def get_queryset(self):
        return super(LogGroupsManager, self).get_queryset().filter(is_deleted=False)


class LogGroups(BaseModel):
    """日志组,后续用户可以自定义日志组
    """
    project_id = models.CharField(max_length=32, help_text=u'为0时，表示所有项目公共的日志组')
    # code暂不使用
    code = models.CharField('编码', max_length=64, default='', blank=True, help_text='暂不使用')
    name = models.CharField('名称', max_length=255)

    objects = LogGroupsManager()
    default_objects = models.Manager()

    class Meta:
        pass

    def __str__(self):
        return '<%s - %s>' % (self.project_id, self.name)


class LogStreamManager(models.Manager):

    def get_queryset(self):
        return super(LogStreamManager, self).get_queryset().filter(is_deleted=False)


class LogStream(BaseModel):
    """日志流"""

    project_id = models.CharField(max_length=32)
    log_group_id = models.IntegerField('日志组ID')
    # code暂不使用
    code = models.CharField('编码', max_length=64, default='', blank=True, help_text='暂不使用')
    name = models.CharField('名称', max_length=255, help_text='名称表示日志流ES-Index，需要与监控配置项保持一致，**请勿修改**')
    type = models.CharField('类型', max_length=32, default='custom', choices=constant.LogStreamTypeEnum.get_choices(),
                            help_text='同一项目下，标准化/非标准化日志均只能存在一个')
    latest_log_time = models.DateTimeField('ES中最新日志时间', null=True, blank=True)

    objects = LogStreamManager()
    default_objects = models.Manager()

    class Meta:
        db_table = 'paas_monitor_log_stream'

    def __str__(self):
        return '<%s - %s>' % (self.project_id, self.name)


class LogMonitorManager(models.Manager):

    def get_queryset(self):
        return super(LogMonitorManager, self).get_queryset().filter(is_deleted=False)


class LogMonitor(BaseModel):
    """日志监控项"""

    project_id = models.CharField(max_length=32)
    log_stream_id = models.IntegerField('日志流ID')
    name = models.CharField('名称', max_length=255)
    monitor_item_config_id = models.IntegerField('监控项配置ID')

    objects = LogMonitorManager()
    default_objects = models.Manager()

    class Meta:
        db_table = 'paas_monitor_log_monitor'


class MonitorItemConfigManager(models.Manager):

    def get_queryset(self):
        return super(MonitorItemConfigManager, self).get_queryset().filter(is_deleted=False)


class MonitorItemConfig(BaseModel):
    """监控项配置，目前用于事件、日志类监控信息系配置"""

    cc_biz_id = models.CharField('配置平台业务ID', max_length=32)
    project_id = models.CharField('项目ID', max_length=32)

    name = models.CharField(max_length=256, verbose_name='名称')
    is_enabled = models.BooleanField('启用状态', default=True)

    status = models.CharField('事件状态', max_length=32, blank=True,
                              choices=constant.ALARM_STATUS_CHOICE, default='created')
    status_time = models.DateTimeField('状态更新时间', null=True, blank=True)

    src_type = models.CharField('监控源分类', blank=True, default='BCS_EVENT', max_length=64)
    scenario = models.CharField('监控场景', blank=True, default='event', max_length=64)

    stat_source_type = models.CharField('统计源分类', max_length=64, default='KAFKA', blank=True)
    stat_source_info = models.TextField('统计源信息', default='', blank=True, help_text='JSON格式数据')

    condition = models.TextField('监控范围', default='', blank='', help_text='JSON格式数据')

    strategy = models.TextField('检测策略', default='', blank=True, help_text='JSON格式数据，包含算法ID，算法配置，如{"algorithm_id": 1000, "config": {"threshold": 1, "method": "gte"}}')  # noqa
    converge = models.TextField('收敛规则', default='{"count": 1, "converge_id": 4, "continuous": 5}', help_text='JSON格式数据，如{"count": 1, "converge_id": 4, "continuous": 5}')  # noqa
    collect = models.TextField('汇总规则', default='{}', help_text='JSON格式数据')
    notice = models.TextField('通知配置', default='[]', help_text='JSON格式数据')

    objects = MonitorItemConfigManager()
    default_objects = models.Manager()

    class Meta:
        db_table = 'paas_monitor_monitor_item_config'


class AlarmShieldManager(models.Manager):

    def get_queryset(self):
        return super(AlarmShieldManager, self).get_queryset().filter(is_deleted=False)


class AlarmShield(BaseModel):
    """告警屏蔽
    """
    project_id = models.CharField(u"项目ID", max_length=32)
    shield_type = models.CharField("屏蔽类型", max_length=32, choices=constant.SHIELD_TYPES.items(), blank=True, null=True)
    shield_condition = models.TextField("屏蔽范围", blank=True, null=True)
    shield_start_time = models.DateTimeField("屏蔽开始时间")
    shield_end_time = models.DateTimeField("屏蔽结束时间")
    is_enabled = models.BooleanField("是否启用", default=True)

    objects = AlarmShieldManager()
    default_objects = models.Manager()

    class Meta:
        ordering = ('-id',)


class JaAlarmAlarminstance(models.Model):
    """告警表
    """
    alarm_source_id = models.IntegerField(
        blank=True, default=0, verbose_name='告警源id')
    raw = models.TextField(verbose_name='告警内容')
    status = models.CharField(
        blank=True, max_length=30, null=True, verbose_name='状态')
    comment = models.TextField(blank=True, null=True, verbose_name='备注')
    comment_id = models.CharField(max_length=128, verbose_name='备注事件ID')
    begin_time = models.DateTimeField(blank=True, verbose_name='告警开始时间')
    end_time = models.DateTimeField(
        blank=True, null=True, verbose_name='告警结束时间')
    source_time = models.DateTimeField(
        blank=True, null=True, verbose_name='告警接入系统的时间')
    failure_type = models.CharField(
        blank=True, max_length=30, null=True, verbose_name='处理失败类型')
    cc_biz_id = models.IntegerField(blank=True, default=0, verbose_name='业务')
    cc_topo_set = models.CharField(max_length=128, verbose_name='SET')
    cc_app_module = models.CharField(max_length=128, verbose_name='模块')
    cc_plat_id = models.IntegerField(
        blank=True, default=0, verbose_name='平台ID')
    cc_company_id = models.IntegerField(
        blank=True, default=0, verbose_name='开发商ID')
    ip = models.CharField(
        blank=True, max_length=30, null=True, verbose_name='IP')
    alarm_type = models.CharField(max_length=128, verbose_name='告警类型')
    solution_type = models.CharField(
        blank=True, max_length=128, null=True, verbose_name='告警处理类型')
    snap_alarm_source = models.TextField(
        blank=True, default='', null=True, verbose_name='告警源快照')
    snap_solution = models.TextField(
        blank=True, default='', null=True, verbose_name='处理快照')
    snap_converge = models.TextField(
        blank=True, default='', null=True, verbose_name='收敛快照')
    snap_collect = models.TextField(
        blank=True, default='', null=True, verbose_name='汇总快照')
    snap_notice = models.TextField(
        blank=True, default='', null=True, verbose_name='通知快照')
    approved_user = models.CharField(
        blank=True, max_length=128, null=True, verbose_name='告警确认者')
    approved_time = models.DateTimeField(
        blank=True, null=True, verbose_name='告警确认时间')
    approved_comment = models.CharField(
        blank=True, max_length=128, null=True, verbose_name='告警确认信息')
    source_id = models.CharField(
        blank=True, max_length=255, null=True, verbose_name='告警特征计算出来的ID')
    source_type = models.CharField(
        blank=True, max_length=32, null=True, verbose_name='告警源类型')
    alarm_dimension = models.TextField(
        blank=True, null=True, verbose_name='告警内容中展示的告警维度')
    match_dimension = models.TextField(
        blank=True, null=True, verbose_name='告警后台内部匹配的维度')
    alarm_attr_id = models.IntegerField(
        blank=True, null=True, verbose_name='监控系统内的监控ID')
    event_id = models.CharField(
        blank=True,
        max_length=255,
        null=True,
        unique=True,
        verbose_name='关联事件ID')
    origin_alarm = models.TextField(
        blank=True, null=True, verbose_name='原始告警内容')
    priority = models.IntegerField(blank=True, default=0, verbose_name='告警优先级')
    level = models.IntegerField(blank=True, default=0, verbose_name='告警等级')
    finish_time = models.DateTimeField(
        blank=True, null=True, verbose_name='处理结束时间')
    status_strategy_id = models.IntegerField(
        blank=True, null=True, verbose_name='status strategy id')
    user_status = models.CharField(
        blank=True,
        default='received',
        max_length=30,
        null=True,
        verbose_name='告警外部状态')
    snap_responsible = models.TextField(
        blank=True, null=True, verbose_name='snap responsible')
    alarm_content = models.TextField(
        blank=True, default='', null=True, verbose_name='推荐显示文字')
    notice_time = models.DateTimeField(
        blank=True, null=True, verbose_name='通知时间')
    project_id = models.CharField(
        blank=True, null=True, max_length=255, db_index=True, verbose_name="项目ID"
    )
    monitor_name = models.CharField(
        blank=True, null=True, max_length=255, db_index=True, verbose_name="告警源名称"
    )

    def __str__(self):
        return f'<{self.alarm_source_id}, {self.raw}>'

    class Meta:
        db_table = 'ja_alarm_alarminstance'
        index_together = ('source_type', 'source_id', 'source_time')
        managed = True
