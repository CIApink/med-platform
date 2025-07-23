from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sign-in/', views.sign_in, name='sign_in'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('logout/', views.user_logout, name='logout'),
    path('data-download/', views.data_download, name='data_download'),
    path('data-echart/', views.data_echart, name='data_echart'),
    path('data-echart-fixed/', views.data_echart_fixed, name='data_echart_fixed'),
    path('data-fetch-tool/', views.data_fetch_tool, name='data_fetch_tool'),
    path('data-local-map/', views.data_local_map, name='data_local_map'),
    path('user-status/', views.user_status, name='user_status'),
    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('verify-email-new/', views.verify_email_new, name='verify_email_new'),
]
