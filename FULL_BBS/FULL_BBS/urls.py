"""FULL_BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from BBS_app import views
from FULL_BBS import settings
from django.views.static import serve
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^favicon.ico$', RedirectView.as_view(url=r'static/favicon.ico')),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.Home.as_view(), name='home'),
    # 注册
    url(r'^register/', views.Register.as_view(), name='register'),
    # 获取验证码
    url(r'^get_valid_code/', views.GetValidCode.as_view(), name='get_valid_code'),
    # 登录
    url(r'^login/', views.Login.as_view(), name='login'),
    # 注销
    url(r'^logout/', views.Logout.as_view(), name='logout'),

    # 修改密码
    url(r'^set_password/', views.SetPassword.as_view(), name='set_password'),
    # 修改头像
    url(r'^modify_head/', views.ModifyHead.as_view(), name='modify_head'),
    # 创建个人站点
    url(r'^create_blog/', views.CreateBlog.as_view(), name='create_blog'),
    # 验证码
    url(r'^get_valid_code/', views.GetValidCode.as_view(), name='get_valid_code'),

    # 管理页面
    url(r'^backend/', views.BackendAdmin.as_view(), name='backend'),
    # 编辑分类
    url(r'^redact_category/', views.RedactCategory.as_view(), name='redact_category'),
    # 删除分类
    url(r'^delete_category/(?P<pk>\d+)', views.DeleteCategory.as_view(), name='delete_category'),
    # 编辑标签
    url(r'^redact_tag/', views.RedactTag.as_view(), name='redact_tag'),
    # 删除标签
    url(r'^delete_tag/(?P<pk>\d+)', views.DeleteTag.as_view(), name='delete_tag'),
    # 添加新文章
    url(r'^add_article/', views.AddArticle.as_view(), name='add_article'),
    # 修改文章
    url(r'^update_article/(?P<pk>\d+)', views.UpdateArticle.as_view(), name='update_article'),
    # 获取文章
    url(r'^get_article/(?P<pk>\d+)', views.GetArticle.as_view()),
    # 上传图片
    url(r'^upload_img/', views.UploadImg.as_view(), name='upload_img'),
    # 删除文章
    url(r'^delete_article/(?P<pk>\d+)', views.DeleteArticle.as_view(), name='delete_article'),
    # 点赞、评论、删除评论
    url(r'^UpAndDown/', views.UpAndDown.as_view()),
    url(r'^commit_comment/', views.CommitComment.as_view()),
    url(r'^remove_comment/', views.RemoveComment.as_view()),
    # 文章详情页面
    url(r'^(?P<site_name>[\w]+)/article/(?P<id>\d+)', views.ArticleDetail.as_view()),
    # 个人站点文章分类、个人站点页面
    url(r'^(?P<site_name>[\w]+)/(?P<condition>category|tag)/(?P<param>.*)', views.Blog.as_view()),
    url(r'^(?P<site_name>[\w]+)$', views.Blog.as_view(), name='blog'),

    url(r'', views.Error.as_view()),

]
