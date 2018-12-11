from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """
    用户表：
        -- 个人站点表 一对一关系
    """
    nid = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=32, null=True, verbose_name='手机号')
    avatar = models.FileField(upload_to='avatar/', default='/avatar/default.jpg', verbose_name='头像')
    blog = models.OneToOneField(to='Blog', to_field='nid', null=True)


class Blog(models.Model):
    """
    个人站点表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, verbose_name='站点标题')
    site_name = models.CharField(max_length=32, verbose_name='站点名')
    theme = models.CharField(max_length=64, verbose_name='站点主题')

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    文章分类表：
        -- 个人站点表 一对多关系
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, verbose_name='文章标题')
    blog = models.ForeignKey(to='Blog', to_field='nid', null=True)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """
    文章标签表：
         -- 个人站点表 一对多关系
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, verbose_name='标签名')
    blog = models.ForeignKey(to='Blog', to_field='nid', null=True)

    def __str__(self):
        return self.title


class Article(models.Model):
    """
    文章表：
         -- 个人站点表 一对多关系
         -- 文章分类表 一对多关系
         -- 文章标签表 多对多关系
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章摘要')
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='文章创建时间')

    comment_count = models.IntegerField(default=0, verbose_name='评论个数')
    up_count = models.IntegerField(default=0, verbose_name='点赞个数')
    down_count = models.IntegerField(default=0, verbose_name='点踩个数')

    blog = models.ForeignKey(to='Blog', to_field='nid', null=True, blank=True)
    category = models.ForeignKey(to='Category', to_field='nid', null=True, blank=True)
    tag = models.ManyToManyField(to='Tag', through='ArticleToTag', through_fields=('article', 'tag'))

    def __str__(self):
        return self.title


class ArticleToTag(models.Model):
    """
    手动创建文章跟标签的第三张表：
        与文章表、文章标签表分别建立外键联系
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to='Article', to_field='nid')
    tag = models.ForeignKey(to='Tag', to_field='nid')

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]


class Comment(models.Model):
    """
    评论表：
        parent -- 子评论
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to='UserInfo', to_field='nid')
    article = models.ForeignKey(to='Article', to_field='nid')
    content = models.CharField(max_length=255, verbose_name='评论内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建文章时间')
    parent = models.ForeignKey(to='self', to_field='nid', null=True)


class UpAndDown(models.Model):
    """
    点赞点踩表:
        -- 用户信息表 一对多关系
        -- 文章表 一对多关系
        is_up 为 True ,点赞
        is_up 为 False ,点踩
        PS：一名用户对一篇文章只能进行一次点赞点踩
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to='UserInfo', to_field='nid')
    article = models.ForeignKey(to='Article', to_field='nid')
    is_up = models.BooleanField()

    class Meta:
        unique_together = [
            ('user', 'article'),
        ]
