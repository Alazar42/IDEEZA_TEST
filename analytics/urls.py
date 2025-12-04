from django.urls import path
from . import views

urlpatterns = [
    path('blog-views/', views.BlogViewsAnalyticsAPI.as_view(), name='blog-views-analytics'),
    path('top/', views.TopAnalyticsAPI.as_view(), name='top-analytics'),
    path('performance/', views.PerformanceAnalyticsAPI.as_view(), name='performance-analytics'),
]