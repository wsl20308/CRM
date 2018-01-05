#! usr/bin/env python
# -*- coding: utf-8 -*-
from stark.service import v1
from . import models
class UserConfing(v1.StarkConfing):
    list_dsplay = ['id','username','email']
    edit_link = ['username']
v1.site.register(models.User,UserConfing)
class RoleConfing(v1.StarkConfing):
    list_dsplay = ['id','title',]
    edit_link = ['title']
v1.site.register(models.Role,RoleConfing)
class PermissionConfig(v1.StarkConfing):
    list_dsplay = ['id','title','url','menu_gp','code']
    edit_link = ['title']
v1.site.register(models.Permission,PermissionConfig)
class GroupConfig(v1.StarkConfing):
    list_dsplay = ['id','caption','menu']
    edit_link = ['caption']
v1.site.register(models.Group,GroupConfig)
class MenuConfig(v1.StarkConfing):
    list_dsplay = ['id','title']
    edit_link = ['title']
v1.site.register(models.Menu,MenuConfig)