from django.shortcuts import HttpResponse


def process(request, **kwargs):
    app = kwargs.get('app', None)
    fun = kwargs.get('function', None)

    try:
        app = __import__("%s.views" % app)
        view = getattr(app, 'views')
        fun = getattr(view, fun)

        # 执行view.py中的函数，并获取其返回值
        result = fun(request, kwargs)

    except (ImportError, AttributeError):
        # 导入失败时，自定义404错误
        return HttpResponse('404 Not Found')
    return result
