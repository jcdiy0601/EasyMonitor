from django.conf.urls import url
from monitor_api import views

urlpatterns = [
    url(r'^v1/config$', views.client_config, name='client_config'),
    url(r'^v1/data$', views.client_data, name='client_data'),
]
