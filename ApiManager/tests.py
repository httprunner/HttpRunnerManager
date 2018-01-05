from django.test import TestCase

# Create your tests here.
import os,django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HttpRunnerManager.settings")
django.setup()
from ApiManager.models import ProjectInfo, ModuleInfo

module_info = list(ModuleInfo.objects.get_module_info('上海存管'))
string = ''
for value in module_info:
    string = string + value + 'replaceFlag'
print(string[:len(string) - 11])




