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
from django.utils.safestring import mark_safe
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

    def display_course(self,obj=None,is_header=False):
        if is_header:
            return "咨询的课程"
        couse_list = obj.course.all()
        html = []
        for item in couse_list:
            temp = "<a class='glyphicon glyphicon-remove', style='display:inline-block;padding:5px 5px;border:1px solid blue;margin:2px;' href='/stark/crm/customer/%s/%s/delete_course/'>%s</a>" % (obj.pk, item.pk, item.name)
            html.append(temp)
        return mark_safe("".join(html))
    
    def delete_course(self,request,customer_id,course_id):
        """
        删除客户咨询的课程
        :param request:
        :param customer_id:
        :param course_id:
        :return:
        """
        customer_obj = self.model_class.objects.filter(pk=customer_id).first()
        customer_obj.course.remove(course_id)
        return redirect(self.get_changelist_url())
    def display_record(self,obj=None,is_header=None):
        if is_header:
            return "跟进记录"
        return mark_safe("<a href='/stark/crm/consultrecord/?customer=%s'>跟进记录</a>"%(obj.pk))


    list_dsplay = ['qq', 'name', dsplay_gender, 'graduation_school',dsplay_education,'consultant',display_status,display_course,display_record]

    edit_link = ['name']

    def extra_url(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        patterns = [
            url(r'^(\d+)/(\d+)/delete_course/$', self.wrap(self.delete_course), name="%s_%s_dc" % app_model_name),
            url(r'public/$',self.wrap(self.public_view),name="%s_%s_public"%app_model_name),
            url(r'user/$', self.wrap(self.user_view), name="%s_%s_user" % app_model_name),
            url(r'(\d+)/competition/$', self.wrap(self.competition_view), name="%s_%s_competition" % app_model_name),
            url(r'single/$', self.wrap(self.single_view), name="%s_%s_single" % app_model_name),
            url(r'multi/$', self.wrap(self.multi_view), name="%s_%s_multi" % app_model_name),
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
            form = SingleModelForm(request.POST)
            if form.is_valid():
                # 获取销售ID
                from distribution_customers import AutoSale
                sale_id = AutoSale.get_sale_id()
                if not sale_id:
                    return HttpResponse("无销售顾问，无法进行分配。")
                try:
                    with transaction.atomic():
                        # 客户表新增客户信息
                        ctime = datetime.datetime.now().date()
                        form.instance.consultant_id = sale_id
                        form.instance.recv_date = ctime
                        form.instance.last_consult_date = ctime
                        new_customer = form.save()
                        # 客户分配表，新增客户分配信息
                        models.CustomerDistribution.objects.create(customer=new_customer, user_id=sale_id,ctime=ctime)
                        # 发送消息，微信，邮件，短信
                        # message.send_message('877252373@qq.com', '放哨', '客户分配', '恭喜您分配到一位客户，请跟进，期待您成单。')
                except Exception as e:
                    # 创建客户和分配销售异常
                    AutoSale.rollback(sale_id)
                    return HttpResponse("录入异常")
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

    def multi_view(self,request):
        """
        批量导入
        :param request:
        :return:
        """
        if request.method == 'GET':
            return render(request,'multi_view.html')
        else:
            from django.core.files.uploadedfile import InMemoryUploadedFile
            file_obj = request.FILES.get('exfile')
            with open('xxxxxx.xlsx',mode='wb') as f:
                for chunk in file_obj:
                    f.write(chunk)
            # 作业2：不在创建临时 xxxxxx.xlsx 文件
            import xlrd
            workbook = xlrd.open_workbook('xxxxxx.xlsx')
            # sheet_names = workbook.sheet_names()
            # sheet = workbook.sheet_by_name('工作表1')
            sheet = workbook.sheet_by_index(0)
            maps = {
                0:'name',
                1:'qq',
            }

            for index in range(1,sheet.nrows):
                row = sheet.row(index)
                # {'name':"吧唧",'qq':9898}
                # print(row,type(row))
                row_dict = {}
                for i in range(len(maps)):
                    key = maps[i]
                    cell = row[i]
                    row_dict[key] = cell.value
                print(row_dict)
                # 自动获取ID
                # 录入客户表
                # 录入客户分配表
            return HttpResponse('上传成功')