from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import UserProfile, UserVerification, AuditLog
from .utils import send_verification_email, verify_email_code
import json
import re
import uuid


def index(request):
    """主页视图"""
    return render(request, 'index.html', {'user': request.user})


def sign_in(request):
    """登录页面视图"""
    if request.method == 'POST':
        email = request.POST.get('email')  # 改为email
        password = request.POST.get('password')
        
        # 尝试通过邮箱查找用户
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            username = email  # 如果没找到，也许用户输入的是用户名
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # 检查用户是否已通过审核
            try:
                profile = user.userprofile
                if profile.status == 'approved':
                    login(request, user)
                    # 始终重定向到首页
                    return redirect('index')
                elif profile.status == 'pending':
                    messages.warning(request, '您的账户正在审核中，请稍后再试')
                elif profile.status == 'rejected':
                    messages.error(request, f'您的账户申请被拒绝。原因：{profile.rejection_reason or "未提供原因"}')
                elif profile.status == 'suspended':
                    messages.error(request, '您的账户已被暂停，请联系管理员')
            except UserProfile.DoesNotExist:
                login(request, user)
                # 始终重定向到首页
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
            # 使用邮箱作为用户名的基础
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
            
            # 发送验证邮件
            send_verification_email(user)
            
            # 根据邮箱类型设置不同的成功消息
            if profile.is_edu_email:
                messages.success(request, '注册成功！检测到教育邮箱，账户已自动审核通过，请前往邮箱验证您的邮箱地址')
            else:
                messages.success(request, '注册成功！非教育邮箱需要人工审核，请前往邮箱验证您的邮箱地址并耐心等待审核结果')
            
            return redirect('verification_sent')
            
        except Exception as e:
            messages.error(request, f'注册失败：{str(e)}')
    
    return render(request, 'sign_up.html')


def user_logout(request):
    """注销视图"""
    logout(request)
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    # 否则重定向到首页
    return redirect('index')


def verification_sent(request):
    """验证发送页面视图"""
    return render(request, 'verification_sent.html')


def verify_email(request):
    """邮箱验证页面视图"""
    code = request.GET.get('code')
    
    if not code:
        messages.error(request, '无效的验证链接')
        return redirect('index')
    
    user = verify_email_code(code)
    
    if user:
        # 如果用户未登录，则登录该用户
        if not request.user.is_authenticated:
            login(request, user)
        
        messages.success(request, '邮箱验证成功！')
        
        # 检查用户状态
        try:
            profile = user.userprofile
            if profile.status == 'approved':
                return redirect('index')
            else:
                return render(request, 'verify_email.html', {'verified': True, 'status': profile.status})
        except UserProfile.DoesNotExist:
            return redirect('index')
    else:
        messages.error(request, '验证链接无效或已过期，请重新获取验证链接')
        return render(request, 'verify_email.html', {'verified': False})


def resend_verification(request):
    """重新发送验证邮件"""
    if not request.user.is_authenticated:
        return HttpResponseForbidden("请先登录")
    
    success = send_verification_email(request.user)
    
    if success:
        messages.success(request, '验证邮件已发送，请查收')
        return redirect('verification_sent')
    else:
        messages.error(request, '发送验证邮件失败，请稍后再试')
        return redirect('index')


@login_required
def user_status(request):
    """返回用户状态的JSON视图"""
    data = {
        'is_authenticated': request.user.is_authenticated,
    }
    
    if request.user.is_authenticated:
        data['username'] = request.user.username
        data['email'] = request.user.email
        try:
            profile = request.user.userprofile
            data['status'] = profile.status
            data['is_approved'] = profile.is_approved
            data['organization'] = profile.organization
        except UserProfile.DoesNotExist:
            pass
    
    return JsonResponse(data)


# 以下是管理员相关视图函数

def is_admin(user):
    """检查用户是否是管理员"""
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin)
def admin_dashboard(request):
    """管理员仪表盘"""
    # 统计信息
    pending_count = UserProfile.objects.filter(status='pending').count()
    approved_count = UserProfile.objects.filter(status='approved').count()
    rejected_count = UserProfile.objects.filter(status='rejected').count()
    suspended_count = UserProfile.objects.filter(status='suspended').count()
    
    # 最近注册的用户
    recent_users = UserProfile.objects.all().order_by('-created_at')[:10]
    
    # 最近的审核日志
    recent_logs = AuditLog.objects.all()[:10]
    
    context = {
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'suspended_count': suspended_count,
        'recent_users': recent_users,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'admin/dashboard.html', context)


@user_passes_test(is_admin)
def admin_user_list(request):
    """管理员用户列表"""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('query', '')
    
    users = UserProfile.objects.all()
    
    # 筛选状态
    if status_filter:
        users = users.filter(status=status_filter)
    
    # 搜索
    if search_query:
        users = users.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(organization__icontains=search_query)
        )
    
    # 分页
    paginator = Paginator(users.order_by('-created_at'), 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin/user_list.html', context)


@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """管理员用户详情"""
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            user_profile.status = 'approved'
            user_profile.is_approved = True
            user_profile.save()
            
            AuditLog.objects.create(
                user_profile=user_profile,
                admin_user=request.user,
                action='approve',
                notes=notes
            )
            
            messages.success(request, f'已批准用户 {user_profile.user.username}')
            
        elif action == 'reject':
            rejection_reason = request.POST.get('rejection_reason', '')
            user_profile.status = 'rejected'
            user_profile.is_approved = False
            user_profile.rejection_reason = rejection_reason
            user_profile.save()
            
            AuditLog.objects.create(
                user_profile=user_profile,
                admin_user=request.user,
                action='reject',
                notes=f"拒绝原因: {rejection_reason}\n备注: {notes}"
            )
            
            messages.success(request, f'已拒绝用户 {user_profile.user.username}')
            
        elif action == 'suspend':
            user_profile.status = 'suspended'
            user_profile.is_approved = False
            user_profile.save()
            
            AuditLog.objects.create(
                user_profile=user_profile,
                admin_user=request.user,
                action='suspend',
                notes=notes
            )
            
            messages.success(request, f'已暂停用户 {user_profile.user.username}')
            
        elif action == 'reactivate':
            user_profile.status = 'approved'
            user_profile.is_approved = True
            user_profile.save()
            
            AuditLog.objects.create(
                user_profile=user_profile,
                admin_user=request.user,
                action='reactivate',
                notes=notes
            )
            
            messages.success(request, f'已重新激活用户 {user_profile.user.username}')
            
        elif action == 'update_notes':
            user_profile.admin_notes = notes
            user_profile.save()
            
            AuditLog.objects.create(
                user_profile=user_profile,
                admin_user=request.user,
                action='other',
                notes=f"更新备注: {notes}"
            )
            
            messages.success(request, f'已更新用户 {user_profile.user.username} 的备注')
    
    # 查询用户审核日志
    audit_logs = AuditLog.objects.filter(user_profile=user_profile).order_by('-created_at')
    
    context = {
        'user_profile': user_profile,
        'audit_logs': audit_logs,
    }
    
    return render(request, 'admin/user_detail.html', context)


def data_download(request):
    """数据下载页面视图"""
    return render(request, 'data_download_1.0.html', {'user': request.user})

def data_download_1_0(request):
    """数据下载页面视图（1.0版本）"""
    return render(request, 'data_download_1.0.html', {'user': request.user})

def data_download_single(request):
    return render(request, 'data_download-single.html')

def data_download_original(request):
    """数据下载页面视图（原版样式）"""
    return render(request, 'data_download_original.html', {'user': request.user})


def data_echart(request):
    """数据图表页面视图"""
    return render(request, 'data_echart.html')


def data_echart_fixed(request):
    """数据图表修复版页面视图"""
    return render(request, 'data_echart_fixed.html')


def data_echart_map(request):
    """数据图表地图页面视图"""
    print("Loading data_echart_map view")
    import os
    import json
    from django.conf import settings
    from django.http import JsonResponse
    
    # 检查静态文件是否存在
    static_file_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'air-quality-data.json')
    file_exists = os.path.exists(static_file_path)
    print(f"JSON文件存在: {file_exists}, 路径: {static_file_path}")
    
    # 如果是API请求，返回JSON数据
    if request.GET.get('api') == 'json':
        try:
            with open(static_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cities_count = len(data.get('cities', []))
                return JsonResponse({
                    'success': True,
                    'file_exists': file_exists,
                    'file_path': static_file_path,
                    'cities_count': cities_count,
                    'update_time': data.get('updateTime', ''),
                    'data': data
                })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # 如果URL中有debug参数，则加载调试版本
    if request.GET.get('debug') == '1':
        return render(request, 'data_echart_map_debug.html')
    
    return render(request, 'data_echart_map.html')


def data_fetch_tool(request):
    """数据获取工具页面视图"""
    return render(request, 'data_fetch_tool.html')


def data_local_map(request):
    """本地地图页面视图"""
    return render(request, 'data_local_map.html')


def verify_email_new(request):
    """新邮箱验证页面视图"""
    return render(request, 'verify_email_new.html')
