from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """用户配置文件模型"""
    ORGANIZATION_TYPE_CHOICES = [
        ('university', '高等院校'),
        ('research_institute', '科研院所'),
        ('government', '政府机构'),
        ('enterprise', '企业单位'),
        ('ngo', '非政府组织'),
        ('hospital', '医疗机构'),
        ('other', '其他机构'),
    ]
    
    COUNTRY_CHOICES = [
        ('CN', '中国'),
        ('US', '美国'),
        ('GB', '英国'),
        ('JP', '日本'),
        ('KR', '韩国'),
        ('DE', '德国'),
        ('FR', '法国'),
        ('CA', '加拿大'),
        ('AU', '澳大利亚'),
        ('SG', '新加坡'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
        ('suspended', '已暂停'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="电话")
    organization = models.CharField(max_length=200, blank=True, null=True, verbose_name="机构名称")
    organization_type = models.CharField(
        max_length=50, 
        choices=ORGANIZATION_TYPE_CHOICES, 
        blank=True, 
        null=True,
        verbose_name="机构类型"
    )
    country = models.CharField(
        max_length=10, 
        choices=COUNTRY_CHOICES, 
        blank=True, 
        null=True,
        verbose_name="机构国家/地区"
    )
    is_edu_email = models.BooleanField(default=False, verbose_name="是否教育邮箱")
    is_approved = models.BooleanField(default=False, verbose_name="是否审核通过")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="审核状态"
    )
    verification_code = models.CharField(max_length=64, blank=True, null=True, verbose_name="验证码")
    is_email_verified = models.BooleanField(default=False, verbose_name="邮箱是否已验证")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="拒绝原因")
    admin_notes = models.TextField(blank=True, null=True, verbose_name="管理员备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    def __str__(self):
        return f"{self.user.username} Profile"
    
    def save(self, *args, **kwargs):
        # 自动检测教育邮箱
        if self.user.email and '@' in self.user.email:
            self.is_edu_email = self.user.email.lower().endswith('.edu.cn')
            # 教育邮箱自动审核通过
            if self.is_edu_email and not self.id:  # 只在创建时自动审核
                self.is_approved = True
                self.status = 'approved'
            elif not self.id:  # 非教育邮箱且是新用户
                self.status = 'pending'
        super().save(*args, **kwargs)


class UserVerification(models.Model):
    """用户邮箱验证模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=64, verbose_name="验证码")
    verification_code = models.CharField(max_length=64, verbose_name="重置密码验证码", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    expires_at = models.DateTimeField(verbose_name="过期时间", blank=True, null=True)
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")
    is_verified = models.BooleanField(default=False, verbose_name="是否已验证")
    
    def __str__(self):
        return f"{self.user.username} - {self.code}"


class AuditLog(models.Model):
    """审核日志模型"""
    ACTION_CHOICES = [
        ('approve', '审核通过'),
        ('reject', '拒绝申请'),
        ('suspend', '暂停账户'),
        ('reactivate', '重新激活'),
        ('other', '其他操作'),
    ]
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name="用户资料")
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="audit_logs", verbose_name="管理员")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="操作类型")
    notes = models.TextField(blank=True, null=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    
    def __str__(self):
        return f"{self.admin_user} - {self.action} - {self.user_profile.user.username}"
    
    class Meta:
        ordering = ['-created_at']
