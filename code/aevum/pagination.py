"""
Custom pagination classes for Aevum Health platform
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.conf import settings
import environ

env = environ.Env()


class StandardResultsPagination(PageNumberPagination):
    """
    Standard pagination class for all listing APIs
    Configurable via environment variables
    """
    page_size = env.int('PAGE_SIZE', default=20)
    page_size_query_param = 'page_size'
    max_page_size = env.int('MAX_PAGE_SIZE', default=100)
    
    def get_paginated_response(self, data):
        """
        Custom paginated response with additional metadata
        """
        return Response({
            'pagination': {
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'next_page': self.page.next_page_number() if self.page.has_next() else None,
                'previous_page': self.page.previous_page_number() if self.page.has_previous() else None,
            },
            'results': data
        })


class LargeResultsPagination(PageNumberPagination):
    """
    Pagination class for APIs that might return large datasets
    """
    page_size = env.int('LARGE_PAGE_SIZE', default=50)
    page_size_query_param = 'page_size'
    max_page_size = env.int('MAX_LARGE_PAGE_SIZE', default=200)
    
    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'next_page': self.page.next_page_number() if self.page.has_next() else None,
                'previous_page': self.page.previous_page_number() if self.page.has_previous() else None,
            },
            'results': data
        })


class SmallResultsPagination(PageNumberPagination):
    """
    Pagination class for APIs with typically smaller datasets
    """
    page_size = env.int('SMALL_PAGE_SIZE', default=10)
    page_size_query_param = 'page_size'
    max_page_size = env.int('MAX_SMALL_PAGE_SIZE', default=50)
    
    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'next_page': self.page.next_page_number() if self.page.has_next() else None,
                'previous_page': self.page.previous_page_number() if self.page.has_previous() else None,
            },
            'results': data
        })


# Convenience function to get pagination class based on type
def get_pagination_class(pagination_type='standard'):
    """
    Get pagination class based on type
    
    Args:
        pagination_type (str): 'standard', 'large', or 'small'
    
    Returns:
        Pagination class
    """
    pagination_classes = {
        'standard': StandardResultsPagination,
        'large': LargeResultsPagination,
        'small': SmallResultsPagination,
    }
    
    return pagination_classes.get(pagination_type, StandardResultsPagination) 