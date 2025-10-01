from django.db import models
from apps.products.models import Product
from apps.branches.models import Branch
from apps.users.models import User

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjust', 'Adjustment'),
        ('return', 'Return'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reason = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, blank=True)  # PO number, etc.

    def save(self, *args, **kwargs):
        if not self.pk:  # New transaction
            self.previous_stock = self.product.quantity
            if self.transaction_type == 'in':
                self.product.quantity += self.quantity
            elif self.transaction_type in ['out', 'return']:
                self.product.quantity -= self.quantity
            self.new_stock = self.product.quantity
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} ({self.quantity})"

    class Meta:
        app_label = 'inventory'
        db_table = 'inventory_transactions'