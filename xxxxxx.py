from crm import models
class XXX(object):
    users = None
    iter_users = None
    reset_status = False
    @classmethod
    def fetch_users(cls):
        sales = models.SaleRank.objects.all().order_by('-weight')
        v = []
        cls.users = v
        print(v)
    @classmethod
    def get_sale_id(cls):
        if not cls.users:
            cls.fetch_users()
        if not cls.iter_users:
            cls.iter_users = iter(cls.users)
        try:
            user_id = next(cls.iter_users)
        except StopIteration as e:
            if cls.reset_status:
                cls.fetch_users()
                cls.reset_status = False
            cls.iter_users = iter(cls.users)
            user_id = cls.get_sale_id()
        return user_id
    @classmethod
    def reset(cls):
        cls.reset_status = True