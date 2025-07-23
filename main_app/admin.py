from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, UserVerification, AuditLog
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户资料'
    fieldsets = (
        ('基本信息', {'fields': ('phone', 'organization', 'organization_type', 'country')}),
        ('审核状态', {'fields': ('is_edu_email', 'is_approved', 'status', 'is_email_verified')}),
        ('审核信息', {'fields': ('rejection_reason', 'admin_notes')}),
    )
    readonly_fields = ('is_edu_email',)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_status', 'get_organization')
    list_filter = ('is_staff', 'is_superuser', 'userprofile__status', 'userprofile__organization_type', 'userprofile__country')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'userprofile__organization')
    inlines = (UserProfileInline,)
    
    def get_status(self, obj):
        try:
            status = obj.userprofile.status
            status_colors = {
                'pending': 'orange',
                'approved': 'green',
                'rejected': 'red',
                'suspended': 'gray',
            }
            color = status_colors.get(status, 'black')
            return format_html('<span style="color: {};">{}</span>', color, obj.userprofile.get_status_display())
        except UserProfile.DoesNotExist:
            return "未设置"
    get_status.short_description = '审核状态'
    
    def get_organization(self, obj):
        try:
            return obj.userprofile.organization
        except UserProfile.DoesNotExist:
            return "未设置"
    get_organization.short_description = '机构名称'


# 重新注册User模型
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'organization_type', 'country', 'status', 'is_edu_email', 'is_email_verified', 'created_at')
    list_filter = ('status', 'is_edu_email', 'is_email_verified', 'organization_type', 'country', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'organization')
    readonly_fields = ('is_edu_email', 'created_at', 'updated_at')
    fieldsets = (
        ('用户信息', {'fields': ('user', 'phone')}),
        ('机构信息', {'fields': ('organization', 'organization_type', 'country')}),
        ('审核状态', {'fields': ('status', 'is_approved', 'is_edu_email', 'is_email_verified')}),
        ('审核详情', {'fields': ('rejection_reason', 'admin_notes')}),
        ('时间信息', {'fields': ('created_at', 'updated_at')})
    )
    actions = ['approve_users', 'reject_users', 'suspend_users', 'reactivate_users']
    
    def approve_users(self, request, queryset):
        for profile in queryset:
            profile.status = 'approved'
            profile.is_approved = True
            profile.save()
            
            # 记录审核日志
            AuditLog.objects.create(
                user_profile=profile,
                admin_user=request.user,
                action='approve',
                notes='批量审核通过'
            )
        self.message_user(request, f'已批准 {queryset.count()} 个用户账户')
    approve_users.short_description = "批准选中的用户"
    
    def reject_users(self, request, queryset):
        for profile in queryset:
            profile.status = 'rejected'
            profile.is_approved = False
            profile.save()
            
            # 记录审核日志
            AuditLog.objects.create(
                user_profile=profile,
                admin_user=request.user,
                action='reject',
                notes='批量拒绝申请'
            )
        self.message_user(request, f'已拒绝 {queryset.count()} 个用户申请')
    reject_users.short_description = "拒绝选中的用户"
    
    def suspend_users(self, request, queryset):
        for profile in queryset:
            profile.status = 'suspended'
            profile.is_approved = False
            profile.save()
            
            # 记录审核日志
            AuditLog.objects.create(
                user_profile=profile,
                admin_user=request.user,
                action='suspend',
                notes='批量暂停账户'
            )
        self.message_user(request, f'已暂停 {queryset.count()} 个用户账户')
    suspend_users.short_description = "暂停选中的用户"
    
    def reactivate_users(self, request, queryset):
        for profile in queryset:
            profile.status = 'approved'
            profile.is_approved = True
            profile.save()
            
            # 记录审核日志
            AuditLog.objects.create(
                user_profile=profile,
                admin_user=request.user,
                action='reactivate',
                notes='批量重新激活账户'
            )
        self.message_user(request, f'已重新激活 {queryset.count()} 个用户账户')
    reactivate_users.short_description = "重新激活选中的用户"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'admin_user', 'action', 'created_at')
    list_filter = ('action', 'created_at', 'admin_user')
    search_fields = ('user_profile__user__username', 'user_profile__user__email', 'admin_user__username', 'notes')
    readonly_fields = ('user_profile', 'admin_user', 'action', 'created_at')


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'code')
    readonly_fields = ('created_at',)
