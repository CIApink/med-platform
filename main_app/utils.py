import uuid
import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import UserVerification


def generate_verification_code():
    """生成唯一的验证码"""
    return str(uuid.uuid4())


def send_verification_email(user, request=None):
    """发送验证邮件给用户"""
    # 生成验证码
    verification_code = generate_verification_code()
    
    # 设置过期时间 (24小时后)
    expires_at = timezone.now() + datetime.timedelta(hours=24)
    
    # 保存验证信息
    verification = UserVerification.objects.create(
        user=user,
        code=verification_code,
        expires_at=expires_at
    )
    
    # 构建验证链接
    verify_url = f"{settings.BASE_URL}/verify-email/?code={verification_code}"
    
    # 邮件内容
    context = {
        'user': user,
        'verify_url': verify_url,
        'expires_hours': 24,
    }
    email_html_message = render_to_string('emails/verify_email.html', context)
    email_plaintext_message = render_to_string('emails/verify_email.txt', context)
    
    # 发送邮件
    try:
        send_mail(
            subject="MED平台 - 请验证您的邮箱",
            message=email_plaintext_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=email_html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"发送邮件失败: {str(e)}")
        return False


def verify_email_code(code):
    """验证邮箱验证码"""
    try:
        # 查找未使用且未过期的验证码
        verification = UserVerification.objects.get(
            code=code,
            is_used=False,
            expires_at__gt=timezone.now()
        )
        
        # 标记为已使用
        verification.is_used = True
        verification.save()
        
        # 更新用户资料
        user_profile = verification.user.userprofile
        user_profile.is_email_verified = True
        user_profile.save()
        
        return verification.user
    
    except UserVerification.DoesNotExist:
        return None
