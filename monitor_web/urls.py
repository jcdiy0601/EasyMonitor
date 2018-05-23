from django.conf.urls import url
from monitor_web.views import host_group_view, host_view

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
]
