from django.template import Library
from django.urls import reverse
from stark.service.v1 import site
register = Library()
@register.inclusion_tag('stark/form.html')
def form(model_form_obj):
    new_form = []
    for bfield in model_form_obj:
        temp = {'is_popup': False, 'item': bfield}
        # field是ModelForm读取对应的models.类，然后根据每一个数据库字段，生成Form的字段
        from django.forms.boundfield import BoundField
        from django.db.models.query import QuerySet
        from django.forms.models import ModelChoiceField
        if isinstance(bfield.field, ModelChoiceField):
            related_class_name = bfield.field.queryset.model
            if related_class_name in site._registry:
                app_model_name = related_class_name._meta.app_label, related_class_name._meta.model_name
                base_url = reverse("stark:%s_%s_add" % app_model_name)
                popurl = "%s?_popbackid=%s" % (base_url, bfield.auto_id)
                temp['is_popup'] = True
                temp['popup_url'] = popurl
        new_form.append(temp)
    return {'form':new_form}