from django.conf.urls import url
from monitor_web.views import host_group_view, host_view, template_view, application_view, item_view, trigger_view

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
]
