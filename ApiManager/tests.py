from django.test import TestCase

# Create your tests here.
import os,django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HttpRunnerManager.settings")
django.setup()
from ApiManager.models import ProjectInfo
a = ProjectInfo.objects.all().values()
for key in a:
    print(key)
print(ProjectInfo.objects.get(pro_name__exact='上海存管'))


