import time
from datetime import timedelta, datetime

from django.utils import timezone

from core.models import Semestre
from stock.helper import get_sales_from_payutc, update_export_csv, update_sharepoint
from stock.models import Sales


def request_sales():
    current_semester = Semestre.objects.latest('id')

    try:
        last_sale = Sales.objects.latest('timestamp')
    except:
        last_sale = None

    if last_sale is not None:
        current_timestamp = last_sale.timestamp + timedelta(seconds=1)
    else:
        start_date = current_semester.start_date
        current_timestamp = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))

    while True:
        current_timestamp_plus_t = datetime.combine(current_timestamp, datetime.max.time())

        print(
            "{} : Request sales between {} and {}".format(timezone.now(), current_timestamp, current_timestamp_plus_t))

        transactions = get_sales_from_payutc(current_timestamp, current_timestamp_plus_t)

        for transaction in reversed(transactions):
            Sales.objects.create(
                timestamp=timezone.make_aware(
                    datetime.strptime(transaction['timestamp'], "%Y-%m-%dT%H:%M:%S")
                ),
                item_name=transaction['item_name'],
                quantity=transaction['quantity'],
                total_price=transaction['total_price'],
                semester_id=current_semester
            )

        current_timestamp = datetime.combine(current_timestamp_plus_t + timedelta(hours=1), datetime.min.time())

        if datetime.now() < current_timestamp:
            try:
                update_export_csv()
                update_sharepoint('stock/export.csv', 'export.csv')
            except Exception as err:
                print('Requester error : {}'.format(err))
                pass
            time.sleep((current_timestamp - datetime.now()).seconds)
        else:
            time.sleep(10)

        if current_timestamp > datetime.combine(current_semester.end_date, datetime.max.time()):
            break
