from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sign-in/', views.sign_in, name='sign_in'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('logout/', views.user_logout, name='logout'),
    path('model-instruction/', views.model_instruction, name='model_instruction'),
    path('data-download/', views.data_download, name='data_download'),
    path('data-download-1.0/', views.data_download_1_0, name='data_download_1_0'),
    # path('data-download/', views.data_download, name='data_download_1.0'),
    path('data-download-original/', views.data_download_original, name='data_download_original'),
    path('data-download-single/', views.data_download_single, name='data_download_single'),
    path('data-echart/', views.data_echart, name='data_echart'),
    path('data-echart-fixed/', views.data_echart_fixed, name='data_echart_fixed'),
    path('data-echart-map/', views.data_echart_map, name='data_echart_map'),
    path('data-fetch-tool/', views.data_fetch_tool, name='data_fetch_tool'),
    path('data-local-map/', views.data_local_map, name='data_local_map'),
    path('user-status/', views.user_status, name='user_status'),
    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('verify-email-new/', views.verify_email_new, name='verify_email_new'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    
    # 管理员面板路由
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', views.admin_user_list, name='admin_user_list'),
    path('admin-user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
]
