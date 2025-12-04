from rest_framework import serializers

class BlogViewAnalyticsSerializer(serializers.Serializer):
    x = serializers.CharField()
    y = serializers.IntegerField()
    z = serializers.IntegerField()

class TopAnalyticsSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    x = serializers.CharField()
    y = serializers.IntegerField()
    z = serializers.IntegerField()

class PerformanceAnalyticsSerializer(serializers.Serializer):
    period = serializers.CharField()
    x = serializers.CharField()
    y = serializers.IntegerField()
    z = serializers.FloatField(allow_null=True)

class FilterSerializer(serializers.Serializer):
    field = serializers.CharField()
    operator = serializers.ChoiceField(choices=['eq', 'gt', 'lt', 'gte', 'lte', 'contains', 'icontains'])
    value = serializers.CharField()

class QueryParamsSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    filters = serializers.JSONField(required=False)
    logic = serializers.ChoiceField(choices=['and', 'or'], default='and')