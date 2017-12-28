#! usr/bin/env python
# -*- coding: utf-8 -*-
from stark.service import v1
from crm import models
from django.shortcuts import redirect, HttpResponse, render
from django.conf.urls import url
import datetime
from django.db.models import Q
from django.forms import ModelForm
from django.db import transaction
from utils import message

class SingleModelForm(ModelForm):
    """单条录入客户信息ModelForm"""
    class Meta:
        model = models.Customer
        exclude = ['consultant','status','recv_date','last_consult_date']


class CustomerConfig(v1.StarkConfing):
    """客户管理"""
    order_by = ["-status"]
    def dsplay_gender(self,obj=None,is_header=False):
        if is_header:
            return "性别"
        return obj.get_gender_display()
    def dsplay_education(self,obj=None,is_header=False):
        if is_header:
            return "学历"
        return obj.get_education_display()
    def display_status(self,obj=None,is_header=False):
        if is_header:
            return '状态'
        return obj.get_status_display()

    list_dsplay = ['qq', 'name', dsplay_gender, 'graduation_school',dsplay_education,'consultant',display_status]

    edit_link = ['name']

    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        patterns = [
            # url(r'^(\d+)/(\d+)/dc/$', self.wrap(self.delete_course), name="%s_%s_dc" % app_model_name),
            url(r'public/$',self.wrap(self.public_view),name="%s_%s_public"%app_model_name),
            url(r'user/$', self.wrap(self.user_view), name="%s_%s_user" % app_model_name),
            url(r'(\d+)/competition/$', self.wrap(self.competition_view), name="%s_%s_competition" % app_model_name),
            url(r'single/$', self.wrap(self.single_view), name="%s_%s_single" % app_model_name),
        ]
        return patterns

    def public_view(self,request):
        """
        :return: 公共客户资源
                条件：未报名 并且 （ 15天未成单(当前时间-15 > 接客时间) or  3天未跟进(当前时间-3天>最后跟进日期) ） Q对象
        """
        current_user_id = 2
        ctime = datetime.datetime.now().date()
        no_deal = ctime-datetime.timedelta(days=15)        #十五天未成单，根据接单时间
        no_follow = ctime-datetime.timedelta(days=3)       #三天未跟进，根据最后跟进日期

        # 方式二
        # q1 = Q()
        # q1.connector = 'OR'
        #
        # q1.children.append(("recv_date__lt", no_deal ))
        # q1.children.append(("last_consult_date__lt",no_follow ))
        #
        # customer_obj_list = models.Customer.objects.filter(q1, status=2).exclude(consultant_id=2)
        coustomer_list = models.Customer.objects.filter(Q(recv_date__lt=no_deal)|Q(last_consult_date__lt=no_follow),status=2)
        return render(request,"public_view.html",{'coustomer_list':coustomer_list,'current_user_id':current_user_id})

    def competition_view(self,request,nid):
        """
            抢单，点击公共用户的抢单按钮，抢单用户添加一条数据。
        :param request:
        :param nid:
        :return:
        """
        ctime = datetime.datetime.now().date()
        no_deal = ctime - datetime.timedelta(days=15)  # 十五天未成单，根据接单时间
        no_follow = ctime - datetime.timedelta(days=3)  # 三天未跟进，根据最后跟进日期

        current_user_id = 2

        row_cont = models.Customer.objects.filter(Q(recv_date__lt=no_deal) | Q(last_consult_date__lt=no_follow),
                            status=2 ,id=nid).exclude(consultant_id=current_user_id).update(consultant=current_user_id,recv_date=ctime,last_consult_date=ctime)
        if not row_cont:
            return HttpResponse("手速有点慢了，期待下次抢单")
        models.CustomerDistribution.objects.create(user_id=current_user_id,customer_id=nid,ctime=ctime)
        return HttpResponse("抢单成功")

    def single_view(self, request):
        """
        单条录入客户信息
        :param request:
        :return:
        """
        if request.method == "GET":
            form = SingleModelForm
            return render(request, "single_view.html", {'form': form})
        else:
            from xxxxxx import XXX
            form = SingleModelForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        # 客户表新增客户信息
                        sale_id = 2
                        ctime = datetime.datetime.now().date()
                        form.instance.consultant_id = sale_id
                        form.instance.recv_date = ctime
                        form.instance.last_consult_date = ctime
                        new_customer = form.save()
                        # 客户分配表，新增客户分配信息
                        models.CustomerDistribution.objects.create(user_id=sale_id, customer=new_customer, ctime=ctime)
                        # 发送消息，微信，邮件，短信
                        message.send_message('877252373@qq.com', '放哨', '客户分配', '恭喜您分配到一位客户，请跟进，期待您成单。')
                except Exception as e:
                    return HttpResponse("录入成功")
            else:
                return render(request, "single_view.html", {'form': form})

    def user_view(self,request):
        """
        :param rquest:当前登录用户的所有客户
        :return:
        """
        session_user_id = 2      #登录用户
        customer = models.CustomerDistribution.objects.filter(user_id=session_user_id).order_by('status')
        return render(request,"user_view.html",{"customer":customer})
