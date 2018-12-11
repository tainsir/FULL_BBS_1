from django.shortcuts import render, redirect, HttpResponse, reverse
from django.http import JsonResponse
from django.contrib import auth
from django.views import View
from BBS_app import func, MyForms, models
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F
import json, os, time, threading
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from bs4 import BeautifulSoup
from FULL_BBS import settings
from django.core.mail import send_mail


# Create your views here.

class Home(View):
    def get(self, request):
        user = request.user
        ret = user.is_authenticated()
        article_list = models.Article.objects.all().order_by('-create_time')
        # 分页器
        paginator = Paginator(article_list, 3)
        try:
            current_page_num = int(request.GET.get('page'))
            current_page = paginator.page(current_page_num)
        except Exception as e:
            current_page_num = 1
            current_page = paginator.page(current_page_num)
        if paginator.num_pages > 11:
            if current_page_num - 5 < 1:
                page_range = range(1, 12)
            elif current_page_num + 5 > paginator.num_pages:
                page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
            else:
                page_range = range(current_page_num - 5, current_page_num + 6)
        else:
            page_range = paginator.page_range
        return render(request, 'home/home_page.html', locals())


class Register(View):
    def get(self, request):
        title = '用户注册'
        my_forms = MyForms.RegForms()
        if request.GET:
            my_forms = MyForms.RegForms(request.GET)
            if my_forms.is_valid():
                error = {'status': 100, 'msg': '用户名校验通过'}
            else:
                error = {'status': 200, 'msg': my_forms.errors}
            return JsonResponse(error)
        return render(request, 'func/register.html', locals())

    def post(self, request):
        error = {'status': 100, 'msg': '注册成功'}
        my_forms = MyForms.RegForms(request.POST)
        if my_forms.is_valid():
            dic = my_forms.cleaned_data
            dic.pop('re_password')
            my_file = request.FILES.get('my_file')
            print(my_file)
            if my_file:
                dic['avatar'] = my_file
            models.UserInfo.objects.create_user(**dic)
        else:
            error['status'] = 200
            error['msg'] = my_forms.errors
        return JsonResponse(error)


class Login(View):
    def get(self, request):
        return render(request, 'func/login.html', {'title': '用户登录'})

    def post(self, request):
        dic = {'status': 100, 'msg': '登录成功！'}
        ret = json.loads(request.body.decode('utf-8'))
        if request.session['valid_code'].upper() == ret['valid_code'].upper():
            user = auth.authenticate(request, username=ret['username'], password=ret['password'])
            if user:
                auth.login(request, user)
            else:
                dic['status'] = 200
                dic['msg'] = '用户名或密码错误！'
        else:
            dic['status'] = 200
            dic['msg'] = '验证码输入错误！'
        return JsonResponse(dic)


class Logout(View):
    def get(self, request):
        auth.logout(request)
        return redirect(reverse('home'))


class GetValidCode(View):
    def get(self, request):
        data = func.get_valid_code(request)
        return HttpResponse(data)


class SetPassword(View):
    def get(self, request):
        return render(request, 'func/set_password.html', locals())

    def post(self, request):
        dic = {'status': 100, 'msg': '登录成功！'}
        data = json.loads(request.body.decode('utf-8'))
        ret = request.user.check_password(data['old_password'])
        if ret:
            if data['old_password'] == data['re_password']:
                request.user.set_password(data['new_password'])
                request.user.save()
            else:
                dic['status'] = 200
                dic['msg'] = '两次密码输入不一致'
        else:
            dic['status'] = 200
            dic['msg'] = '旧密码输入错误'
        return JsonResponse(dic)


class ModifyHead(View):
    def get(self, request):
        return render(request, 'func/modify_head.html')

    def post(self, request):
        my_file = request.FILES.get('my_file')
        if my_file:
            request.user.avatar = my_file
            request.user.save()
        return JsonResponse({'msg': 'ok'})


class Blog(View):
    def get(self, request, site_name, *args, **kwargs):
        obj = models.Blog.objects.filter(site_name=site_name).first()
        if obj:
            user = models.UserInfo.objects.filter(blog__site_name=site_name).first()
            ret = request.user.is_authenticated()
            count = models.Article.objects.filter(blog=user.blog).count()
            article_list = user.blog.article_set.all()
            param = kwargs.get('param')
            condition = kwargs.get('condition')
            if condition == 'category':
                article_list = article_list.filter(category__pk=param)

            elif condition == 'tag':
                article_list = article_list.filter(tag__pk=param)

            return render(request, 'blog/blog.html', locals())
        else:
            return render(request, 'func/error.html')


class CreateBlog(View):
    def get(self, request):
        return render(request, 'blog/create_blog.html')

    def post(self, request):
        title = request.POST.get('title')
        site_name = request.POST.get('site_name')
        theme = request.POST.get('theme')
        if title and site_name and theme:
            blog = models.Blog.objects.create(title=title, site_name=site_name, theme=theme)
            request.user.blog_id = blog
            request.user.blog_id = blog
            request.user.save()
            return redirect(reverse('home'))
        else:
            return redirect(reverse('create_blog'))


class ArticleDetail(View):
    def get(self, request, site_name, *args, **kwargs):
        pk = kwargs.get('id')
        username = request.user.username
        user = models.UserInfo.objects.filter(blog__site_name=site_name).first()
        count = models.Article.objects.filter(blog=user.blog).count()
        article = models.Article.objects.filter(pk=pk).first()
        comment_list = article.comment_set.all()
        ret = request.user.is_authenticated()
        return render(request, 'blog/article_detail.html', locals())


class UpAndDown(View):
    def post(self, request):
        dic = {'status': 100, 'msg': None}
        if request.user.is_authenticated:
            article_id = request.POST.get('article_id')
            is_up = request.POST.get('is_up')
            if is_up:
                is_up = True
            else:
                is_up = False
            ret = models.UpAndDown.objects.filter(user=request.user, article_id=article_id).first()
            if not ret:
                with transaction.atomic():
                    models.UpAndDown.objects.create(is_up=is_up, article_id=article_id, user=request.user)
                    if is_up:
                        models.Article.objects.filter(pk=article_id).update(up_count=F('up_count') + 1)
                        dic['msg'] = '推荐成功'
                    else:
                        models.Article.objects.filter(pk=article_id).update(up_count=F('down_count') + 1)
                        dic['msg'] = '反对成功'
            else:
                if ret.is_up:
                    dic['status'] = 200
                    dic['msg'] = '您已经推荐过了'
                else:
                    dic['status'] = 200
                    dic['msg'] = '您已经反对过了'
            dic['up_count'] = models.Article.objects.filter(pk=article_id).first().up_count
            dic['down_count'] = models.Article.objects.filter(pk=article_id).first().down_count

        else:
            dic['status'] = 300
            dic['msg'] = '请先登录！'
        return JsonResponse(dic)


class CommitComment(View):
    def post(self, request):
        dic = {'status': 100, 'msg': None}
        user = request.user
        article_id = request.POST.get('article_id')
        content = request.POST.get('content')
        pid = request.POST.get('pid')
        with transaction.atomic():
            ret = models.Comment.objects.create(article_id=article_id, content=content, parent_id=pid, user=user)
            models.Article.objects.filter(pk=article_id).update(comment_count=F('comment_count') + 1)
            dic['msg'] = '评论成功'
            dic['time'] = ret.create_time.strftime('%Y-%m-%d %X')
            dic['content'] = ret.content
            dic['username'] = ret.user.username
        article_name = ret.article.title
        recipients = models.UserInfo.objects.filter(blog__article__nid=article_id).first().email
        import threading
        t = threading.Thread(target=send_mail, args=(
            '您的文章收到一条新的评论',
            '用户[%s]在[%s]评论了您的文章《%s》' % (user.username, time.strftime("%Y-%m-%d %X"), article_name),
            settings.DEFAULT_FROM_EMAIL,
            [recipients, ],
        ))
        t.start()
        return JsonResponse(dic)


class RemoveComment(View):
    def post(self, request):
        dic = {'status': 100, 'msg': None}
        user = request.user
        comment_id = request.POST.get('comment_id')
        article_id = request.POST.get('article_id')
        with transaction.atomic():
            models.Comment.objects.filter(pk=comment_id, user=user).delete()
            models.Article.objects.filter(pk=article_id).update(comment_count=F('comment_count') - 1)
        dic['msg'] = '删除成功'
        return JsonResponse(dic)


class BackendAdmin(View):
    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        print(user.username)
        article_list = models.Article.objects.filter(blog=user.blog)
        return render(request, 'back/backend_admin.html', locals())


class RedactCategory(View):
    @method_decorator(login_required)
    def get(self, request):
        category_list = models.Category.objects.filter(blog=request.user.blog)
        return render(request, 'back/redact_category.html', locals())

    def post(self, request):
        dic = {'status': 100, 'msg': None}
        pk = request.POST.get('id')
        category = request.POST.get('category')
        if category:
            ret = models.Category.objects.filter(title=category, blog=request.user.blog).first()
            if not ret:
                if pk:
                    models.Category.objects.filter(pk=pk, blog=request.user.blog).update(title=category)
                else:
                    models.Category.objects.create(title=category, blog=request.user.blog)
                dic['msg'] = '添加成功'
            else:
                dic['status'] = 200
                dic['msg'] = '该分类已存在！'
        else:
            dic['status'] = 300
            dic['msg'] = '分类名不能为空！'
        return JsonResponse(dic)


class DeleteCategory(View):
    def get(self, request, pk):
        models.Category.objects.filter(pk=pk, blog=request.user.blog).delete()
        return redirect(reverse('redact_category'))


class RedactTag(View):
    @method_decorator(login_required)
    def get(self, request):
        tag_list = models.Tag.objects.filter(blog=request.user.blog)
        return render(request, 'back/redact_tag.html', locals())

    def post(self, request):
        dic = {'status': 100, 'msg': None}
        pk = request.POST.get('id')
        tag = request.POST.get('tag')
        if tag:
            ret = models.Tag.objects.filter(title=tag, blog=request.user.blog).first()
            if not ret:
                if pk:
                    models.Tag.objects.filter(pk=pk, blog=request.user.blog).update(title=tag)
                else:
                    models.Tag.objects.create(title=tag, blog=request.user.blog)
                dic['msg'] = '添加成功'
            else:
                dic['status'] = 200
                dic['msg'] = '该标签已存在！'
        else:
            dic['status'] = 300
            dic['msg'] = '标签名不能为空！'
        return JsonResponse(dic)


class DeleteTag(View):
    def get(self, request, pk):
        models.Tag.objects.filter(pk=pk, blog=request.user.blog).delete()
        return redirect(reverse('redact_tag'))


class AddArticle(View):
    @method_decorator(login_required)
    def get(self, request):
        category_list = models.Category.objects.filter(blog=request.user.blog)
        if not category_list:
            return render(request, 'back/redact_category.html')
        tag_list = models.Tag.objects.filter(blog=request.user.blog)
        if not tag_list:
            return render(request, 'back/redact_tag.html')
        return render(request, 'back/add_article.html', locals())

    def post(self, request):
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_list = request.POST.getlist('tag_list[]')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        desc = soup.text[0:150]
        ret = models.Article.objects.create(title=title, content=str(soup), desc=desc, blog=request.user.blog,
                                            category_id=category_id)
        for t in tag_list:
            models.ArticleToTag.objects.create(article_id=ret.pk, tag_id=t)
        return JsonResponse({'status': 100})


class UpdateArticle(View):
    def get(self, request, pk):
        article = models.Article.objects.filter(blog=request.user.blog)
        pk_list = []
        for i in article:
            pk_list.append(i.pk)
        if int(pk) in pk_list:
            category_list = models.Category.objects.filter(blog=request.user.blog)
            tag_list = models.Tag.objects.filter(blog=request.user.blog)
            return render(request, 'back/update_article.html', locals())
        else:
            return redirect(reverse('backend'))

    def post(self, request, pk):
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        desc = soup.text[0:150]
        models.Article.objects.filter(pk=pk).update(title=title, content=str(soup), desc=desc,
                                                    category_id=category_id)
        tag_list = request.POST.getlist('tag_list[]')
        models.ArticleToTag.objects.filter(article_id=pk).delete()
        for t in tag_list:
            models.ArticleToTag.objects.create(article_id=pk, tag_id=t)
        return JsonResponse({'status': 100})


class GetArticle(View):
    def get(self, request, pk):
        tags = models.Tag.objects.filter(articletotag__article_id=pk).all()
        category = models.Category.objects.filter(article__nid=pk).first()
        article = models.Article.objects.filter(pk=pk).first()
        tag_list = []
        for i in tags:
            tag_list.append(i.pk)
        return JsonResponse({
            'title': article.title,
            'content': article.content,
            'tag_list': tag_list,
            'category': [category.pk]
        })


class DeleteArticle(View):
    def get(self, request, pk):
        models.Article.objects.filter(pk=pk).delete()
        return redirect(reverse('backend'))


class UploadImg(View):
    def post(self, request):

        my_file = request.FILES.get('my_file')
        path = os.path.join(settings.BASE_DIR, 'media', 'img')
        if not os.path.isdir(path):
            os.mkdir(path)
        file_path = os.path.join(path, my_file.name)
        with open(file_path, 'wb') as f:
            for line in my_file:
                f.write(line)
        dic = {'error': 0, 'url': '/media/img/%s' % my_file.name}
        return JsonResponse(dic)


class Error(View):
    def get(self, request):
        return render(request, 'func/error.html')


def clear():
    """
    每7天执行一次清理服务器无用图片、无用头像
    :return:
    """
    from BBS_app import models
    from FULL_BBS import settings
    from bs4 import BeautifulSoup
    contents = models.Article.objects.all().values('content')
    ll = []
    for content in contents:
        soup = BeautifulSoup(content['content'], 'html.parser')
        tags = soup.find_all(name='img')
        for tag in tags:
            ll.append(tag.attrs['src'])
    path = os.path.join(settings.BASE_DIR, 'media', 'img')
    img_list = os.listdir(path)
    for i in img_list:
        img_path = '/' + 'media' + '/' + 'img' + '/' + i
        if img_path not in ll:
            os.remove(os.path.join(settings.BASE_DIR, 'media', 'img', i))
    print('clear - 1')
    # 取出服务器内所有头像文件的名字
    avatar_list = os.listdir(os.path.join(settings.BASE_DIR, 'media', 'avatar'))
    user = models.UserInfo.objects.all().values_list('avatar')
    li = []
    for i in range(user.count()):
        li.append(user[i][0])
    for i in avatar_list:
        i2 = 'avatar' + '/' + i
        if i2 not in li:
            os.remove(os.path.join(settings.BASE_DIR, 'media', 'avatar', i))
    print('clear - 2')
    timer = threading.Timer(60 * 60 * 24 * 7, clear)  # 60 * 60 * 24 * 7 每7天执行clear函数
    timer.start()


timer = threading.Timer(1, clear)
timer.start()
