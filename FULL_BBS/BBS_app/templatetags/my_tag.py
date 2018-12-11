from django.template import Library
from BBS_app import models
from django.db.models import Count

register = Library()


@register.inclusion_tag('blog/sidebar.html')
def sidebar(site_name):
    user = models.UserInfo.objects.filter(blog__site_name=site_name).first()
    if user:
        category_list = models.Category.objects.filter(blog__site_name=site_name).annotate(
            coun=Count('article__title')).values('title', 'coun', 'pk')

        tag_list = models.Tag.objects.filter(blog=user.blog).annotate(coun=Count('article__title')). \
            values('title', 'coun', 'pk')

        return {'category_list': category_list, 'tag_list': tag_list, 'site_name': site_name, 'user': user}
