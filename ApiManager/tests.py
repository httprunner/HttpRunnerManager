from django.test import TestCase

# Create your tests here.
import os,django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HttpRunnerManager.settings")
django.setup()
from ApiManager.models import ProjectInfo, ModuleInfo

print(ProjectInfo.objects.all().get(pro_name__exact='上海').id)




