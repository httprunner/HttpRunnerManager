# Create your tests here.
import json

import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HttpRunnerManager.settings")

django.setup()

a = {}
print(json.loads(json.dumps(a)))

print(bool('true'))