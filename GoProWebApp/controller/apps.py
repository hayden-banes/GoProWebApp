from django.apps import AppConfig


class ControllerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'controller'

    def ready(self):
        from .models import GoPro, Timelapse
        # print('PRE --')
        # print(GoPro.objects.all().values())
        GoPro.objects.all().update(connected=False, keep_alive_id=-1)
        Timelapse.objects.all().update(task_signal=False, task_id=-1)
        # print('POST --')
        # print(GoPro.objects.all().values())
