from rest_framework.pagination import PageNumberPagination

class SmallResultPagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page"
    
class LargeResultPagination(PageNumberPagination):
    page_size = 30
    page_query_param = "page"