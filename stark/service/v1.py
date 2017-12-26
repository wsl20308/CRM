#! usr/bin/env python
# -*- coding: utf-8 -*
"""stark组件的主要数据处理"""
from django.conf.urls import url
from django.shortcuts import render,redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.http import QueryDict
from django.db.models import Q
import copy
import json
class FilterOption(object):
    def __init__(self,filter_name,multi=False,condition=None,is_choices=False,text_func_name=None,val_func_name=None):
        """
            app中stark  combination_filter配置
            :param field_name: 字段
            :param multi:  是否多选
            :param condition: 显示数据的筛选条件
            :param is_choice: 是否是choice
            :param text_func_name:组合搜索时，页面上生成显示文本的函数
            :param val_func_name=None:组合搜索时，页面上生成a标签中的值得函数，默认使用对象pk
            例：
                combination_filter = [
                v1.FilterOption('gender',is_choice=True),
                v1.FilterOption('depart',condition={'id__gt':3}),
                v1.FilterOption('role',True),
                v1.FilterOption('depart',text_func_name=lambda x:str(x),val_func_name=lambda x:x.code,),
                                ]
        """
        self.filter_name = filter_name
        self.multi=multi
        self.condition=condition
        self.is_choices=is_choices
        self.text_func_name=text_func_name
        self.val_func_name=val_func_name

    def get_queryset(self,_filter):
        """处理MTM,FK,判断有没有设置显示条数"""
        if self.condition:
            return _filter.rel.to.objects.filter(**self.condition)
        return _filter.rel.to.objects.all()
    def get_choices(self,_filter):
        """处理choices类型数据"""
        return _filter.choices

class FilterRow(object):
    def __init__(self,option,data,request):
        self.data = data
        self.option = option
        self.request = request
    def __iter__(self):
        params = copy.deepcopy(self.request.GET)
        params._mutable = True
        current_id = params.get(self.option.filter_name)
        current_id_list = params.getlist(self.option.filter_name)
        if self.option.filter_name in params:
            origin_list = params.pop(self.option.filter_name)
            url = "{0}?{1}".format(self.request.path_info,params.urlencode())
            yield mark_safe("<a href='{0}'>全部</a>".format(url))
            params.setlist(self.option.filter_name,origin_list)
        else:
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())
            yield mark_safe("<a href='{0}' class='active'>全部</a>".format(url))
        for val in self.data:
            if self.option.is_choices:
                pk,text=str(val[0]),str(val[1])
            else:
                text = self.option.text_func_name(val) if self.option.text_func_name else str(val)
                pk = str(self.option.val_func_name(val))if self.option.val_func_name else str(val.pk)

            if not self.option.multi:
                #单选
                params[self.option.filter_name] = pk
                url="{0}?{1}".format(self.request.path_info,params.urlencode())
                if current_id == pk:
                    yield mark_safe("<a href={0} class='active'>{1}</a>".format(url,text))
                else:
                    yield mark_safe("<a href={0}>{1}</a>".format(url, text))
            else:
                # 多选
                _params = copy.deepcopy(params)
                id_list = _params.getlist(self.option.filter_name)
                if pk in current_id_list:
                    id_list.remove(pk)
                    _params.setlist(self.option.filter_name,id_list)
                    url = "{0}?{1}".format(self.request.path_info,_params.urlencode())
                    yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url,text))
                else:
                    id_list.append(pk)
                    _params.setlist(self.option.filter_name,id_list)
                    #创建url
                    url = "{0}?{1}".format(self.request.path_info,_params.urlencode())
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))

class Changelist(object):
    """列表封装函数"""
    def __init__(self,config,queryset):
        self.config = config

        self.list_dsplay = config.get_list_dsplay()
        self.model_class = config.model_class
        self.request = config.request
        self.show_add_btn = config.get_show_add_btn()
        self.edit_link = config.get_edit_link()

        #组合搜索
        self.combination_filter = config.get_combination_filter()

        #搜索
        self.show_search_form = config.get_show_search_form()
        self.search_form_val = config.request.GET.get(config.serch_key,'')

        #批量操作
        self.actions = config.get_actions()
        self.show_actions = config.get_show_actions()
        # 分页
        from stark.paging.pager import Pagination
        current_page = self.request.GET.get('page', 1)
        total_count = queryset.count()
        page_obj = Pagination(current_page, total_count, self.request.path_info, self.request.GET, per_page_count=2)
        self.page_obj = page_obj
        self.data_list = queryset[page_obj.start:page_obj.end]
    #批量操作，用户自定制
    def modify_actions(self):
        """用于action中显示文本和value属性值"""
        result = []
        for func in self.actions:
            temp = {'name':func.__name__,'text':func.short_desc}
            result.append(temp)
        return result
    def add_url(self):
        return self.config.get_add_url()
    # 处理表头
    def head_list(self):
        """构建表头"""
        result = []
        for field_name in self.list_dsplay:
            if isinstance(field_name, str):
                verbose_name = self.model_class._meta.get_field(field_name).verbose_name
            else:
                verbose_name = field_name(self.config, is_header=True)
            result.append(verbose_name)
        return result
    #处理表数据
    def body_list(self):
        """列表页面，数据表内容中显示每一行数据"""
        data_list = self.data_list
        new_data_list = []
        for row in data_list:
            temp = []
            for field_name in self.list_dsplay:
                if isinstance(field_name, str):
                    val = getattr(row, field_name)
                else:
                    val = field_name(self.config,row)
                # 判断field在不在edit_name中，在变成a标签,反向生成url,获取url的参数
                if field_name in self.edit_link:
                    val = self.edit_link_tag(row.pk, val)
                temp.append(val)

            new_data_list.append(temp)
        return new_data_list
    #组合搜索
    def gen_combination_filter(self):
        from django.db.models import ForeignKey, ManyToManyField
        for option in self.combination_filter:
            _filter = self.model_class._meta.get_field(option.filter_name)
            print(_filter)
            if isinstance(_filter,ForeignKey):
                row = FilterRow(option,option.get_queryset(_filter),self.request)
            elif isinstance(_filter,ManyToManyField):
                row = FilterRow(option,option.get_queryset(_filter),self.request)
            else:
                row = FilterRow(option,option.get_choices(_filter),self.request)
            yield row
    #反向生成url,生成a标签
    def edit_link_tag(self,pk,text):
        query_str = self.request.GET.urlencode()
        params = QueryDict(mutable=True)
        params[self.config._query_param_key] = query_str
        return mark_safe('<a href = "%s?%s">%s</a>' % (self.config.get_change_url(pk), params.urlencode(),text))

class StarkConfing(object):
    """用于处理stark组件中增删改查的基类，以后对于每个类都要继承该类，如：
        class DepartmentConfig(v1.StarkConfing):
            list_dsplay = ['id','title']
            edit_link = ['title']
            # def get_list_dsplay(self):
            #     result = []
            #     if self.list_dsplay:
            #         result.extend(self.list_dsplay)
            #         result.append(v1.StarkConfing.edit)
            #         result.append(v1.StarkConfing.delete)
            #         result.insert(0,v1.StarkConfing.checkbox)
            #     return result
        v1.site.register(models.Department,DepartmentConfig)
    """
    # 1. 定制列表页面显示的列
    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return "选择"
        return mark_safe('<input type="checkbox" name=pk value=%s>' % (obj.id,))
        # 编辑
    def edit(self, obj=None, is_header=False):
        if is_header:
            return "编辑"
        query_str = self.request.GET.urlencode()
        if query_str:
            params = QueryDict(mutable=True)
            params[self._query_param_key] = query_str
            return mark_safe('<a href = "%s?%s">编辑</a>' % (self.get_change_url(obj.id),params.urlencode(),))
        return mark_safe('<a href = "%s">编辑</a>' % (self.get_change_url(obj.id)))
        #删除
    def delete(self, obj=None, is_header=False):
        if is_header:
            return "删除"
        query_str = self.request.GET.urlencode()
        if query_str:
            params = QueryDict(mutable=True)
            params[self._query_param_key] = query_str
            return mark_safe('<a href = "%s?%s">删除</a>' %(self.get_delete_url(obj.id),params.urlencode()))
        return mark_safe('<a href = "%s">删除</a>' %(self.get_delete_url(obj.id),))
    # 2. 是否显示添加按钮
    show_add_btn = True
    def get_show_add_btn(self):
        return self.show_add_btn
        # list_dsplay配置
    list_dsplay = []
    def get_list_dsplay(self):
        data = []
        if self.list_dsplay:
            data.extend(self.list_dsplay)
            # data.append(StarkConfing.edit)
            data.append(StarkConfing.delete)
            data.insert(0, StarkConfing.checkbox)
        return data
    #3,用户自定制Model.form
    model_form_class = None
    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class
        from django.forms import ModelForm
        class TestModelForm(ModelForm):
            class Meta:
                model = self.model_class
                fields = "__all__"
        return TestModelForm
    #4.关键字搜索
        #是否显示搜索框
    show_search_form = False
    def get_show_search_form(self):
        return self.show_search_form
        #显示字段
        #搜索配置
    search_fields=[]
    def get_search_fields(self):
        resuelt=[]
        if self.search_fields:
            resuelt.extend(self.search_fields)
        return resuelt
        #搜索
        #执行搜索
    def get_search_condition(self):
        key_word = self.request.GET.get(self.serch_key)
        search_fields = self.get_search_fields()
        condition = Q()
        condition.connector = 'or'
        if key_word and self.get_search_fields():
            for field_name in search_fields:
                condition.children.append((field_name, key_word))  # 只接收一个位置参数
        return condition
    #5:action批量操作
        # 是否显示批量操作
    show_actions = False
    def get_show_actions(self):
        return self.show_actions
        #action配置
    actions = []
    def get_actions(self):
        result=[]
        if self.actions:
            result.extend(self.actions)
        return result
    #6:组合搜索
    combination_filter = []
    def get_combination_filter(self):
        result=[]
        if self.combination_filter:
            result.extend(self.combination_filter)
        return result
    #自定义编辑按钮
    edit_link = []
    def get_edit_link(self):
        result = []
        if self.edit_link:
            result.extend(self.edit_link)
        return result

    #构造方法
    def __init__(self, model_class, site):
        self.model_class = model_class
        self.site = site
        self.request = None
        self._query_param_key = "_listfilter"
        self.serch_key = "_q"
    #request,装饰器
    def wrap(self,view_func):
        def inner(request,*args,**kwargs):
            self.request = request
            return view_func(request,*args,**kwargs)
        return inner
    # url相关
        # 增删改查url，进来先走wrap装饰器，拿到request
    def get_urls(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name)
        url_pattern = [
            url('^$', self.wrap(self.changelist_view), name='%s_%s_changelist' % app_model_name),
            url('^add/$',self.wrap(self.add_view) , name='%s_%s_add' % app_model_name),
            url('^(\d+)/delete/$',self.wrap(self.delete_view), name='%s_%s_delete' % app_model_name),
            url('^(\d+)/change/$',self.wrap(self.change_view), name='%s_%s_change' % app_model_name),
        ]
        # 调用钩子函数
        url_pattern.extend(self.extra_url())
        return url_pattern
        #钩子函数
    def extra_url(self):
        return []
    @property
    def urls(self):
        return self.get_urls()
        # 反向生成列表页面url
    def get_changelist_url(self):
        name = "stark:%s_%s_changelist" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        edit_url = reverse(name)
        return edit_url

    #反向生成url
        # 反向生成编辑页面url
    def get_change_url(self, nid):
        print(nid)
        name = "stark:%s_%s_change" % (self.model_class._meta.app_label, self.model_class._meta.model_name)

        edit_url = reverse(name, args=(nid,))
        return edit_url
        # 反向生成删除页面url
    def get_delete_url(self,nid):
        name = "stark:%s_%s_delete" % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        edit_url = reverse(name, args=(nid,))
        return edit_url
        # 重定向删除
        # 反向生成删除页面url
    def get_add_url(self):
        name = "stark:%s_%s_add" % (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        edit_url = reverse(name)
        return edit_url

    # 处理请求的方法---------增删改查
        #列表

    def changelist_view(self, request, *args, **kwargs):
        """列表"""
        if request.method=="POST" and self.get_show_actions():
            func_name_str = request.POST.get('list_action')
            action_func = getattr(self,func_name_str)
            ret = action_func(request)
            if ret:
                return ret
        combination_filter = {}
        option_list = self.get_combination_filter()
        for key in request.GET.keys():
            value_list = request.GET.getlist(key)
            flag = False
            for option in option_list:
                if option.filter_name == key:
                    flag = True
                    break
            if flag:
                combination_filter["%s__in" % key] = value_list
        queryset = self.model_class.objects.filter(self.get_search_condition()).filter(**combination_filter).distinct()
        cl = Changelist(self,queryset)
        return render(request, "stark/changelist_view.html", {'cl': cl})
        #添加
    def add_view(self, request, *args, **kwargs):
        """添加"""
        model_form_class = self.get_model_form_class()
        _popbackid = request.GET.get('_popbackid')
        if request.method=="GET":
            form=model_form_class()
            # new_form = []
            # for bfield in form:
            #     temp = {'is_popup':False,'item':bfield}
            #     from django.forms.models import ModelChoiceField
            #     if isinstance(bfield.field,ModelChoiceField):
            #         related_class_name = bfield.field.queryset.model
            #         if related_class_name in site._registry:
            #             app_model_name = related_class_name._meta.app_label,related_class_name._meta.model_name
            #             base_url = reverse("stark:%s_%s_add"%app_model_name)
            #             popup_url = "%s?_popbackid=%s"%(base_url,bfield.auto_id)
            #             temp['is_popup'] = True
            #             temp['popup_url'] = popup_url
            #     new_form.append(temp)
            return render(request,'stark/add_view.html',{'form':form,})
        else:
            form =  model_form_class (request.POST)
            if form.is_valid():
                #添加数据库
                new_obj = form.save()#拿到一个返回值
                if _popbackid:
                    # 是popup请求
                    # render一个页面，写自执行函数
                    #拿到数据，实现实时更新
                    result = {'id': new_obj.pk, 'text': str(new_obj), 'popbackid': _popbackid}
                    return render(request, 'stark/popup_response.html',{'json_result':json.dumps(result,ensure_ascii=False)})
                else:
                    list_query_str = self.request.GET.get(self._query_param_key)
                    list_url = '%s?%s'%(self.get_changelist_url(),list_query_str)
                    return redirect(list_url)
            return render(request, 'stark/add_view.html',{'form':form})
    def delete_view(self, request, nid, *args, **kwargs):
        """删除"""
        obj = self.model_class.objects.filter(pk=nid)
        if not obj:
            list_query_str = self.request.GET.get(self._query_param_key)
            list_url = '%s?%s'%(self.get_changelist_url(),list_query_str)
            return redirect(list_url)
        else:
            self.model_class.objects.filter(pk=nid).delete()
            list_query_str = self.request.GET.get(self._query_param_key)
            list_url = '%s?%s'%(self.get_changelist_url(), list_query_str)
            return redirect(list_url)
        #编辑
    def change_view(self, request, nid, *args, **kwargs):
        """编辑"""
        obj = self.model_class.objects.filter(pk=nid).first()
        if not obj:
            return redirect(self.get_changelist_url())
        model_form_class=self.get_model_form_class()
        if request.method=="GET":
            form = model_form_class(instance=obj)
            return render(request,'stark/change_view.html',{'form':form})
        else:
            form = model_form_class(instance=obj, data=request.POST)
            if form.is_valid():
                form.save()
                list_query_str = self.request.GET.get(self._query_param_key)
                list_url = '%s?%s'%(self.get_changelist_url(),list_query_str)
                return redirect(list_url)
            return render(request, 'stark/change_view.html', {'form': form})

class StarkSite(object):
    def __init__(self):
        self._registry = {}

    def register(self, model_class, stark_confing_class=None):
        if not stark_confing_class:
            stark_confing_class = StarkConfing
        self._registry[model_class] = stark_confing_class(model_class, self)

    def get_urls(self):
        url_pattern = []
        for model_class, stark_confing_obj in self._registry.items():
            app_name = model_class._meta.app_label
            model_name = model_class._meta.model_name
            curd_url = url('^%s/%s/' % (app_name, model_name), (stark_confing_obj.urls, None, None))
            url_pattern.append(curd_url)
        return url_pattern
    @property
    def urls(self):
        return (self.get_urls(), None, 'stark')
site = StarkSite()
