from django.utils.safestring import mark_safe

'''分页类'''


class PageInfo(object):
    def __init__(self, current, total_item, per_items=5):
        self.__current = current
        self.__per_items = per_items
        self.__total_item = total_item

    @property
    def start(self):
        return (self.__current - 1) * self.__per_items

    @property
    def end(self):
        return self.__current * self.__per_items

    @property
    def total_page(self):
        result = divmod(self.__total_item, self.__per_items)
        if result[1] == 0:
            return result[0]
        else:
            return result[0] + 1


'''分页处理 返回html'''


def customer_pager(base_url, current_page, total_page):  # 基础页，当前页，总页数
    per_pager = 11
    middle_pager = 5
    start_pager = 1
    if total_page <= per_pager:
        begin = 0
        end = total_page
    else:
        if current_page > middle_pager:
            begin = current_page - middle_pager
            end = current_page + middle_pager
            if end > total_page:
                end = total_page
        else:
            begin = 0
            end = per_pager
    pager_list = []

    if current_page <= start_pager:
        first = "<li><a href=''>首页</a></li>"
    else:
        first = "<li><a href='%s%d'>首页</a></li>" % (base_url, start_pager)
    pager_list.append(first)

    if current_page <= start_pager:
        prev = "<li><a href=''><<</a></li>"
    else:
        prev = "<li><a href='%s%d'><<</a></li>" % (base_url, current_page - start_pager)
    pager_list.append(prev)

    for i in range(begin + start_pager, end + start_pager):
        if i == current_page:
            temp = "<li><a href='%s%d' class='selected'>%d</a></li>" % (base_url, i, i)
        else:
            temp = "<li><a href='%s%d'>%d</a></li>" % (base_url, i, i)
        pager_list.append(temp)
    if current_page >= total_page:
        next = "<li><a href=''>>></a></li>"
    else:
        next = "<li><a href='%s%d'>>></a></li>" % (base_url, current_page + start_pager)
    pager_list.append(next)
    if current_page >= total_page:
        last = "<li><a href='''>尾页</a></li>"
    else:
        last = "<li><a href='%s%d' >尾页</a></li>" % (base_url, total_page)
    pager_list.append(last)
    result = ''.join(pager_list)
    return mark_safe(result)  # 把字符串转成html语言


def get_pager_info(Model, filter_query, url, id, per_items=10):
    id = int(id)
    filter = int(filter_query.get('filter'))
    name = filter_query.get('name')
    user = filter_query.get('user')
    obj = Model.objects.filter(status__exact=filter)

    if url == '/api/project_list/':
        if name == '' and user != '':
            obj = obj.filter(responsible_name__contains=user)
        elif name != '' and user == '':
            obj = obj.filter(pro_name__contains=name)
        elif name != '' and user != '':
            obj = obj.filter(pro_name__contains=name).filter(responsible_name__contains=user)

    elif url == '/api/module_list/':
        if name == '' and user != '':
            obj = obj.filter(test_user__contains=user)
        elif name != '' and user == '':
            obj = obj.filter(module_name__contains=name)
        elif name != '' and user != '':
            obj = obj.filter(module_name__contains=name).filter(test_user__contains=user)

    elif url == '/api/test_list/':
        if name == '' and user != '':
            obj = obj.filter(author__contains=user)
        elif name != '' and user == '':
            obj = obj.filter(name__contains=name)
        elif name != '' and user != '':
            obj = obj.filter(name__contains=name).filter(author__contains=user)

    total = obj.count()
    page_info = PageInfo(id, total, per_items=per_items)
    info = obj[page_info.start:page_info.end]
    page_list = customer_pager(url, id, page_info.total_page)
    return page_list, info
