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
from django.urls import reverse
from .models import UserProfile, UserVerification, AuditLog
from .utils import send_verification_email, verify_email_code
import json
import re
import uuid


def index(request):
    return render(request, 'index.html', {'user': request.user})


def sign_in(request):
    status = request.GET.get('status')
    if status == 'approved':
        messages.success(request, '注册成功！检测到教育邮箱，账户已自动通过审核，您现在可以登录使用平台')
    elif status == 'pending':
        messages.info(request, '注册成功！您的账户申请已提交，需要人工审核，审核通过后您将收到邮件通知')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            username = email
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                profile = user.userprofile
                if profile.status == 'approved':
                    login(request, user)
                    next_url = request.POST.get('next') or request.GET.get('next') or 'index'
                    return redirect(next_url)
                elif profile.status == 'pending':
                    messages.warning(request, '您的账户正在审核中，请稍后再试')
                elif profile.status == 'rejected':
                    messages.error(request, f'您的账户申请被拒绝。原因：{profile.rejection_reason or "未提供原因"}')
                elif profile.status == 'suspended':
                    messages.error(request, '您的账户已被暂停，请联系管理员')
            except UserProfile.DoesNotExist:
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next') or 'index'
                return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
            
    return render(request, 'sign_in.html')


def sign_up(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        organization = request.POST.get('organization')
        organization_type = request.POST.get('organization_type')
        country = request.POST.get('country')
        
        if password != confirm_password:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'sign_up.html')
        
        if not all([email, password, first_name, last_name, organization, organization_type, country]):
            messages.error(request, '请填写所有必填字段')
            return render(request, 'sign_up.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册')
            return render(request, 'sign_up.html')
        
        if len(password) < 6 or len(password) > 20:
            messages.error(request, '密码长度必须在6-20位之间')
            return render(request, 'sign_up.html')
        
        has_number = bool(re.search(r'\d', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password))
        
        conditions_met = sum([has_number, has_upper, has_lower, has_special])
        if conditions_met < 2:
            messages.error(request, '密码强度不足，至少包含数字、大写字母、小写字母和特殊字符中的两种')
            return render(request, 'sign_up.html')
        
        try:
            username = email.split('@')[0]
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username, 
                email=email, 
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            is_edu_email = email.lower().endswith('.edu.cn')
            
            profile = UserProfile.objects.create(
                user=user,
                organization=organization,
                organization_type=organization_type,
                country=country,
                status='approved' if is_edu_email else 'pending',
                is_email_verified=True
            )
            
            if is_edu_email:
                return redirect('/sign-in/?status=approved')
            else:
                return redirect('/sign-in/?status=pending')
            
        except Exception as e:
            messages.error(request, f'注册失败：{str(e)}')
    
    return render(request, 'sign_up.html')


def user_logout(request):
    logout(request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('index')


@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            password = data.get('password')
            
            if not request.session.get('reset_verified') or not request.session.get('reset_user_id'):
                return JsonResponse({
                    'success': False,
                    'message': '身份验证已过期，请重新验证'
                })
            
            if len(password) < 6 or len(password) > 20:
                return JsonResponse({
                    'success': False,
                    'message': '密码长度必须在6-20位之间'
                })
            
            has_number = bool(re.search(r'\d', password))
            has_upper = bool(re.search(r'[A-Z]', password))
            has_lower = bool(re.search(r'[a-z]', password))
            has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password))
            
            conditions_met = sum([has_number, has_upper, has_lower, has_special])
            if conditions_met < 2:
                return JsonResponse({
                    'success': False,
                    'message': '密码强度不足，至少包含数字、大写字母、小写字母和特殊字符中的两种'
                })
            
            try:
                user = User.objects.get(id=request.session['reset_user_id'])
                user.set_password(password)
                user.save()
                
                request.session.pop('reset_user_id', None)
                request.session.pop('reset_verified', None)
                
                AuditLog.objects.create(
                    user=user,
                    action='password_reset',
                    description=f'用户通过密码找回功能重置了密码',
                    ip_address=request.META.get('REMOTE_ADDR', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'message': '密码重置成功'
                })
                
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户不存在'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '数据格式错误'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'重置失败：{str(e)}'
            })
    
@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            last_name = data.get('last_name')
            first_name = data.get('first_name')
            email = data.get('email')
            organization = data.get('organization')
            password = data.get('password')
            
            if not all([last_name, first_name, email, organization, password]):
                return JsonResponse({
                    'success': False,
                    'message': '请填写所有必填字段'
                })
            
            if len(password) < 6 or len(password) > 20:
                return JsonResponse({
                    'success': False,
                    'message': '密码长度必须在6-20位之间'
                })
            
            has_number = bool(re.search(r'\d', password))
            has_upper = bool(re.search(r'[A-Z]', password))
            has_lower = bool(re.search(r'[a-z]', password))
            has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password))
            
            conditions_met = sum([has_number, has_upper, has_lower, has_special])
            if conditions_met < 2:
                return JsonResponse({
                    'success': False,
                    'message': '密码强度不足，至少包含数字、大写字母、小写字母和特殊字符中的两种'
                })
            
            try:
                user = User.objects.get(
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                profile = user.userprofile
                
                if profile.organization.lower() != organization.lower():
                    return JsonResponse({
                        'success': False,
                        'message': '用户信息验证失败，请检查输入信息'
                    })
                
                user.set_password(password)
                user.save()
                
                AuditLog.objects.create(
                    user=user,
                    action='password_reset',
                    description=f'用户通过密码找回功能重置了密码',
                    ip_address=request.META.get('REMOTE_ADDR', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'message': '密码重置成功'
                })
                
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户信息验证失败，请检查输入信息'
                })
            except UserProfile.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户资料不完整'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '数据格式错误'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'重置失败：{str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '请求方法不允许'})


def user_logout(request):
    logout(request)
    
    # 如果是AJAX请求，返回JSON响应
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    # 否则重定向到首页
    return redirect('index')


def verification_sent(request):
    return render(request, 'verification_sent.html')


def verify_email_new(request):
    code = request.GET.get('code')
    
    if not code:
        messages.error(request, '无效的验证链接')
        return redirect('index')
    
    user = verify_email_code(code)
    
    if user:
        if not request.user.is_authenticated:
            login(request, user)
        
        messages.success(request, '邮箱验证成功！')
        
        try:
            profile = user.userprofile
            if profile.status == 'approved':
                return redirect('index')
            else:
                return render(request, 'verify_email_new.html', {'verified': True, 'status': profile.status})
        except UserProfile.DoesNotExist:
            return redirect('index')
    else:
        messages.error(request, '验证链接无效或已过期，请重新获取验证链接')
        return render(request, 'verify_email_new.html', {'verified': False})


def resend_verification(request):
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


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin)
def admin_dashboard(request):
    pending_count = UserProfile.objects.filter(status='pending').count()
    approved_count = UserProfile.objects.filter(status='approved').count()
    rejected_count = UserProfile.objects.filter(status='rejected').count()
    suspended_count = UserProfile.objects.filter(status='suspended').count()
    
    recent_users = UserProfile.objects.all().order_by('-created_at')[:10]
    
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
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('query', '')
    
    users = UserProfile.objects.all()
    
    if status_filter:
        users = users.filter(status=status_filter)
    
    if search_query:
        users = users.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(organization__icontains=search_query)
        )
    
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
    
    audit_logs = AuditLog.objects.filter(user_profile=user_profile).order_by('-created_at')
    
    context = {
        'user_profile': user_profile,
        'audit_logs': audit_logs,
    }
    
    return render(request, 'admin/user_detail.html', context)


def data_download(request):
    return render(request, 'data_download_1.0.html', {'user': request.user})

def model_instruction(request):
    return render(request, 'model_instruction.html', {'user': request.user})

def user_service(request):
    return render(request, 'user_service.html', {'user': request.user})


import random
import string
from django.core.mail import send_mail
from django.conf import settings


@csrf_exempt
def send_reset_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '该邮箱地址未注册'
                })
            
            verification_code = ''.join(random.choices(string.digits, k=6))
            
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
            
            return JsonResponse({
                'success': True,
                'message': f'验证码已发送到您的邮箱（测试：{verification_code}）'
            })
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'message': '请求格式错误'
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': '系统错误，请稍后重试'
            })
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})


@csrf_exempt
def verify_reset_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户不存在'
                })
            
            try:
                verification = UserVerification.objects.get(user=user)
                
                if verification.verification_code != code:
                    return JsonResponse({
                        'success': False,
                        'message': '验证码错误'
                    })
                
                time_diff = timezone.now() - verification.created_at
                if time_diff.total_seconds() > 600:
                    return JsonResponse({
                        'success': False,
                        'message': '验证码已过期，请重新获取'
                    })
                
                verification.is_verified = True
                verification.save()
                
                return JsonResponse({
                    'success': True,
                    'message': '验证成功'
                })
            except UserVerification.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '请先获取验证码'
                })
                
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'message': '请求格式错误'
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': '系统错误，请稍后重试'
            })
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})


@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')
            password = data.get('password')
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户不存在'
                })
            
            try:
                verification = UserVerification.objects.get(user=user)
                
                if not verification.is_verified:
                    return JsonResponse({
                        'success': False,
                        'message': '请先验证验证码'
                    })
                
                if verification.verification_code != code:
                    return JsonResponse({
                        'success': False,
                        'message': '验证码错误'
                    })
                
                time_diff = timezone.now() - verification.created_at
                if time_diff.total_seconds() > 900:
                    return JsonResponse({
                        'success': False,
                        'message': '验证码已过期，请重新获取'
                    })
                
            except UserVerification.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '验证信息不存在'
                })
            
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
            
            user.set_password(password)
            user.save()
            
            verification.delete()
            
            try:
                pass
            except:
                pass
            
            return JsonResponse({
                'success': True,
                'message': '密码重置成功'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': '系统错误，请稍后重试'
            })
    
    return JsonResponse({'success': False, 'message': '无效的请求方法'})

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import csv
import io
import json
import os
import tempfile
import zipfile
from datetime import datetime, timedelta
import random
import string

@login_required
@csrf_exempt
def get_available_data(request):
    if request.method != 'GET':
        return JsonResponse({'error': '仅支持GET请求'}, status=405)
    
    try:
        available_data = {
            'air_pollution': {
                'china': {
                    'PM2.5': {
                        'monthly': ['2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06',
                                   '2020-07', '2020-08', '2020-09', '2020-10', '2020-11', '2020-12',
                                   '2021-01', '2021-02', '2021-03', '2021-04', '2021-05', '2021-06',
                                   '2021-07', '2021-08', '2021-09', '2021-10', '2021-11', '2021-12',
                                   '2022-01', '2022-02', '2022-03', '2022-04', '2022-05', '2022-06',
                                   '2022-07', '2022-08', '2022-09', '2022-10', '2022-11', '2022-12',
                                   '2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06'],
                        'yearly': ['2020', '2021', '2022', '2023']
                    },
                    'PM10': {
                        'monthly': ['2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06',
                                   '2020-07', '2020-08', '2020-09', '2020-10', '2020-11', '2020-12',
                                   '2021-01', '2021-02', '2021-03', '2021-04', '2021-05', '2021-06'],
                        'yearly': ['2020', '2021', '2022']
                    },
                    'NO2': {
                        'monthly': ['2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06',
                                   '2020-07', '2020-08', '2020-09', '2020-10', '2020-11', '2020-12'],
                        'yearly': ['2020', '2021']
                    },
                    'O3': {
                        'monthly': ['2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06'],
                        'yearly': ['2020']
                    }
                },
                'uk': {
                    'PM2.5': {
                        'monthly': ['2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06'],
                        'yearly': ['2020', '2021']
                    },
                    'PM10': {
                        'monthly': ['2020-01', '2020-02', '2020-03', '2020-04'],
                        'yearly': ['2020']
                    }
                }
            },
            'weather': {
                'china': {
                    '温度': {
                        'monthly': ['2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06'],
                        'yearly': ['2020', '2021']
                    },
                    '紫外辐射': {
                        'monthly': ['2020-01', '2020-02', '2020-03'],
                        'yearly': ['2020']
                    }
                }
            },
            'urban': {
                'china': {
                    'NDVI': {
                        'monthly': ['2020-01', '2020-02', '2020-03'],
                        'yearly': ['2020']
                    }
                }
            }
        }
        
        return JsonResponse({
            'success': True,
            'data': available_data,
            'message': '数据列表获取成功'
        })
        
    except Exception as e:
        return JsonResponse({'error': f'获取数据列表失败: {str(e)}'}, status=500)

@login_required
@csrf_exempt  
def request_data_download(request):
    if request.method != 'POST':
        return JsonResponse({'error': '仅支持POST请求'}, status=405)
    
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        category = data.get('category', 'air_pollution')
        country = data.get('country', 'china')
        pollutant = data.get('pollutant', 'PM2.5')
        time_range = data.get('time_range', 'monthly')
        selected_dates = data.get('selected_dates', [])
        
        if not selected_dates:
            return JsonResponse({'error': '请选择至少一个时间段'}, status=400)
            
        task_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        
        file_info = {
            'task_id': task_id,
            'status': 'processing',
            'category': category,
            'country': country, 
            'pollutant': pollutant,
            'time_range': time_range,
            'selected_dates': selected_dates,
            'created_at': datetime.now().isoformat(),
            'estimated_size': len(selected_dates) * 1024 * 50,
            'download_url': None
        }
        
        try:
            download_url = generate_data_file(file_info)
            file_info['status'] = 'completed'
            file_info['download_url'] = download_url
            file_info['completed_at'] = datetime.now().isoformat()
        except Exception as e:
            file_info['status'] = 'failed'
            file_info['error'] = str(e)
        
        return JsonResponse({
            'success': True,
            'task_id': task_id,
            'status': file_info['status'],
            'download_url': file_info.get('download_url'),
            'estimated_size': file_info['estimated_size'],
            'message': '数据文件生成完成' if file_info['status'] == 'completed' else '数据文件生成失败'
        })
        
    except Exception as e:
        return JsonResponse({'error': f'请求处理失败: {str(e)}'}, status=500)

def generate_data_file(file_info):
    try:
        category = file_info['category']
        country = file_info['country']
        pollutant = file_info['pollutant']
        time_range = file_info['time_range']
        selected_dates = file_info['selected_dates']
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{country}_{category}_{pollutant}_{time_range}_{timestamp}.csv"
        
        csv_content = generate_csv_data(category, country, pollutant, time_range, selected_dates)
        
        download_url = f"/api/download-file/{file_info['task_id']}/"
        
        return download_url
        
    except Exception as e:
        raise Exception(f"文件生成失败: {str(e)}")

@login_required
@require_http_methods(["GET"])
def download_file(request, task_id):
    try:
        file_info = {
            'category': 'air_pollution',
            'country': 'china',
            'pollutant': 'PM2.5',
            'time_range': 'monthly',
            'selected_dates': ['2020-01', '2020-02', '2020-03']
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{file_info['country']}_{file_info['category']}_{file_info['pollutant']}_{timestamp}.csv"
        filename = filename.replace('<sub>', '').replace('</sub>', '').replace('.', '_')
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        response.write('\ufeff')
        writer = csv.writer(response)
        
        if file_info['category'] == 'air_pollution':
            generate_air_pollution_data(writer, file_info['country'], file_info['pollutant'], 
                                      file_info['time_range'], file_info['selected_dates'])
        elif file_info['category'] == 'weather':
            generate_weather_data(writer, file_info['pollutant'], file_info['time_range'], file_info['selected_dates'])
        elif file_info['category'] == 'urban':
            generate_urban_data(writer, file_info['pollutant'], file_info['time_range'], file_info['selected_dates'])
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': f'文件下载失败: {str(e)}'}, status=500)

def generate_csv_data(category, country, pollutant, time_range, selected_dates):
    output = io.StringIO()
    writer = csv.writer(output)
    
    if category == 'air_pollution':
        generate_air_pollution_data(writer, country, pollutant, time_range, selected_dates)
    elif category == 'weather':
        generate_weather_data(writer, pollutant, time_range, selected_dates)
    elif category == 'urban':
        generate_urban_data(writer, pollutant, time_range, selected_dates)
    
    return output.getvalue()

def generate_air_pollution_data(writer, country, pollutant, time_range, dates_input):
    import random
    from datetime import datetime, timedelta
    
    if isinstance(dates_input, list):
        dates = dates_input
        start_date = dates[0] if dates else '2020-01'
        end_date = dates[-1] if dates else '2020-01'
    else:
        start_date = dates_input
        end_date = time_range if isinstance(time_range, str) and '-' in time_range else start_date
        
        dates = []
        if 'month' in str(time_range):
            if '-' in start_date and '-' in end_date:
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
                dates = [start_date]
        else:
            try:
                start_year = int(start_date)
                end_year = int(end_date)
                dates = [str(year) for year in range(start_year, end_year + 1)]
            except:
                dates = [start_date]
    
    writer.writerow(['数据类型', '大气污染数据'])
    writer.writerow(['国家/地区', '中国' if country == 'china' else '英国'])
    writer.writerow(['污染物', pollutant])
    writer.writerow(['时间范围', '月均数据' if 'month' in str(time_range) else '年均数据'])
    writer.writerow(['时间段', f"{start_date} 至 {end_date}"])
    writer.writerow(['数据点数', len(dates)])
    writer.writerow(['下载时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['数据来源', '模拟数据'])
    writer.writerow([])
    
    if country == 'china':
        cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '重庆',
                 '天津', '苏州', '郑州', '长沙', '东莞', '青岛', '沈阳', '宁波', '昆明', '大连']
    else:
        cities = ['London', 'Manchester', 'Birmingham', 'Leeds', 'Glasgow', 'Liverpool', 
                 'Edinburgh', 'Bristol', 'Sheffield', 'Cardiff', 'Newcastle', 'Nottingham']
    
    writer.writerow(['时间', '城市', '经度', '纬度', f'{pollutant}浓度(μg/m³)', 'AQI', '空气质量等级', '数据质量'])
    
    for date in dates:
        for city in cities:
            if pollutant in ['PM2.5', 'PM<sub>2.5</sub>']:
                if country == 'china':
                    concentration = random.uniform(15, 120)
                else:
                    concentration = random.uniform(8, 45)
                aqi = int(concentration * 2.1 + random.uniform(-15, 15))
            elif pollutant in ['PM10', 'PM<sub>10</sub>']:
                if country == 'china':
                    concentration = random.uniform(25, 200)
                else:
                    concentration = random.uniform(15, 80)
                aqi = int(concentration * 1.4 + random.uniform(-10, 10))
            elif pollutant in ['PM2.5-PM10', 'PM<sub>2.5</sub>-PM<sub>10</sub>']:
                concentration = random.uniform(10, 80)
                aqi = int(concentration * 1.8 + random.uniform(-12, 12))
            elif pollutant in ['NO2', 'NO<sub>2</sub>']:
                concentration = random.uniform(10, 80)
                aqi = int(concentration * 2.5 + random.uniform(-20, 20))
            elif pollutant in ['O3', 'O<sub>3</sub>']:
                concentration = random.uniform(50, 160)
                aqi = int(concentration * 1.1 + random.uniform(-25, 25))
            elif pollutant == 'CO':
                concentration = random.uniform(0.5, 4.0)
                aqi = int(concentration * 45 + random.uniform(-15, 15))
            else:
                concentration = random.uniform(20, 100)
                aqi = random.randint(50, 200)
            
            if country == 'china':
                longitude = random.uniform(110, 125)
                latitude = random.uniform(30, 45)
            else:
                longitude = random.uniform(-5, 2)
                latitude = random.uniform(50, 58)
            
            if aqi <= 50:
                quality_level = '优'
            elif aqi <= 100:
                quality_level = '良'
            elif aqi <= 150:
                quality_level = '轻度污染'
            elif aqi <= 200:
                quality_level = '中度污染'
            elif aqi <= 300:
                quality_level = '重度污染'
            else:
                quality_level = '严重污染'
            
            data_quality = random.choice(['优', '良', '优', '优'])
            
            writer.writerow([
                date,
                city,
                f"{longitude:.4f}",
                f"{latitude:.4f}",
                f"{concentration:.2f}",
                max(0, min(500, aqi)),
                quality_level,
                data_quality
            ])

def generate_weather_data(writer, indicator, time_range, dates_input):
    import random
    from datetime import datetime
    
    if isinstance(dates_input, list):
        dates = dates_input
        start_date = dates[0] if dates else '2020-01'
        end_date = dates[-1] if dates else '2020-01'
    else:
        start_date = dates_input
        end_date = time_range if isinstance(time_range, str) and '-' in time_range else start_date
        
        # 生成时间序列
        dates = []
        if 'month' in str(time_range):
            if '-' in start_date and '-' in end_date:
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
                dates = [start_date]
        else:
            try:
                start_year = int(start_date)
                end_year = int(end_date)
                dates = [str(year) for year in range(start_year, end_year + 1)]
            except:
                dates = [start_date]
    
    # 写入元数据
    writer.writerow(['数据类型', '气象数据'])
    writer.writerow(['国家/地区', '中国'])
    writer.writerow(['气象指标', indicator])
    writer.writerow(['时间范围', '月均数据' if 'month' in str(time_range) else '年均数据'])
    writer.writerow(['时间段', f"{start_date} 至 {end_date}"])
    writer.writerow(['数据点数', len(dates)])
    writer.writerow(['下载时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['数据来源', '模拟腾讯云对象存储'])
    writer.writerow([])
    
    cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '重庆',
             '天津', '苏州', '郑州', '长沙', '青岛', '沈阳', '宁波', '昆明', '大连', '哈尔滨']
    
    # 根据指标设置表头和单位
    if indicator == '温度':
        writer.writerow(['时间', '城市', '经度', '纬度', '平均温度(°C)', '最高温度(°C)', '最低温度(°C)', '湿度(%)', '数据质量'])
    elif indicator == '紫外辐射':
        writer.writerow(['时间', '城市', '经度', '纬度', 'UV指数', 'UV强度等级', '云量(%)', '数据质量'])
    
    # 生成数据
    for date in dates:
        for city in cities:
            longitude = random.uniform(110, 125)
            latitude = random.uniform(30, 45)
            quality = random.choice(['优', '良', '优', '优'])
            
            if indicator == '温度':
                # 根据月份生成合理的温度
                if '-' in date:
                    month = int(date.split('-')[1])
                    if month in [12, 1, 2]:  # 冬季
                        avg_temp = random.uniform(-10, 10)
                    elif month in [3, 4, 5]:  # 春季
                        avg_temp = random.uniform(10, 25)
                    elif month in [6, 7, 8]:  # 夏季
                        avg_temp = random.uniform(25, 38)
                    else:  # 秋季
                        avg_temp = random.uniform(15, 28)
                else:
                    avg_temp = random.uniform(5, 25)
                
                max_temp = avg_temp + random.uniform(3, 12)
                min_temp = avg_temp - random.uniform(3, 12)
                humidity = random.uniform(30, 80)
                
                writer.writerow([
                    date, city, f"{longitude:.4f}", f"{latitude:.4f}",
                    f"{avg_temp:.1f}", f"{max_temp:.1f}", f"{min_temp:.1f}", 
                    f"{humidity:.1f}", quality
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
                
                cloud_cover = random.uniform(0, 100)
                
                writer.writerow([
                    date, city, f"{longitude:.4f}", f"{latitude:.4f}",
                    f"{uv_index:.1f}", uv_level, f"{cloud_cover:.1f}", quality
                ])

def generate_urban_data(writer, indicator, time_range, dates_input):
    import random
    from datetime import datetime
    
    if isinstance(dates_input, list):
        dates = dates_input
        start_date = dates[0] if dates else '2020-01'
        end_date = dates[-1] if dates else '2020-01'
    else:
        start_date = dates_input
        end_date = time_range if isinstance(time_range, str) and '-' in time_range else start_date
        
        # 生成时间序列
        dates = []
        if 'month' in str(time_range):
            if '-' in start_date and '-' in end_date:
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
                dates = [start_date]
        else:
            try:
                start_year = int(start_date)
                end_year = int(end_date)
                dates = [str(year) for year in range(start_year, end_year + 1)]
            except:
                dates = [start_date]
    
    # 写入元数据
    writer.writerow(['数据类型', '建成环境数据'])
    writer.writerow(['国家/地区', '中国'])
    writer.writerow(['建成指标', indicator])
    writer.writerow(['时间范围', '月均数据' if 'month' in str(time_range) else '年均数据'])
    writer.writerow(['时间段', f"{start_date} 至 {end_date}"])
    writer.writerow(['数据点数', len(dates)])
    writer.writerow(['下载时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['数据来源', '模拟腾讯云对象存储'])
    writer.writerow([])
    
    cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '重庆',
             '天津', '苏州', '郑州', '长沙', '青岛', '沈阳', '宁波', '昆明', '大连', '福州']
    
    if indicator == 'NDVI':
        writer.writerow(['时间', '城市', '经度', '纬度', 'NDVI值', '植被覆盖等级', '绿化率(%)', '数据质量'])
    
    # 生成数据
    for date in dates:
        for city in cities:
            longitude = random.uniform(110, 125)
            latitude = random.uniform(30, 45)
            quality = random.choice(['优', '良', '优', '优'])
            
            if indicator == 'NDVI':
                # 根据月份生成季节性NDVI变化
                if '-' in date:
                    month = int(date.split('-')[1])
                    if month in [12, 1, 2]:  # 冬季
                        ndvi = random.uniform(0.1, 0.4)
                    elif month in [3, 4, 5]:  # 春季
                        ndvi = random.uniform(0.3, 0.7)
                    elif month in [6, 7, 8]:  # 夏季
                        ndvi = random.uniform(0.5, 0.9)
                    else:  # 秋季
                        ndvi = random.uniform(0.2, 0.6)
                else:
                    ndvi = random.uniform(0.2, 0.7)
                
                if ndvi < 0.2:
                    vegetation_level = '稀疏植被'
                elif ndvi < 0.4:
                    vegetation_level = '中等植被'
                elif ndvi < 0.6:
                    vegetation_level = '密集植被'
                else:
                    vegetation_level = '极密植被'
                
                green_rate = ndvi * 100 + random.uniform(-10, 10)
                green_rate = max(0, min(100, green_rate))
                
                writer.writerow([
                    date, city, f"{longitude:.4f}", f"{latitude:.4f}",
                    f"{ndvi:.3f}", vegetation_level, f"{green_rate:.1f}", quality
                ])
