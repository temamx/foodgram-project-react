from rest_framework.pagination import PageNumberPagination

from foodgram.settings import MAX_PAGE_SIZE


class Pagination(PageNumberPagination):
    page_size = MAX_PAGE_SIZE
    page_size_query_param = 'limit'
