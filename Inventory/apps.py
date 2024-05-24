from django.apps import AppConfig

class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Inventory"  # 确保这里的路径正确指向你的 Inventory 应用
