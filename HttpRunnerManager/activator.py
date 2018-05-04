import platform
import traceback

from django.shortcuts import HttpResponse


def isWindows():
    return True if 'Windows' in platform.system() else False


def isLinux():
    return True if 'Linux' in platform.system() else False


def process(request, **kwargs):
    app = kwargs.pop('app', None)
    fun = kwargs.pop('function', None)
    index = kwargs.pop('id', None)

    if app == 'api':
        app = 'ApiManager'
    try:
        app = __import__("%s.views" % app)
        view = getattr(app, 'views')
        fun = getattr(view, fun)

        # 执行view.py中的函数，并获取其返回值
        result = fun(request, index) if index else fun(request)
    except (ImportError, AttributeError):
        return HttpResponse(traceback.format_exc())

    return result
