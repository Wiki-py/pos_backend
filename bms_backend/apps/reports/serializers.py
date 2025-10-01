from rest_framework import serializers
from .models import Report
from apps.branches.models import Branch

class ReportSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)

    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('generated_at',)

class ReportGenerateSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=Report.REPORT_TYPES)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    period = serializers.CharField(required=False)
    export_format = serializers.ChoiceField(choices=[('pdf', 'PDF'), ('excel', 'Excel')], required=False)