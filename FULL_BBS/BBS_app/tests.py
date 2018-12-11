import os

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FULL_BBS.settings")
    import django

    # 启动django服务
    django.setup()

    from BBS_app import models
    from FULL_BBS import settings
    from bs4 import BeautifulSoup

    """
    models.UserInfo.objects.create_superuser(username='HGQ', password='123123', phone='13695797487',email='he_guiqing@qq.com')
    """


    def clear():
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

    clear()