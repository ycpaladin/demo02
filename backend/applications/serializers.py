from rest_framework import serializers
from applications.models import Application, Navigation


class ApplicationSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_children(self, obj):
        if obj.children.exists():
            return ApplicationSerializer(obj.children.all(), many=True).data
        return []


class NavigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Navigation
        fields = '__all__'
        read_only_fields = ['id', 'application', 'created_at', 'updated_at']
