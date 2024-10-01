from flask_apscheduler import APScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timezone, timedelta
from bson import ObjectId

from libs.db import connect_to_mongodb

from src.merchant.service import MerchantService

scheduler = APScheduler()

merchant_service = MerchantService()


class WeeklyChargeFromMerchantsSchedulerService:
    def __init__(self, app) -> None:
        scheduler.init_app(app)
        scheduler.start()
        scheduler.add_job(id='weekly_charge_from_merchants_scheduler', func=self.weekly_charge_from_merchants_scheduler,
                          trigger=CronTrigger(day_of_week='sun', hour=0, minute=0))
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.weekly_charges_collection = self.db.weekly_charges

    def weekly_charge_from_merchants_scheduler(self) -> None:
        today = datetime.today()

        print(f'weekly_charge_from_merchants_scheduler - starting - {today}')

        current_timestamp = datetime.now(tz=timezone.utc)

        days_to_subtract = (today.weekday() - 0) % 7
        last_monday = today - timedelta(days=days_to_subtract)

        merchants = merchant_service.get_merchants()

        weekly_charges = []

        for merchant in merchants:
            weekly_charge = {
                'merchant_id': ObjectId(merchant['_id']),
                'from_date': last_monday,
                'to_date': today,
                'charge': 50,
                'status': 'PENDING',
                'created_at': current_timestamp,
                'updated_at': current_timestamp

            }

            weekly_charges.append(weekly_charge)

        weekly_charges_inserted_result = self.weekly_charges_collection.insert_many(weekly_charges)

        print(f'weekly_charge_from_merchants_scheduler - success : {weekly_charges_inserted_result}')
