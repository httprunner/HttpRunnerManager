from django.contrib import admin

from ApiManager.models import UserInfo, ProjectInfo, ModuleInfo, TestCaseInfo, EnvInfo


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password', 'email', 'status', 'create_time', 'update_time')
    list_per_page = 20
    ordering = ('-create_time',)
    list_display_links = ('username',)
    # 筛选器
    list_filter = ('username', 'email')  # 过滤器
    search_fields = ('username', 'email')  # 搜索字段
    date_hierarchy = 'update_time'  # 详细时间分层筛选　


@admin.register(ProjectInfo)
class ProjectInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_name', 'responsible_name', 'test_user', 'dev_user', 'publish_app', 'simple_desc',
                    'other_desc', 'create_time', 'update_time')
    list_per_page = 20
    ordering = ('-create_time',)
    list_display_links = ('project_name',)
    list_filter = ('project_name', 'responsible_name')  # 过滤器
    search_fields = ('project_name', 'responsible_name')  # 搜索字段
    date_hierarchy = 'update_time'  # 详细时间分层筛选　


@admin.register(ModuleInfo)
class ModuleInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'module_name', 'belong_project', 'test_user', 'simple_desc'
                    , 'other_desc', 'create_time', 'update_time')
    list_per_page = 20
    ordering = ('-create_time',)
    list_display_links = ('module_name',)
    list_filter = ('module_name', 'test_user')  # 过滤器
    search_fields = ('module_name', 'test_user')  # 搜索字段
    date_hierarchy = 'update_time'  # 详细时间分层筛选　


@admin.register(TestCaseInfo)
class TestCaseInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'type', 'name', 'belong_project', 'belong_module', 'include', 'author', 'request',
        'create_time',
        'update_time')
    list_per_page = 50
    ordering = ('-create_time',)
    list_display_links = ('name',)
    list_filter = ('belong_project', 'belong_module', 'type', 'name')  # 过滤器
    search_fields = ('belong_project', 'belong_module', 'type', 'name')  # 搜索字段
    date_hierarchy = 'update_time'  # 详细时间分层筛选


@admin.register(EnvInfo)
class EnvInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'env_name', 'base_url', 'simple_desc', 'create_time', 'update_time')
    list_per_page = 50
    ordering = ('-create_time',)
    list_display_links = ('env_name',)
    list_filter = ('env_name', 'base_url')  # 过滤器
    search_fields = ('env_name', 'env_name')  # 搜索字段
    date_hierarchy = 'update_time'  # 详细时间分层筛选


admin.site.site_header = 'HttpRunnerManager运维管理系统'
admin.site.site_title = 'HttpRunnerManager'
