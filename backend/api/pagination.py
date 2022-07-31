from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    """
    Класс RecipePagination для создания пагинации.
    """
    page_size = 6
    page_size_query_param = 'limit'
