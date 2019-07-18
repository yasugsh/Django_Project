from project_admin.project_express.project_express import ProjectExpress
from .models import ExpressInfo
import celery


@celery.task
def celery_place_order(data, staff_id):
    """使用Celery + djcelery实现快递异步下单
    使用djcelery可以在任务中方便的直接操作Django数据库，
    而且最终的任务可以在Django的后台中查看和修改相关的任务"""

    # 创建快递操作对象
    express = ProjectExpress()
    result = express.place_order(request_data=data)

    if result.get('Success'):
        ExpressInfo.objects.create(
            order_id=result['Order']['OrderCode'],
            staff_id=staff_id,
            logistic_code=result['Order']['LogisticCode'],  # 快递单号
            shipper_code=result['Order']['ShipperCode']  # 快递公司编码
        )
        return True
    return False
