from rest_framework.pagination import PageNumberPagination

from django.conf import MAX_PAGE_SIZE


class Pagination(PageNumberPagination):
    page_size = MAX_PAGE_SIZE
    page_size_query_param = 'limit'
