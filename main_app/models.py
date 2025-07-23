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
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"
    
    def save(self, *args, **kwargs):
        # 自动检测教育邮箱
        if self.user.email and '@' in self.user.email:
            self.is_edu_email = self.user.email.lower().endswith('.edu.cn')
            # 教育邮箱自动审核通过
            if self.is_edu_email:
                self.is_approved = True
        super().save(*args, **kwargs)


class DataDownload(models.Model):
    """数据下载记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset_name = models.CharField(max_length=200)
    download_time = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(default=0)
    download_url = models.URLField()
    
    def __str__(self):
        return f"{self.user.username} - {self.dataset_name}"
    
    class Meta:
        ordering = ['-download_time']
