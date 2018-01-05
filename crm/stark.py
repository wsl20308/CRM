#! usr/bin/env python
# -*- coding: utf-8 -*-
from stark.service import v1
from crm import models
from crm.congfigs.customer import CustomerConfig
from django.shortcuts import redirect,HttpResponse,render
class BasePermission(object):
    """
    用于多继承
    根据权限，定制页面显示，stark组件预留钩子
    """
    def get_show_add_btn(self):
        code_list = self.request.permission_code_list
        if "add" in code_list:
            return True

    def get_edit_link(self):
        code_list = self.request.permission_code_list
        if "edit" in code_list:
            return super(SchoolConfing,self).get_edit_link()
        else:
            return []

    def get_list_display(self):
        code_list = self.request.permission_code_list
        data = []
        if self.list_dsplay:
            data.extend(self.list_dsplay)
            if 'del' in code_list:
                data.append(v1.StarkConfing.delete)
            data.insert(0, v1.StarkConfing.checkbox)
        return data




class DepartmentConfig(v1.StarkConfing):
    """部门管理"""
    list_dsplay = ['id','title']
    edit_link = ['title']
            # def get_list_diplay(self):
            #     code_list = self.request.permission_code_list
            #     data = []
            #     if self.list_display:
            #         data.extend(self.list_display)
            #         if 'del' in code_list:
            #             data.append(v1.StarkConfig.delete)
            #         data.insert(0, v1.StarkConfig.checkbox)
            #     return data
    #重新显示编辑按钮，重写get_list_dsplay
    # def get_list_dsplay(self):
    #     result = []
    #     if self.list_dsplay:
    #         result.extend(self.list_dsplay)
    #         result.append(v1.StarkConfing.edit)
    #         result.append(v1.StarkConfing.delete)
    #         result.insert(0,v1.StarkConfing.checkbox)
    #     return result
v1.site.register(models.Department,DepartmentConfig)
class UserInfoConfig(v1.StarkConfing):
    """用户管理"""
    list_dsplay = ['name','username','email','depart']
    edit_link = ['depart']
    combination_filter = [
        v1.FilterOption('depart',text_func_name=lambda x:str(x),val_func_name=lambda x:x.code,),
    ]
    show_search_form = True
    search_fields = ['name__contains']
v1.site.register(models.UserInfo,UserInfoConfig)
class CourseConfig(v1.StarkConfing):
    """课程管理"""
    list_dsplay = ['name']
v1.site.register(models.Course,CourseConfig)
class SchoolConfig(v1.StarkConfing):
    """学校管理"""
    list_dsplay = ['title']
    edit_link = ['title']
        # def get_edit_link(self):
        #     code_list = self.request.permission_code_list
        #     if "edit" in code_list:
        #         return super(SchoolConfig, self).get_edit_link()
        #     else:
        #         return []
        # def get_list_diplay(self):
        #     code_list = self.request.permission_code_list
        #     data = []
        #     if self.list_display:
        #         data.extend(self.list_display)
        #         if 'del' in code_list:
        #             data.append(v1.StarkConfig.delete)
        #         data.insert(0, v1.StarkConfig.checkbox)
        #     return data
v1.site.register(models.School,SchoolConfig)
class ClassListConfig(v1.StarkConfing):
    """班级管理"""
    def course_semester(self,obj=None,is_header=False):
        """课程和班级拼接"""
        if is_header:
            return '班级'
        return '%s(%s期)'%(obj.course.name,obj.semester,)
    #未完成作业班级人数
    # ############## 作业3：popup增加时，是否将新增的数据显示到页面中（获取条件） #############
    def num(self,obj=None,is_header=False):
        """班级人数"""
        if is_header:
            return '班级人数'
        return 80
    combination_filter = [
        v1.FilterOption('school',),
        v1.FilterOption('course',True)
    ]
    list_dsplay = ['school',course_semester,num,'start_date']
    edit_link = [course_semester]
v1.site.register(models.ClassList,ClassListConfig)

v1.site.register(models.Customer,CustomerConfig)

class ConsultRecordConfig(v1.StarkConfing):
    """
    客户跟进记录
    """
    list_dsplay = ['customer','consultant','date']
    combination_filter =[
        v1.FilterOption('customer')
    ]
    def changelist_view(self,request,*args,**kwargs):
        customer = request.GET.get('customer')
        # session中获取当前用户ID
        current_login_user_id = 2
        ct = models.Customer.objects.filter(consultant=current_login_user_id,id=customer).count()
        if not ct:
            return HttpResponse('别抢客户呀...')
        return super(ConsultRecordConfig,self).changelist_view(request,*args,**kwargs)

v1.site.register(models.ConsultRecord,ConsultRecordConfig)