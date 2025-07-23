from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import UserProfile, DataDownload
import json


def index(request):
    """主页视图"""
    return render(request, 'index.html')


def sign_in(request):
    """登录页面视图"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'sign_in.html')


def sign_up(request):
    """注册页面视图"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        organization = request.POST.get('organization')
        organization_type = request.POST.get('organization_type')
        country = request.POST.get('country')
        
        # 验证密码匹配
        if password != confirm_password:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'sign_up.html')
        
        # 验证必填字段
        if not all([email, password, organization, organization_type, country]):
            messages.error(request, '请填写所有必填字段')
            return render(request, 'sign_up.html')
        
        # 检查邮箱是否已存在
        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册')
            return render(request, 'sign_up.html')
        
        # 验证密码强度
        import re
        if len(password) < 6 or len(password) > 20:
            messages.error(request, '密码长度必须在6-20位之间')
            return render(request, 'sign_up.html')
        
        # 检查密码复杂度
        has_number = bool(re.search(r'\d', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password))
        
        conditions_met = sum([has_number, has_upper, has_lower, has_special])
        if conditions_met < 2:
            messages.error(request, '密码强度不足，至少包含数字、大写字母、小写字母和特殊字符中的两种')
            return render(request, 'sign_up.html')
        
        try:
            # 使用邮箱作为用户名
            username = email.split('@')[0]
            # 如果用户名已存在，添加数字后缀
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # 创建用户
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=password,
                first_name='',  # 可以后续完善
                last_name=''
            )
            
            # 创建用户配置文件
            profile = UserProfile.objects.create(
                user=user,
                organization=organization,
                organization_type=organization_type,
                country=country
            )
            
            # 根据邮箱类型设置不同的成功消息
            if profile.is_edu_email:
                messages.success(request, '注册成功！检测到教育邮箱，账户已自动审核通过，请登录')
            else:
                messages.success(request, '注册成功！非教育邮箱需要人工审核，请耐心等待审核结果')
            
            return redirect('sign_in')
            
        except Exception as e:
            messages.error(request, f'注册失败：{str(e)}')
    
    return render(request, 'sign_up.html')


def user_logout(request):
    """注销视图"""
    logout(request)
    return redirect('index')


def data_download(request):
    """数据下载页面视图"""
    return render(request, 'data_download.html')


def data_echart(request):
    """数据图表页面视图"""
    return render(request, 'data_echart.html')


def data_echart_fixed(request):
    """数据图表修复版页面视图"""
    return render(request, 'data_echart_fixed.html')


def data_fetch_tool(request):
    """数据获取工具页面视图"""
    return render(request, 'data_fetch_tool.html')


def data_local_map(request):
    """本地地图页面视图"""
    return render(request, 'data_local_map.html')


def user_status(request):
    """用户状态页面视图"""
    return render(request, 'user_status.html')


def verification_sent(request):
    """验证发送页面视图"""
    return render(request, 'verification_sent.html')


def verify_email(request):
    """邮箱验证页面视图"""
    return render(request, 'verify_email.html')


def verify_email_new(request):
    """新邮箱验证页面视图"""
    return render(request, 'verify_email_new.html')
