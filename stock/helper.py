import csv
import os
from typing import List

from shareplum import Office365
from shareplum import Site
from shareplum.site import Version

from core.models import Semestre
from core.services.payutc import PayutcClient
from core.settings_confidential import SHAREPOINT_URL, SHAREPOINT_USERNAME, SHAREPOINT_PASSWORD
from stock.models import Sales


def update_sharepoint(path_to_file, save_name) -> None:
    try:
        authcookie = Office365(
            SHAREPOINT_URL,
            username=SHAREPOINT_USERNAME,
            password=SHAREPOINT_PASSWORD
        ).GetCookies()

        site = Site('https://etuutcfr.sharepoint.com/sites/PicassoSharePoint', version=Version.v2016,
                    authcookie=authcookie)

        folder = site.Folder('Documents partages/')

        with open(path_to_file, 'rb') as file:
            folder.upload_file(file, save_name)

        print('Sharepoint updated')
    except Exception as err:
        print(err)


def update_export_csv() -> None:
    file_name = 'stock/export.csv'

    current_semester = Semestre.objects.latest('id')

    sales = Sales.objects.filter(semester_id=current_semester.id)

    if os.path.exists(file_name):
        os.remove(file_name)

    with open(file_name, 'x') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Item Name', 'Quantity', 'Total Price'])
        for sale in sales:
            writer.writerow([sale.timestamp, sale.item_name, sale.quantity, sale.total_price])

    print("export.csv saved")

"""
WIP

def update_supply_csv() -> None:
    file_name = 'stock/supply.csv'

    current_semester = Semestre.objects.latest('id')

    supply = Supply.objects.filter(semester_id=current_semester.id)

    if os.path.exists(file_name):
        os.remove(file_name)

    with open(file_name, 'x') as file:
        writer = csv.writer(file)
        writer.writerow([])
        for s in supply:
            writer.writerow([])
"""


def get_sales_from_payutc(start_time, end_time) -> List:
    try:
        p = PayutcClient()
        p.login_admin()

        ROW_COUNT = 20000

        sales = p.get_sales(start=start_time, end=end_time, row_count=ROW_COUNT)

        transactions = []

        for sale in sales['transactions']:
            for row in sale['rows']:
                transactions.append({
                    'timestamp': sale['validated'],
                    'item_name': row['item']['name'],
                    'quantity': row['payments'][0]['quantity'],
                    'total_price': row['payments'][0]['amount'] / 100
                })

        return transactions
    except Exception as err:
        raise Exception('Cannot get sales from payutc with error : {}'.format(err))
