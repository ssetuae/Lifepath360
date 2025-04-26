from django.db import models
from django.conf import settings
from django_cryptography.fields import encrypt
from django.utils import timezone
import uuid

class AccessLog(models.Model):
    """
    Model for tracking user access for audit purposes.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='access_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    action = models.CharField(max_length=50)  # e.g., 'login', 'view_report', 'edit_question'
    resource_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'assessment', 'user', 'question'
    resource_id = models.CharField(max_length=50, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='success')  # 'success', 'failure', 'denied'
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'resource_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email if self.user else 'Anonymous'} - {self.action} - {self.timestamp}"


class DataEncryption(models.Model):
    """
    Model for storing encryption keys and initialization vectors.
    """
    key_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    iv = models.BinaryField()
    description = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Key {self.key_id} - {'Active' if self.active else 'Inactive'}"


class SensitiveData(models.Model):
    """
    Model for storing sensitive student data with encryption.
    """
    student = models.OneToOneField('diagnostic.Student', on_delete=models.CASCADE, related_name='sensitive_data')
    medical_notes = encrypt(models.TextField(blank=True, null=True))
    special_accommodations = encrypt(models.TextField(blank=True, null=True))
    parent_contact = encrypt(models.TextField(blank=True, null=True))
    additional_notes = encrypt(models.TextField(blank=True, null=True))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='accessed_sensitive_data')
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        permissions = [
            ("view_sensitive_data", "Can view sensitive student data"),
            ("edit_sensitive_data", "Can edit sensitive student data"),
        ]
    
    def __str__(self):
        return f"Sensitive data for {self.student.first_name} {self.student.last_name}"
    
    def record_access(self, user):
        """Record when sensitive data is accessed and by whom."""
        self.last_accessed_by = user
        self.last_accessed_at = timezone.now()
        self.save(update_fields=['last_accessed_by', 'last_accessed_at'])
        
        # Log access for audit
        AccessLog.objects.create(
            user=user,
            action='view_sensitive_data',
            resource_type='student',
            resource_id=str(self.student.id),
            details=f"Viewed sensitive data for student {self.student.id}",
            status='success'
        )


class SecurityPolicy(models.Model):
    """
    Model for storing security policies and their enforcement status.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    settings = models.JSONField(default=dict)
    
    class Meta:
        verbose_name_plural = "Security policies"
    
    def __str__(self):
        return f"{self.name} - {'Enabled' if self.enabled else 'Disabled'}"


class FailedLoginAttempt(models.Model):
    """
    Model for tracking failed login attempts for security monitoring.
    """
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['email', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    @classmethod
    def check_lockout(cls, email, ip_address):
        """Check if account should be temporarily locked due to too many failed attempts."""
        recent_time = timezone.now() - timezone.timedelta(minutes=15)
        count = cls.objects.filter(
            email=email,
            ip_address=ip_address,
            timestamp__gte=recent_time
        ).count()
        
        return count >= 5  # Lock after 5 failed attempts within 15 minutes
