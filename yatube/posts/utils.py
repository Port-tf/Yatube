from django.conf import settings
from django.core.paginator import Paginator


def paginator_posts(request, posts):
    paginator = Paginator(posts, settings.PAGINATOR_POST_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
