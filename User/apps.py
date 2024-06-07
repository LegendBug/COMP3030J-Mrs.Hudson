from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "User"

    def ready(self):
        from .models import GlobalSetting
        authorization_code = 'LFobuC5UHf6CT3BlbkFJldFawYhXcw0zQ8D93sBo'
        GlobalSetting.objects.get_or_create(key='AUTHORIZATION_CODE', defaults={'value': authorization_code})
