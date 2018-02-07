
# Create your tests here.
import os,django

import requests
from requests import request

from httprunner.cli import main_ate

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HttpRunnerManager.settings")

django.setup()
from ApiManager.models import TestCaseInfo, ModuleInfo

a = TestCaseInfo.objects.filter(belong_module=ModuleInfo.objects.get(id=25)).values_list('id')
for i in a:
    print(i[1])