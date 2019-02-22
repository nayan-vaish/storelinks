from django.contrib import admin

from .models import SharedMusicLink, User, UserInfo, Friends

admin.site.register(SharedMusicLink)
admin.site.register(User)
admin.site.register(UserInfo)
admin.site.register(Friends)
