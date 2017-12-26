#! usr/bin/env python
# -*- coding: utf-8 -*-
from stark.service import v1
from crm import models
class DepartmentConfig(v1.StarkConfing):
    """部门管理"""
    list_dsplay = ['id','title']
    # edit_link = ['title']
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
class CustomerConfig(v1.StarkConfing):
    """客户管理"""
    def dsplay_gender(self,obj=None,is_header=False):
        if is_header:
            return "性别"
        return obj.get_gender_display()
    list_dsplay = ['qq','name',dsplay_gender]
    edit_link = ['qq']
v1.site.register(models.Customer,CustomerConfig)