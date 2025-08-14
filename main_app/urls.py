from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sign-in/', views.sign_in, name='sign_in'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('logout/', views.user_logout, name='logout'),
    path('model-instruction/', views.model_instruction, name='model_instruction'),
    path('user-service/', views.user_service, name='user_service'),
    path('data-download/', views.data_download, name='data_download'),
    path('user-status/', views.user_status, name='user_status'),
    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('verify-email-new/', views.verify_email_new, name='verify_email_new'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    
    # 忘记密码功能路由
    path('verify-user-info/', views.verify_user_info, name='verify_user_info'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # 管理员面板路由
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', views.admin_user_list, name='admin_user_list'),
    path('admin-user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    
    # 数据下载API - 模拟腾讯云流程
    path('api/available-data/', views.get_available_data, name='get_available_data'),
    path('api/request-download/', views.request_data_download, name='request_data_download'),
    path('api/download-file/<str:task_id>/', views.download_file, name='download_file'),
]
