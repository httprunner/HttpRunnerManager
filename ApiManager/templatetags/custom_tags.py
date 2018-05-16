from django import template

register = template.Library()


@register.filter(name='data_type')
def data_type(value):
    """
    返回数据类型 自建filter
    :param value:
    :return: the type of value
    """
    return str(type(value).__name__)


@register.filter(name='convert_eval')
def data_type(value):
    """
    数据eval转换 自建filter
    :param value:
    :return: the value which had been eval
    """
    return eval(value)
