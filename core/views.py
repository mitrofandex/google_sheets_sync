import gspread
from bs4 import BeautifulSoup
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import datetime

from core.models import Order
from sheets.settings import (
    SERVICE_KEY_PATH,
    SHEET_ID,
)

sheets_service = gspread.service_account(filename=SERVICE_KEY_PATH)
sheet = sheets_service.open_by_key(SHEET_ID)


def convert_to_rub(usd: float):
    today = datetime.date.today()
    response = requests.get(f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={today.strftime("%d/%m/%Y")}')
    soup = BeautifulSoup(response.text, "html.parser")
    rate = float(soup.select_one("Valute[ID='R01235'] > value").text.replace(",", "."))
    return usd * rate


class GoogleDriveWebhookView(APIView):
    """
    Google Drive Push Notifications API Webhook (https://developers.google.com/drive/api/guides/push)
    Set it up to monitor file with SHEET_ID and get updates.
    """
    def post(self, request):
        records = sheet.sheet1.get_all_records()

        Order.objects.all().delete()

        Order.objects.bulk_create(
            [
                Order(
                    external_id=record['заказ №'],
                    date=datetime.datetime.strptime(record['срок поставки'], '%d.%m.%Y'),
                    cost_usd=record['стоимость,$'],
                    cost_rub=convert_to_rub(record['стоимость,$'])
                )
                for record in records
            ]
        )
        return Response(status=200)
