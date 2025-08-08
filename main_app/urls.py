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
    path('send-reset-code/', views.send_reset_code, name='send_reset_code'),
    path('verify-reset-code/', views.verify_reset_code, name='verify_reset_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # 管理员面板路由
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', views.admin_user_list, name='admin_user_list'),
    path('admin-user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    
    # 数据下载相关接口
    path('api/download-data/', views.download_data, name='download_data'),
    path('api/export-data/', views.export_data, name='export_data'),
    path('api/preview-data/', views.preview_data, name='preview_data'),
    path('api/data-statistics/', views.data_statistics, name='data_statistics'),
]
