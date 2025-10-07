from django.db import models

class Branch(models.Model):
    BRANCH_TYPES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing & Apparel'),
        ('food', 'Food & Beverages'),
        ('home', 'Home & Furniture'),
        ('sports', 'Sports & Outdoors'),
        ('beauty', 'Beauty & Health'),
        ('books', 'Books & Stationery'),
        ('automotive', 'Automotive'),
        ('jewelry', 'Jewelry & Accessories'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50, choices=BRANCH_TYPES)
    location = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    manager = models.CharField(max_length=100, blank=True)
    opening_date = models.DateField(null=True, blank=True)
    capacity = models.IntegerField(default=0)
    
    description = models.TextField(blank=True)
    color_theme = models.CharField(max_length=100, default='from-emerald-400 to-teal-500')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.location}"

    class Meta:
        db_table = 'branches'
        verbose_name_plural = 'Branches'