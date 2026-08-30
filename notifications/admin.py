from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title','user']
admin.site.register(Notification, NotificationAdmin)