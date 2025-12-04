from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, F, Q
from datetime import datetime
from analytics.utils import AnalyticsCalculator, AnalyticsQueryBuilder
from .models import Blog, BlogView
from .serializers import (
    BlogViewAnalyticsSerializer,
    TopAnalyticsSerializer,
    PerformanceAnalyticsSerializer
)


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return "invalid"


def get_queryset_with_filters(model_cls, filters_json, logic, start_date=None, end_date=None, date_field="created_at"):
    q = AnalyticsQueryBuilder.build_filters(filters_json, logic)
    qs = model_cls.objects.filter(q)
    return AnalyticsQueryBuilder.apply_date_range(qs, start_date, end_date, date_field)


class BlogViewsAnalyticsAPI(APIView):
    """/analytics/blog-views/"""
    def get(self, request):
        object_type = request.GET.get("object_type", "country")
        range_type = request.GET.get("range", "month")
        start_date = parse_date(request.GET.get("start_date"))
        end_date = parse_date(request.GET.get("end_date"))
        filters_json = request.GET.get("filters")
        logic = request.GET.get("logic", "and")

        if object_type not in ["country", "user"]:
            return Response({"error": 'object_type must be "country" or "user"'}, status=status.HTTP_400_BAD_REQUEST)
        if range_type not in ["day", "week", "month", "year"]:
            return Response({"error": "range must be one of: day, week, month, year"}, status=status.HTTP_400_BAD_REQUEST)
        if start_date == "invalid" or end_date == "invalid":
            return Response({"error": "Dates must be in YYYY-MM-DD format"}, status=status.HTTP_400_BAD_REQUEST)

        blog_views = get_queryset_with_filters(BlogView, filters_json, logic, start_date, end_date)

        trunc_func = AnalyticsQueryBuilder.get_time_trunc_func(range_type)
        group_key = F("viewer_country") if object_type == "country" else F("viewer__username")

        data = (
            blog_views.annotate(period=trunc_func("viewed_at"), grouping_key=group_key)
            .values("period", "grouping_key")
            .annotate(number_of_blogs=Count("blog", distinct=True), total_views=Count("id"))
            .order_by("period", "grouping_key")
        )

        result = [
            {
                "x": f"{item['grouping_key'] or 'Unknown'} - {item['period'].strftime('%Y-%m-%d') if item['period'] else 'Unknown'}",
                "y": item["number_of_blogs"],
                "z": item["total_views"],
            }
            for item in data
        ]

        return Response(BlogViewAnalyticsSerializer(result, many=True).data)


class TopAnalyticsAPI(APIView):
    """/analytics/top/"""
    def get(self, request):
        top_type = request.GET.get("top", "blog")
        start_date = parse_date(request.GET.get("start_date"))
        end_date = parse_date(request.GET.get("end_date"))
        filters_json = request.GET.get("filters")
        logic = request.GET.get("logic", "and")

        if top_type not in ["user", "country", "blog"]:
            return Response({"error": 'top must be one of: "user", "country", "blog"'}, status=status.HTTP_400_BAD_REQUEST)
        if start_date == "invalid" or end_date == "invalid":
            return Response({"error": "Dates must be in YYYY-MM-DD format"}, status=status.HTTP_400_BAD_REQUEST)

        blog_views = get_queryset_with_filters(BlogView, filters_json, logic, start_date, end_date)

        result = []

        if top_type == "blog":
            data = (
                blog_views.values("blog__id", "blog__title", "blog__author__username")
                .annotate(blog_title=F("blog__title"), author_name=F("blog__author__username"),
                          total_views=Count("id"), unique_viewers=Count("viewer", distinct=True))
                .order_by("-total_views")[:10]
            )
            result = [{"rank": i+1, "x": d["blog_title"] or f"Blog {d['blog__id']}", "y": d["total_views"], "z": d["unique_viewers"]}
                      for i, d in enumerate(data)]

        elif top_type == "user":
            data = (
                blog_views.filter(viewer__isnull=False)
                .values("viewer__username")
                .annotate(username=F("viewer__username"),
                          blogs_viewed=Count("blog", distinct=True),
                          total_views=Count("id"))
                .order_by("-total_views")[:10]
            )
            result = [{"rank": i+1, "x": d["username"] or "Anonymous", "y": d["total_views"], "z": d["blogs_viewed"]}
                      for i, d in enumerate(data)]

        else:  # country
            data = (
                blog_views.exclude(viewer_country__isnull=True)
                .values("viewer_country")
                .annotate(country=F("viewer_country"), total_views=Count("id"), unique_users=Count("viewer", distinct=True))
                .order_by("-total_views")[:10]
            )
            result = [{"rank": i+1, "x": d["country"] or "Unknown", "y": d["total_views"], "z": d["unique_users"]}
                      for i, d in enumerate(data)]

        return Response(TopAnalyticsSerializer(result, many=True).data)


class PerformanceAnalyticsAPI(APIView):
    """/analytics/performance/"""
    def get(self, request):
        compare_type = request.GET.get("compare", "month")
        user_id = request.GET.get("user_id")
        start_date = parse_date(request.GET.get("start_date"))
        end_date = parse_date(request.GET.get("end_date"))
        filters_json = request.GET.get("filters")
        logic = request.GET.get("logic", "and")

        if compare_type not in ["day", "week", "month", "year"]:
            return Response({"error": 'compare must be one of: "day", "week", "month", "year"'}, status=status.HTTP_400_BAD_REQUEST)
        if start_date == "invalid" or end_date == "invalid":
            return Response({"error": "Dates must be in YYYY-MM-DD format"}, status=status.HTTP_400_BAD_REQUEST)

        blogs = get_queryset_with_filters(Blog, filters_json, logic, start_date, end_date, date_field="created_at")
        if user_id:
            blogs = blogs.filter(author_id=user_id)

        trunc_func = AnalyticsQueryBuilder.get_time_trunc_func(compare_type)

        blog_agg = blogs.annotate(period=trunc_func("created_at")).values("period").annotate(blogs_created=Count("id")).order_by("period")
        blog_ids = blogs.values_list("id", flat=True)

        blog_views = get_queryset_with_filters(BlogView, filters_json, logic, start_date, end_date)
        blog_views = blog_views.filter(blog_id__in=blog_ids)
        views_agg = blog_views.annotate(period=trunc_func("viewed_at")).values("period").annotate(total_views=Count("id")).order_by("period")

        blog_data = {b["period"]: b["blogs_created"] for b in blog_agg if b["period"]}
        views_data = {v["period"]: v["total_views"] for v in views_agg if v["period"]}

        all_periods = sorted(set(blog_data.keys()) | set(views_data.keys()))
        result = []
        prev_views = 0

        for i, period in enumerate(all_periods):
            blogs_in_period = blog_data.get(period, 0)
            views_in_period = views_data.get(period, 0)
            growth = None if i == 0 else AnalyticsCalculator.calculate_growth(views_in_period, prev_views)
            period_str = period.strftime("%Y-%m-%d") if period else "Unknown"

            result.append({"period": period_str, "x": f"{period_str} - {blogs_in_period} blogs", "y": views_in_period, "z": growth})
            prev_views = views_in_period

        return Response(PerformanceAnalyticsSerializer(result, many=True).data)
