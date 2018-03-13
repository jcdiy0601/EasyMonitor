from django.conf.urls import url
from monitor_api import views

urlpatterns = [
    url(r'^v1/config', views.client_configs, name='client_configs'),
    # url(r'^v1/data', views.client_configs, name='client_configs'),
]
