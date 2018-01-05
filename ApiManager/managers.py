from django.db import models


class UserTypeManager(models.Manager):
    def insert_user_type(self, user_type):
        self.create(user_type=user_type)

    def insert_type_name(self, type_name):
        self.create(type_name=type_name)

    def insert_type_desc(self, type_desc):
        self.create(type_desc=type_desc)

    def get_objects(self, user_type_id):  # 根据user_type得到一条数据
        return self.get(user_type_id=user_type_id)


class UserInfoManager(models.Manager):
    def insert_user(self, username, password, email, object):
        self.create(username=username, password=password, email=email, user_type=object)

    def query_user(self, username, password):
        return self.filter(username__exact=username, password__exact=password).count()


class ProjectInfoManager(models.Manager):
    def insert_project(self, pro_name, responsible_name, test_user, dev_user, publish_app, simple_desc, other_desc):
        self.create(pro_name=pro_name, responsible_name =responsible_name, test_user = test_user, dev_user = dev_user
                    , publish_app = publish_app, simple_desc = simple_desc, other_desc = other_desc)

    def get_pro_name(self, pro_name, type = True):
        if type:
            return self.filter(pro_name__exact=pro_name).count()
        else:
            return self.get(pro_name = pro_name)

    def get_pro_info(self):
        return self.all().values('pro_name')





class ModuleInfoManager(models.Manager):
    def insert_module(self, module_name, belong_project, test_user, lifting_time, simple_desc, other_desc):
        self.create(module_name = module_name, belong_project = belong_project, test_user = test_user, lifting_time = lifting_time,
                    simple_desc = simple_desc, other_desc = other_desc)
    def get_module_name(self, module_name, type = True):
        if type:
            return self.filter(module_name__exact=module_name).count()
        else:
            return self.get(module_name = module_name)

    def get_module_info(self, belong_project):
        return self.filter(belong_project__pro_name__exact=belong_project).values_list('module_name', flat=True).order_by('-create_time')

class TestCaseInfoManager(models.Manager):
    def insert_case(self, belong_module, **kwargs):
        name = kwargs.pop('name')
        request = kwargs.pop('request')
        self.create(case_name = name.pop('case_name'), belong_project = name.pop('project'), belong_module = belong_module,
                    author = name.pop('author'), include = name.pop('include'), variables = kwargs.get('variables'),
                    setup = kwargs.get('setUp'), url = request.pop('url'), method = request.pop('method'), data_type = request.pop('type'),
                    request = request.pop('request_data'), headers = request.pop('headers'), teardown = kwargs.pop('tearDown'),
                    extract = kwargs.pop('extract'), validate = kwargs.pop('validate'))

    def get_case_name(self, case_name, module_name):
        return self.filter(belong_module__module_name=module_name).filter(case_name__exact=case_name).count()