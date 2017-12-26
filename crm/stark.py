#! usr/bin/env python
# -*- coding: utf-8 -*-
from stark.service import v1
from crm import models
class DepartmentConfig(v1.StarkConfing):
    list_dsplay = ['id','title']
    edit_link = ['title']
v1.site.register(models.Department,DepartmentConfig)