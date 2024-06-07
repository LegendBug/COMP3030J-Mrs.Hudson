from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "User"

    def ready(self):
        # Connect the post_migrate signal to the handler
        post_migrate.connect(create_default_global_settings, sender=self)


def create_default_global_settings(sender, **kwargs):
    from .models import GlobalSetting
    # Ensure that the default setting is created after the migration
    authorization_code = 'LFobuC5UHf6CT3BlbkFJldFawYhXcw0zQ8D93sBo'
    GlobalSetting.objects.get_or_create(key='AUTHORIZATION_CODE', defaults={'value': authorization_code})
