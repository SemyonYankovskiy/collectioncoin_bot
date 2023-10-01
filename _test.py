import random
from datetime import datetime, timedelta

from database.datacoin import DataCoin


date_from = datetime(year=2023, month=8, day=10)

while date_from != datetime(year=2023, month=9, day=11):
    print(date_from)
    DataCoin(
        telegram_id=726837488, datetime_=date_from, totla_sum=random.randrange(20_000, 30_000, step=125)
    ).save()
    date_from += timedelta(days=1)

