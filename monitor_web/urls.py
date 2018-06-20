from django.conf.urls import url
from monitor_web.views import host_group_view, host_view, template_view, application_view, item_view, trigger_view, \
    action_view, action_operation_view, user_view, chart_view, show_chart_view

urlpatterns = [
    # 主机组
    url(r'^host_group.html$', host_group_view.host_group, name='host_group'),
    url(r'^add_host_group.html$', host_group_view.add_host_group, name='add_host_group'),
    url(r'^edit_host_group_(?P<gid>\d+).html$', host_group_view.edit_host_group, name='edit_host_group'),
    url(r'^del_host_group.html$', host_group_view.del_host_group, name='del_host_group'),
    # 主机
    url(r'^host.html$', host_view.host, name='host'),
    url(r'^add_host.html$', host_view.add_host, name='add_host'),
    url(r'^hostname_check.html$', host_view.hostname_check, name='hostname_check'),
    url(r'^edit_host_(?P<hid>\d+).html$', host_view.edit_host, name='edit_host'),
    url(r'^del_host.html$', host_view.del_host, name='del_host'),
    # 模板
    url(r'^template.html$', template_view.template, name='template'),
    url(r'^add_template.html$', template_view.add_template, name='add_template'),
    url(r'^edit_template_(?P<tid>\d+).html$', template_view.edit_template, name='edit_template'),
    url(r'^del_template.html$', template_view.del_template, name='del_template'),
    # 应用集
    url(r'^application.html$', application_view.application, name='application'),
    url(r'^add_application.html$', application_view.add_application, name='add_application'),
    url(r'^edit_application_(?P<aid>\d+).html$', application_view.edit_application, name='edit_application'),
    url(r'^del_application.html$', application_view.del_application, name='del_application'),
    # 监控项
    url(r'^item.html$', item_view.item, name='item'),
    url(r'^add_item.html$', item_view.add_item, name='add_item'),
    url(r'^edit_item_(?P<iid>\d+).html$', item_view.edit_item, name='edit_item'),
    url(r'^del_item.html$', item_view.del_item, name='del_item'),
    # 触发器
    url(r'^trigger.html$', trigger_view.trigger, name='trigger'),
    url(r'^add_trigger.html$', trigger_view.add_trigger, name='add_trigger'),
    url(r'^edit_trigger_(?P<tid>\d+).html$', trigger_view.edit_trigger, name='edit_trigger'),
    url(r'^del_trigger.html$', trigger_view.del_trigger, name='del_trigger'),
    url(r'^select_application.html$', trigger_view.select_application, name='select_application'),
    url(r'^select_item.html$', trigger_view.select_item, name='select_item'),
    # 报警策略
    url(r'^action.html$', action_view.action, name='action'),
    url(r'^add_action.html$', action_view.add_action, name='add_action'),
    url(r'^edit_action_(?P<aid>\d+).html$', action_view.edit_action, name='edit_action'),
    url(r'^del_action.html$', action_view.del_action, name='del_action'),
    # 报警动作
    url(r'^action_operation.html$', action_operation_view.action_operation, name='action_operation'),
    url(r'^add_action_operation.html$', action_operation_view.add_action_operation, name='add_action_operation'),
    url(r'^edit_action_operation_(?P<aid>\d+).html$', action_operation_view.edit_action_operation, name='edit_action_operation'),
    url(r'^del_action_operation.html$', action_operation_view.del_action_operation, name='del_action_operation'),
    # 用户管理
    url(r'^user.html$', user_view.user, name='user'),
    url(r'^add_user.html$', user_view.add_user, name='add_user'),
    url(r'^edit_user_(?P<uid>\d+).html$', user_view.edit_user, name='edit_user'),
    url(r'^del_user.html$', user_view.del_user, name='del_user'),
    url(r'^change_pass_user_(?P<uid>\d+).html$', user_view.change_pass_user, name='change_pass_user'),
    url(r'^change_permission_user_(?P<uid>\d+).html$', user_view.change_permission_user, name='change_permission_user'),
    # 图形管理
    url(r'^chart.html$', chart_view.chart, name='chart'),
    url(r'^add_chart.html$', chart_view.add_chart, name='add_chart'),
    url(r'^edit_chart_(?P<cid>\d+).html$', chart_view.edit_chart, name='edit_chart'),
    url(r'^del_chart.html$', chart_view.del_chart, name='del_chart'),
    url(r'^get_application.html', chart_view.get_application, name='get_application'),
    url(r'^get_item.html', chart_view.get_item, name='get_item'),
    # 图形
    url(r'^show_chart.html$', show_chart_view.show_chart, name='show_chart'),
    url(r'^select_host_group_for_show_chart.html$', show_chart_view.select_host_group_for_show_chart, name='select_host_group_for_show_chart'),
    url(r'^select_host_for_show_chart.html$', show_chart_view.select_host_for_show_chart, name='select_host_for_chart'),
    url(r'^select_chart_for_show_chart.html$', show_chart_view.select_chart_for_show_chart, name='select_template_for_show_chart'),
]
