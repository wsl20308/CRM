"""radis实现自动分配ID"""
import redis
from crm import models
POOL = redis.ConnectionPool(host='47.93.4.198', port=6379, password='123123')
CONN = redis.Redis(connection_pool=POOL)
class AutoSale(object):
    @classmethod
    def fetch_users(cls):
        sales = models.SaleRank.objects.all().order_by('-weight')

        sale_id_list = []
        count = 0
        while True:
            flag = False
            for row in sales:
                if count < row.num:
                    sale_id_list.append(row.user_id)
                    flag = True
            count += 1
            if not flag:
                break

        if sale_id_list:
            CONN.rpush('sale_id_list', *sale_id_list)  # 自动pop数据
            CONN.rpush('sale_id_list_origin', *sale_id_list)  # 原来的数据
            return True
        return False

    @classmethod
    def get_sale_id(cls):
        # 查看原来数据是否存在
        sale_id_origin_count = CONN.llen('sale_id_list_origin')
        if not sale_id_origin_count:
            # 去数据库中获取数据，并赋值给： 原数据，pop数据
            status = cls.fetch_users()
            if not status:
                return None

        user_id = CONN.lpop('sale_id_list')
        if user_id:
            return user_id

        reset = CONN.get('sale_id_reset')
        # 要重置
        if reset:
            CONN.delete('sale_id_list_origin')
            status = cls.fetch_users()
            if not status:
                return None
            CONN.delete('sale_id_reset')
            return CONN.lpop('sale_id_list')
        else:
            ct = CONN.llen('sale_id_list_origin')
            for i in range(ct):
                v = CONN.lindex('sale_id_list_origin', i)
                CONN.rpush('sale_id_list', v)
            return CONN.lpop('sale_id_list')
    @classmethod
    def reset(cls):
        CONN.set('sale_id_reset',1)
    @classmethod
    def rollback(cls,nid):
        CONN.lpush('sale_id_list',nid)