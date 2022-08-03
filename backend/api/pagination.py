from rest_framework.pagination import PageNumberPagination

from backend.settings import PAGE_SIZE


class RecipePagination(PageNumberPagination):
    """
    Класс RecipePagination для создания пагинации.
    """
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
