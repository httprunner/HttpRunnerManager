from django import template

register = template.Library()
'''自定义模板tag，判断数据类型'''


@register.filter(name='data_type')
def data_type(value):
    if isinstance(value, str):
        return 'string'
    elif isinstance(value, int):
        return 'int'
    elif isinstance(value, float):
        return 'float'
    elif isinstance(value, bool):
        return 'boolean'
