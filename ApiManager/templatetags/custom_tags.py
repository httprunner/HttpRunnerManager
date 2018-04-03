from django import template

register = template.Library()
'''自定义模板tag，判断数据类型'''


@register.filter(name='data_type')
def data_type(value):
    return str(type(value).__name__)

