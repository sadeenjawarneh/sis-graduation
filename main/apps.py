from django.apps import AppConfig

class MainConfig(AppConfig):
    # هذا السطر يمنع ظهور تحذيرات (Warnings) بخصوص نوع الـ ID في الداتابيز
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    # يمكنك إضافة هذا السطر ليظهر اسم التطبيق بالعربية في لوحة التحكم
    verbose_name = 'نظام إدارة مشاريع التخرج'