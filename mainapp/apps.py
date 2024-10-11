from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from mainapp.views import dump_neo4j_db

class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'

    def ready(self):
        scheduler = BackgroundScheduler()
        # 매일 자정마다 DB 덤프 실행
        scheduler.add_job(dump_neo4j_db, 'cron', hour=0, minute=0)
        scheduler.start()
