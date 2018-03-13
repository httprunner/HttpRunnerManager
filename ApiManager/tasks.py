# Create your tasks here
from __future__ import absolute_import, unicode_literals

import time
from celery import shared_task


@shared_task
def add(x, y):
    time.sleep(10)
    print('the sum is:',x+y)
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)