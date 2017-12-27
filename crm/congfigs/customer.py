#! usr/bin/env python
# -*- coding: utf-8 -*-
from stark.service import v1
from crm import models
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.shortcuts import redirect, HttpResponse, render
from django.conf.urls import url
class CustomerConfig(v1.StarkConfing):
    """客户管理"""
    def dsplay_gender(self,obj=None,is_header=False):
        if is_header:
            return "性别"
        return obj.get_gender_display()
    def dsplay_education(self,obj=None,is_header=False):
        if is_header:
            return "学历"
        return obj.get_education_display()

    list_dsplay = ['qq', 'name', dsplay_gender, dsplay_education, 'graduation_school']
    edit_link = ['name']

    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        patterns = [
            # url(r'^(\d+)/(\d+)/dc/$', self.wrap(self.delete_course), name="%s_%s_dc" % app_model_name),
            url(r'public/$',self.wrap(self.public_view),name="%s_%s_public"%app_model_name),
            url(r'user/$', self.wrap(self.user_view), name="%s_%s_user" % app_model_name),
        ]
        return patterns
    def public_view(self,request):
        """
        :return: 公共客户资源
                条件：未报名 并且 （ 15天未成单(当前时间-15 > 接客时间) or  3天未跟进(当前时间-3天>最后跟进日期) ） Q对象
        """
        import datetime
        from django.db.models import Q
        ctime = datetime.datetime.now().date()
        no_deal = ctime-datetime.timedelta(days=15)        #十五天未成单，根据接单时间
        no_follow = ctime-datetime.timedelta(days=3)       #三天未跟进，根据最后跟进日期

        coustomer_list = models.Customer.objects.filter(Q(recv_date__lt=no_deal)|Q(last_consult_date__lt=no_follow),status=2)
        return render(request,"public_view.html",{'coustomer_list':coustomer_list})

    def user_view(self,request):
        """
        :param rquest:当前登录用户的所有客户
        :return:
        """
        session_user_id = 1
        customer = models.CustomerDistribution.objects.filter(user_id=session_user_id).order_by('status')
        return render(request,"user_view.html",{"customer":customer})