"""DjangoPro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from ApiManager.views import register, login, index, add_project, add_module, add_case, add_config, add_api, run_test, \
    test_get, project_list, module_list, test_list, edit_case, edit_config

urlpatterns = [
    url(r'^register/', register),
    url(r'^login/', login),
    url(r'^index/', index),
    url(r'^add_project/', add_project),
    url(r'^add_module/', add_module),
    url(r'^add_case/', add_case),
    url(r'^add_config/', add_config),
    url(r'^add_api/', add_api),
    url(r'^run_test/', run_test),
    url(r'^project_list/(?P<id>\w+)/', project_list),
    url(r'^module_list/(?P<id>\w+)/', module_list),
    url(r'^test_list/(?P<id>\w+)/', test_list),
    url(r'^edit_case/(?P<id>\w+)/', edit_case),
    url(r'^edit_config/(?P<id>\w+)/', edit_config),
    url(r'^test_get/', test_get),

]
