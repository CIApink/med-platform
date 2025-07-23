from django.contrib import admin
from .models import UserProfile, DataDownload


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'organization', 'created_at')
    list_filter = ('created_at', 'organization')
    search_fields = ('user__username', 'user__email', 'phone', 'organization')


@admin.register(DataDownload)
class DataDownloadAdmin(admin.ModelAdmin):
    list_display = ('user', 'dataset_name', 'download_time', 'file_size')
    list_filter = ('download_time', 'dataset_name')
    search_fields = ('user__username', 'dataset_name')
    readonly_fields = ('download_time',)
