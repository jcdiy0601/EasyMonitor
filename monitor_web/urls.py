from django.conf.urls import url
from monitor_web import views

urlpatterns = [
    url(r'^host_group.html$', views.host_group, name='host_group'),
    url(r'^host_group_add.html$', views.host_group_add, name='host_group_add'),
]
