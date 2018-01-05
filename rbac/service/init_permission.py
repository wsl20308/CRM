from django.conf import settings


def init_permission(user,request):
    """
    初始化权限信息，获取权限信息并放置到session中。
    :param user:
    :param request:
    :return:
    """
    permission_list = user.roles.values('permissions__id',
                                        'permissions__title',              # 用户列表
                                        'permissions__url',
                                        'permissions__code',
                                        'permissions__menu_gp_id',         # 组内菜单ID，Null表示是菜单
                                        'permissions__group_id',
                                        'permissions__group__menu_id',     # 菜单ID
                                        'permissions__group__menu__title',#  菜单名称
                                        ).distinct()

    # 菜单相关（以后再匹配）
    sub_permission_list = []
    for item in permission_list:
        tpl = {
            'id':item['permissions__id'],
            'title':item['permissions__title'],
            'url':item['permissions__url'],
            'menu_gp_id':item['permissions__menu_gp_id'],
            'menu_id':item['permissions__group__menu_id'],
            'menu_title':item['permissions__group__menu__title'],
        }
        sub_permission_list.append(tpl)
    request.session[settings.PERMISSION_MENU_KEY] = sub_permission_list

    # 权限相关
    result = {}
    for item in  permission_list:
        group_id = item['permissions__group_id']
        code = item['permissions__code']
        url = item['permissions__url']
        if group_id in result:
            result[group_id]['codes'].append(code)
            result[group_id]['urls'].append(url)
        else:
            result[group_id] = {
                'codes':[code,],
                'urls':[url,]
            }

    request.session[settings.PERMISSION_URL_DICT_KEY] = result