from django.apps import AppConfig

class InventoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Inventory"  # 确保这里的路径正确指向你的 Inventory 应用

    def ready(self):
        # 导入所有相关的信号处理函数
        import Inventory.signals  # 假设你将信号处理函数存放在 signals.py 文件中
