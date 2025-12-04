from django.db.models import Q, Count, Sum, F, Window
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear, TruncDay
from django.utils import timezone
from datetime import timedelta
import json
import urllib.parse

class AnalyticsQueryBuilder:
    """Utility class to build dynamic queries with filters"""
    
    OPERATORS = {
        'eq': 'exact',
        'gt': 'gt',
        'lt': 'lt',
        'gte': 'gte',
        'lte': 'lte',
        'contains': 'contains',
        'icontains': 'icontains',
        'ne': 'exact',
    }
    
    @staticmethod
    def parse_filters_string(filters_string):
        """Parse filters from URL string with proper decoding"""
        if not filters_string:
            return []
        
        # If it's already a list, return it
        if isinstance(filters_string, list):
            return filters_string
            
        # Try to parse as JSON
        try:
            # Handle URL encoded strings
            if isinstance(filters_string, str):
                # Remove URL encoding
                decoded = urllib.parse.unquote(filters_string)
                # Remove any escaped quotes
                decoded = decoded.replace('\\"', '"')
                filters = json.loads(decoded)
                return filters if isinstance(filters, list) else []
        except (json.JSONDecodeError, TypeError):
            # Try direct parsing
            try:
                filters = json.loads(filters_string)
                return filters if isinstance(filters, list) else []
            except (json.JSONDecodeError, TypeError):
                pass
        
        return []
    
    @classmethod
    def build_filters(cls, filters_json, logic='and'):
        """Build Q objects from filter JSON"""
        filters = cls.parse_filters_string(filters_json)
        
        if not filters:
            return Q()
        
        q_objects = []
        for filter_item in filters:
            if not isinstance(filter_item, dict):
                continue
                
            field = filter_item.get('field')
            operator = filter_item.get('operator', 'eq')
            value = filter_item.get('value')
            
            if not field:
                continue
            
            # Handle different operators
            if operator == 'ne':
                q = ~Q(**{f"{field}": value})
            elif operator in ['contains', 'icontains']:
                lookup = f"{field}__{operator}"
                q = Q(**{lookup: value})
            else:
                lookup = f"{field}__{cls.OPERATORS.get(operator, 'exact')}"
                q = Q(**{lookup: value})
            
            q_objects.append(q)
        
        if not q_objects:
            return Q()
        
        # Combine with AND or OR logic
        if logic.lower() == 'or':
            combined_q = Q()
            for q in q_objects:
                combined_q |= q
        else:
            combined_q = Q()
            for q in q_objects:
                combined_q &= q
        
        return combined_q
    
    @classmethod
    def apply_date_range(cls, queryset, start_date, end_date, date_field='viewed_at'):
        """Apply date range filter to queryset"""
        if start_date:
            queryset = queryset.filter(**{f"{date_field}__gte": start_date})
        if end_date:
            # Add one day to include the entire end date
            end_date = end_date + timedelta(days=1)
            queryset = queryset.filter(**{f"{date_field}__lt": end_date})
        return queryset
    
    @classmethod
    def get_time_trunc_func(cls, range_type):
        """Get appropriate truncation function for time range"""
        trunc_funcs = {
            'week': TruncWeek,
            'month': TruncMonth,
            'year': TruncYear,
            'day': TruncDay,
        }
        return trunc_funcs.get(range_type.lower(), TruncMonth)

class AnalyticsCalculator:
    """Utility class for analytics calculations"""
    
    @staticmethod
    def calculate_growth(current, previous):
        """Calculate growth percentage"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100