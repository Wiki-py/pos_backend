from django.db import models
from apps.branches.models import Branch

class Report(models.Model):
    REPORT_TYPES = [
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('customer', 'Customer Report'),
        ('financial', 'Financial Report'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    period = models.CharField(max_length=100)  # e.g., "September 2023", "Q3 2023"
    generated_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Store report data as JSON
    file_path = models.FileField(upload_to='reports/', null=True, blank=True)
    is_exported = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.period}"

    class Meta:
        db_table = 'reports'