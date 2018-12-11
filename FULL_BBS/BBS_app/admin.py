from django.contrib import admin

# Register your models here.
from BBS_app import models

admin.site.register(models.UserInfo)
admin.site.register(models.Article)
admin.site.register(models.ArticleToTag)
admin.site.register(models.UpAndDown)
admin.site.register(models.Blog)
admin.site.register(models.Category)
admin.site.register(models.Comment)
admin.site.register(models.Tag)
