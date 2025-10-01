from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('created_at',)

class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('user', 'branch', 'title', 'message', 'notification_type', 'action_url', 'priority')