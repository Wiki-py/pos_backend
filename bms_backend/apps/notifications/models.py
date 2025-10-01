from django.db import models
from apps.users.models import User
from apps.branches.models import Branch

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    action_url = models.CharField(max_length=500, blank=True)
    priority = models.IntegerField(default=1)  # 1=Low, 2=Medium, 3=High

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']