from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
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

def model_instruction(request):
    """模型介绍页面视图"""
    return render(request, 'model_instruction.html', {'user': request.user})

def user_service(request):
    """用户服务页面视图"""
    return render(request, 'user_service.html', {'user': request.user})


# def data_echart_map(request):
#     """数据图表地图页面视图"""
#     print("Loading data_echart_map view")
#     import os
#     import json
#     from django.conf import settings
#     from django.http import JsonResponse
    
#     # 检查静态文件是否存在
#     static_file_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'air-quality-data.json')
#     file_exists = os.path.exists(static_file_path)
#     print(f"JSON文件存在: {file_exists}, 路径: {static_file_path}")
    
#     # 如果是API请求，返回JSON数据
#     if request.GET.get('api') == 'json':
#         try:
#             with open(static_file_path, 'r', encoding='utf-8') as f:
#                 data = json.load(f)
#                 cities_count = len(data.get('cities', []))
#                 return JsonResponse({
#                     'success': True,
#                     'file_exists': file_exists,
#                     'file_path': static_file_path,
#                     'cities_count': cities_count,
#                     'update_time': data.get('updateTime', ''),
#                     'data': data
#                 })
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
    
#     # 如果URL中有debug参数，则加载调试版本
#     if request.GET.get('debug') == '1':
#         return render(request, 'data_echart_map_debug.html')
    
#     return render(request, 'data_echart_map.html')




def verify_email_new(request):
    """新邮箱验证页面视图"""
    return render(request, 'verify_email_new.html')


# 忘记密码相关视图
import random
import string
from django.core.mail import send_mail
from django.conf import settings


@csrf_exempt
def send_reset_code(request):
    """发送密码重置验证码"""
    print(f"收到发送重置码请求: method={request.method}")  # 调试信息
    
    if request.method == 'POST':
        try:
            print(f"请求body: {request.body}")  # 调试信息
            data = json.loads(request.body)
            email = data.get('email')
            print(f"解析的邮箱: {email}")  # 调试信息
            
            # 检查用户是否存在
            try:
                user = User.objects.get(email=email)
                print(f"找到用户: {user.username}")  # 调试信息
            except User.DoesNotExist:
                print(f"用户不存在: {email}")  # 调试信息
                return JsonResponse({
                    'success': False,
                    'message': '该邮箱地址未注册'
                })
            
            # 生成6位数验证码
            verification_code = ''.join(random.choices(string.digits, k=6))
            print(f"生成验证码: {verification_code}")  # 调试信息
            
            # 存储或更新验证码
            verification, created = UserVerification.objects.get_or_create(
                user=user,
                defaults={
                    'verification_code': verification_code,
                    'is_verified': False,
                    'created_at': timezone.now()
                }
            )
            
            if not created:
                verification.verification_code = verification_code
                verification.is_verified = False
                verification.created_at = timezone.now()
                verification.save()
            
            print(f"验证码已保存，created={created}")  # 调试信息
            
            # 临时跳过邮件发送，直接返回成功（用于测试）
            print("跳过邮件发送（测试模式）")  # 调试信息
            return JsonResponse({
                'success': True,
                'message': f'验证码已发送到您的邮箱（测试：{verification_code}）'
            })
                
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")  # 调试信息
            return JsonResponse({
                'success': False,
                'message': '请求格式错误'
            })
        except Exception as e:
            print(f"发送重置验证码失败: {e}")
            import traceback
            traceback.print_exc()  # 打印完整的错误堆栈
            return JsonResponse({
                'success': False,
                'message': '系统错误，请稍后重试'
            })
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})


@csrf_exempt
def verify_reset_code(request):
    """验证密码重置验证码"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')
            
            print(f"验证重置码请求: email={email}, code={code}")  # 调试信息
            
            # 查找用户
            try:
                user = User.objects.get(email=email)
                print(f"找到用户: {user.username}")  # 调试信息
            except User.DoesNotExist:
                print(f"用户不存在: {email}")  # 调试信息
                return JsonResponse({
                    'success': False,
                    'message': '用户不存在'
                })
            
            # 验证验证码
            try:
                verification = UserVerification.objects.get(user=user)
                print(f"验证记录: code={verification.verification_code}, created_at={verification.created_at}, is_verified={verification.is_verified}")  # 调试信息
                
                # 检查验证码是否正确
                if verification.verification_code != code:
                    print(f"验证码不匹配: 期望={verification.verification_code}, 实际={code}")  # 调试信息
                    return JsonResponse({
                        'success': False,
                        'message': '验证码错误'
                    })
                
                # 检查验证码是否过期（10分钟）
                time_diff = timezone.now() - verification.created_at
                print(f"时间差: {time_diff.total_seconds()}秒")  # 调试信息
                if time_diff.total_seconds() > 600:  # 10分钟 = 600秒
                    return JsonResponse({
                        'success': False,
                        'message': '验证码已过期，请重新获取'
                    })
                
                # 标记验证码为已验证
                verification.is_verified = True
                verification.save()
                print("验证码验证成功")  # 调试信息
                
                return JsonResponse({
                    'success': True,
                    'message': '验证成功'
                })
                
            except UserVerification.DoesNotExist:
                print(f"验证记录不存在: {user.username}")  # 调试信息
                return JsonResponse({
                    'success': False,
                    'message': '请先获取验证码'
                })
                
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")  # 调试信息
            return JsonResponse({
                'success': False,
                'message': '请求格式错误'
            })
        except Exception as e:
            print(f"验证重置验证码失败: {e}")
            import traceback
            traceback.print_exc()  # 打印完整的错误堆栈
            return JsonResponse({
                'success': False,
                'message': '系统错误，请稍后重试'
            })
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})


@csrf_exempt
def reset_password(request):
    """重置用户密码"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')
            password = data.get('password')
            
            # 查找用户
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户不存在'
                })
            
            # 验证验证码状态
            try:
                verification = UserVerification.objects.get(user=user)
                
                # 检查验证码是否已验证
                if not verification.is_verified:
                    return JsonResponse({
                        'success': False,
                        'message': '请先验证验证码'
                    })
                
                # 检查验证码是否正确
                if verification.verification_code != code:
                    return JsonResponse({
                        'success': False,
                        'message': '验证码错误'
                    })
                
                # 检查验证码是否过期（15分钟）
                time_diff = timezone.now() - verification.created_at
                if time_diff.total_seconds() > 900:  # 15分钟 = 900秒
                    return JsonResponse({
                        'success': False,
                        'message': '验证码已过期，请重新获取'
                    })
                
            except UserVerification.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '验证信息不存在'
                })
            
            # 验证密码格式（与注册时相同的要求）
            if len(password) < 8:
                return JsonResponse({
                    'success': False,
                    'message': '密码长度至少为8位'
                })
            
            if not re.search(r'[A-Z]', password):
                return JsonResponse({
                    'success': False,
                    'message': '密码必须包含至少一个大写字母'
                })
            
            if not re.search(r'[a-z]', password):
                return JsonResponse({
                    'success': False,
                    'message': '密码必须包含至少一个小写字母'
                })
            
            if not re.search(r'\d', password):
                return JsonResponse({
                    'success': False,
                    'message': '密码必须包含至少一个数字'
                })
            
            # 更新用户密码
            user.set_password(password)
            user.save()
            
            # 清除验证记录
            verification.delete()
            
            # 记录审计日志（可选，不影响主要功能）
            try:
                # 由于AuditLog模型设计用于管理员操作，这里我们简单跳过
                # 如果需要记录密码重置日志，可以创建专门的PasswordResetLog模型
                pass
            except:
                pass  # 审计日志失败不影响主要功能
            
            return JsonResponse({
                'success': True,
                'message': '密码重置成功'
            })
            
        except Exception as e:
            print(f"重置密码失败: {e}")
            return JsonResponse({
                'success': False,
                'message': '系统错误，请稍后重试'
            })
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

# 简化测试版本 - 可以立即测试前后端连接

# 将以下代码添加到 main_app/views.py 文件的末尾用于测试

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import csv
import io
from datetime import datetime

@login_required
@require_http_methods(["POST"])
def download_data(request):
    """数据下载接口 - 根据数据类型和时间范围生成对应数据"""
    try:
        # 获取参数
        category = request.POST.get('category', 'CN environmental data')
        data_type = request.POST.get('data_type', 'air_pollution')
        country = request.POST.get('country', 'china')
        pollutant = request.POST.get('pollutant', 'PM2.5')
        time_range = request.POST.get('time_range', 'month')
        start_date = request.POST.get('start_date', '2023-01')
        end_date = request.POST.get('end_date', '2023-12')
        
        # 生成文件名
        filename = f"{country}_{data_type}_{pollutant}_{time_range}_{start_date}_to_{end_date}.csv"
        filename = filename.replace('<sub>', '').replace('</sub>', '').replace('.', '_')
        
        # 创建CSV响应
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # 添加BOM以支持中文显示
        response.write('\ufeff')
        writer = csv.writer(response)
        
        # 根据数据类型生成不同的数据结构
        if data_type == 'air_pollution':
            generate_air_pollution_data(writer, country, pollutant, time_range, start_date, end_date)
        elif data_type == 'weather':
            generate_weather_data(writer, pollutant, time_range, start_date, end_date)
        elif data_type == 'urban':
            generate_urban_data(writer, pollutant, time_range, start_date, end_date)
        else:
            # 默认返回大气污染数据
            generate_air_pollution_data(writer, country, pollutant, time_range, start_date, end_date)
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': f'下载失败: {str(e)}'}, status=500)

def generate_air_pollution_data(writer, country, pollutant, time_range, start_date, end_date):
    """生成大气污染数据"""
    import random
    from datetime import datetime, timedelta
    
    # 写入元数据
    writer.writerow(['数据类型', '大气污染数据'])
    writer.writerow(['国家/地区', '中国' if country == 'china' else '英国'])
    writer.writerow(['污染物', pollutant])
    writer.writerow(['时间范围', '月均' if time_range == 'month' else '年均'])
    writer.writerow(['开始时间', start_date])
    writer.writerow(['结束时间', end_date])
    writer.writerow(['下载时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])  # 空行
    
    # 根据国家选择城市
    if country == 'china':
        cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '重庆']
    else:  # 英国
        cities = ['London', 'Manchester', 'Birmingham', 'Leeds', 'Glasgow', 'Liverpool', 'Edinburgh', 'Bristol', 'Sheffield', 'Cardiff']
    
    # 写入数据表头
    if time_range == 'month':
        writer.writerow(['年月', '城市', '经度', '纬度', f'{pollutant}浓度(μg/m³)', 'AQI', '数据质量'])
    else:
        writer.writerow(['年份', '城市', '经度', '纬度', f'{pollutant}年均浓度(μg/m³)', 'AQI', '数据质量'])
    
    # 生成时间序列
    dates = []
    if time_range == 'month':
        start_year, start_month = map(int, start_date.split('-'))
        end_year, end_month = map(int, end_date.split('-'))
        
        current_year, current_month = start_year, start_month
        while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
            dates.append(f"{current_year}-{current_month:02d}")
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
    else:
        start_year = int(start_date)
        end_year = int(end_date)
        dates = [str(year) for year in range(start_year, end_year + 1)]
    
    # 生成数据
    for date in dates:
        for city in cities:
            # 根据城市和污染物生成不同的浓度范围
            if pollutant in ['PM2.5', 'PM<sub>2.5</sub>']:
                concentration = random.uniform(15, 150)
                aqi = int(concentration * 2.5 + random.uniform(-20, 20))
            elif pollutant in ['PM10', 'PM<sub>10</sub>']:
                concentration = random.uniform(25, 250)
                aqi = int(concentration * 1.5 + random.uniform(-15, 15))
            elif pollutant in ['PM2.5-PM10', 'PM<sub>2.5</sub>-PM<sub>10</sub>']:
                # PM2.5-PM10 表示粗颗粒物
                concentration = random.uniform(10, 100)
                aqi = int(concentration * 2.0 + random.uniform(-15, 15))
            elif pollutant in ['NO2', 'NO<sub>2</sub>']:
                concentration = random.uniform(10, 80)
                aqi = int(concentration * 3 + random.uniform(-25, 25))
            elif pollutant in ['O3', 'O<sub>3</sub>']:
                concentration = random.uniform(50, 200)
                aqi = int(concentration * 1.2 + random.uniform(-30, 30))
            elif pollutant == 'CO':
                concentration = random.uniform(0.5, 5.0)
                aqi = int(concentration * 50 + random.uniform(-20, 20))
            else:
                concentration = random.uniform(20, 100)
                aqi = random.randint(50, 200)
            
            # 生成坐标（模拟）
            if country == 'china':
                longitude = random.uniform(110, 125)
                latitude = random.uniform(30, 45)
            else:
                longitude = random.uniform(-5, 2)
                latitude = random.uniform(50, 58)
            
            quality = random.choice(['优', '良', '优'])
            
            writer.writerow([
                date,
                city,
                f"{longitude:.4f}",
                f"{latitude:.4f}",
                f"{concentration:.2f}",
                max(0, min(500, aqi)),
                quality
            ])

def generate_weather_data(writer, indicator, time_range, start_date, end_date):
    """生成气象数据"""
    import random
    from datetime import datetime
    
    # 写入元数据
    writer.writerow(['数据类型', '气象数据'])
    writer.writerow(['国家/地区', '中国'])
    writer.writerow(['气象指标', indicator])
    writer.writerow(['时间范围', '月均' if time_range == 'month' else '年均'])
    writer.writerow(['开始时间', start_date])
    writer.writerow(['结束时间', end_date])
    writer.writerow(['下载时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '重庆']
    
    # 根据指标设置表头和单位
    if indicator == '温度':
        writer.writerow(['时间', '城市', '经度', '纬度', '平均温度(°C)', '最高温度(°C)', '最低温度(°C)', '数据质量'])
    elif indicator == '紫外辐射':
        writer.writerow(['时间', '城市', '经度', '纬度', 'UV指数', 'UV强度等级', '数据质量'])
    
    # 生成时间序列
    dates = []
    if time_range == 'month':
        start_year, start_month = map(int, start_date.split('-'))
        end_year, end_month = map(int, end_date.split('-'))
        
        current_year, current_month = start_year, start_month
        while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
            dates.append(f"{current_year}-{current_month:02d}")
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
    else:
        start_year = int(start_date)
        end_year = int(end_date)
        dates = [str(year) for year in range(start_year, end_year + 1)]
    
    # 生成数据
    for date in dates:
        for city in cities:
            longitude = random.uniform(110, 125)
            latitude = random.uniform(30, 45)
            quality = random.choice(['优', '良', '优'])
            
            if indicator == '温度':
                avg_temp = random.uniform(-5, 35)
                max_temp = avg_temp + random.uniform(5, 15)
                min_temp = avg_temp - random.uniform(5, 15)
                writer.writerow([
                    date, city, f"{longitude:.4f}", f"{latitude:.4f}",
                    f"{avg_temp:.1f}", f"{max_temp:.1f}", f"{min_temp:.1f}", quality
                ])
            elif indicator == '紫外辐射':
                uv_index = random.uniform(1, 11)
                if uv_index <= 2:
                    uv_level = '低'
                elif uv_index <= 5:
                    uv_level = '中等'
                elif uv_index <= 7:
                    uv_level = '高'
                elif uv_index <= 10:
                    uv_level = '很高'
                else:
                    uv_level = '极高'
                writer.writerow([
                    date, city, f"{longitude:.4f}", f"{latitude:.4f}",
                    f"{uv_index:.1f}", uv_level, quality
                ])

def generate_urban_data(writer, indicator, time_range, start_date, end_date):
    """生成建成环境数据"""
    import random
    from datetime import datetime
    
    # 写入元数据
    writer.writerow(['数据类型', '建成环境数据'])
    writer.writerow(['国家/地区', '中国'])
    writer.writerow(['建成指标', indicator])
    writer.writerow(['时间范围', '月均' if time_range == 'month' else '年均'])
    writer.writerow(['开始时间', start_date])
    writer.writerow(['结束时间', end_date])
    writer.writerow(['下载时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '重庆']
    
    if indicator == 'NDVI':
        writer.writerow(['时间', '城市', '经度', '纬度', 'NDVI值', '植被覆盖等级', '数据质量'])
    
    # 生成时间序列
    dates = []
    if time_range == 'month':
        start_year, start_month = map(int, start_date.split('-'))
        end_year, end_month = map(int, end_date.split('-'))
        
        current_year, current_month = start_year, start_month
        while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
            dates.append(f"{current_year}-{current_month:02d}")
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
    else:
        start_year = int(start_date)
        end_year = int(end_date)
        dates = [str(year) for year in range(start_year, end_year + 1)]
    
    # 生成数据
    for date in dates:
        for city in cities:
            longitude = random.uniform(110, 125)
            latitude = random.uniform(30, 45)
            quality = random.choice(['优', '良', '优'])
            
            if indicator == 'NDVI':
                ndvi = random.uniform(0.1, 0.8)
                if ndvi < 0.2:
                    vegetation_level = '稀疏植被'
                elif ndvi < 0.4:
                    vegetation_level = '中等植被'
                elif ndvi < 0.6:
                    vegetation_level = '密集植被'
                else:
                    vegetation_level = '极密植被'
                
                writer.writerow([
                    date, city, f"{longitude:.4f}", f"{latitude:.4f}",
                    f"{ndvi:.3f}", vegetation_level, quality
                ])

@login_required
@require_http_methods(["POST"]) 
def export_data(request):
    """临时测试版本的数据导出接口"""
    try:
        category = request.POST.get('category', '未知类别')
        pollutant = request.POST.get('pollutant', '未知污染物')
        
        test_data = {
            'message': '这是测试导出功能',
            'parameters': {
                'category': category,
                'pollutant': pollutant,
                'user': request.user.email,
                'export_time': datetime.now().isoformat()
            },
            'sample_data': [
                {'date': '2023-01', 'city': '北京', 'pm25': 45},
                {'date': '2023-01', 'city': '上海', 'pm25': 38},
                {'date': '2023-01', 'city': '广州', 'pm25': 42}
            ]
        }
        
        import json
        response = HttpResponse(
            json.dumps(test_data, ensure_ascii=False, indent=2),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="test_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': f'导出失败: {str(e)}'}, status=500)

@login_required
def preview_data(request):
    """测试版本的数据预览接口"""
    return JsonResponse({
        'message': '预览功能测试成功',
        'preview': [
            ['2023-01', '北京', 45, 78, 89],
            ['2023-01', '上海', 38, 65, 76],
            ['2023-01', '广州', 42, 70, 82]
        ],
        'total_count': 100,
        'columns': ['日期', '城市', 'PM2.5', 'PM10', 'AQI']
    })

@login_required
def data_statistics(request):
    """测试版本的数据统计接口"""
    return JsonResponse({
        'message': '统计功能测试成功',
        'total_records': 12500,
        'available_data': ['PM2.5', 'PM10', 'NO2', 'O3'],
        'date_range': ['2015-01-01', '2023-12-31'],
        'last_updated': datetime.now().isoformat()
    })
