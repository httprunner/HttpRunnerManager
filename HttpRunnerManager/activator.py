import traceback

from django.shortcuts import HttpResponse


def process(request, **kwargs):
    app = kwargs.pop('app', None)
    fun = kwargs.pop('function', None)
    index = kwargs.pop('id', None)
    mode = kwargs.pop('mode', None)

    if app == 'api':
        app = 'ApiManager'
    try:
        app = __import__("%s.views" % app)
        view = getattr(app, 'views')
        fun = getattr(view, fun)

        # 执行view.py中的函数，并获取其返回值
        if mode:
            result = fun(request, mode, index)
        else:
            result = fun(request, index)
    except TypeError:
        result = fun(request)
    except (ImportError, AttributeError):
        # 导入失败时，自定义404错误
        return HttpResponse(traceback.format_exc())

    return result
