from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from mainapp.functions.CPR_GraphDB import backup_data

class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'

    def ready(self):
        scheduler = BackgroundScheduler()
        # 매일 자정마다 DB 덤프 실행
        scheduler.add_job(backup_data, 'cron', hour=14, minute=20)
        scheduler.start()
