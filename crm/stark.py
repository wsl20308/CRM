#! usr/bin/env python
# -*- coding: utf-8 -*-
from stark.service import v1
from crm import models
class DepartmentConfig(v1.StarkConfing):
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
    list_dsplay = ['name','username','email','depart']
    edit_link = ['depart']
    combination_filter = [
        v1.FilterOption('depart',text_func_name=lambda x:str(x),val_func_name=lambda x:x.code,),
    ]
v1.site.register(models.UserInfo,UserInfoConfig)