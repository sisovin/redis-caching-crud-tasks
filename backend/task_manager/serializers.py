from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Task

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user references in tasks"""
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['username']

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model with additional computed fields.
    Supports both read and write operations with proper validation.
    """
    is_overdue = serializers.BooleanField(read_only=True)
    time_since_created = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField(read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Task
        fields = [
            'id', 
            'title', 
            'description', 
            'completed', 
            'created_at',
            'updated_at',
            'due_date',
            'priority',
            'status',
            'user',
            'user_details',
            'is_overdue',
            'time_since_created',
            'days_until_due'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_overdue']

    def get_time_since_created(self, obj):
        """
        Returns a human-readable string representing time since task creation.
        Example: "2 days ago", "5 hours ago", etc.
        """
        from django.utils.timesince import timesince
        return timesince(obj.created_at, timezone.now())

    def get_days_until_due(self, obj):
        """
        Returns number of days until due date, negative if overdue.
        Returns None if no due date is set.
        """
        if not obj.due_date:
            return None
        
        delta = obj.due_date - timezone.now().date()
        return delta.days

    def create(self, validated_data):
        """
        Create a new task and associate it with the current user.
        """
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def validate_due_date(self, value):
        """
        Validate due date is not in the past.
        """
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate_title(self, value):
        """
        Validate title is not too short.
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value

    def validate(self, data):
        """
        Custom validation for the entire task object.
        """
        # If marking as completed, ensure status is also set to completed
        if data.get('completed') and data.get('status') != 'completed':
            data['status'] = 'completed'
            
        # If status is changed to completed, ensure completed flag is True
        if data.get('status') == 'completed' and not data.get('completed', False):
            data['completed'] = True
        
        # Ensure high priority tasks have due dates
        if data.get('priority', 0) >= 3 and not data.get('due_date'):
            raise serializers.ValidationError({
                'due_date': 'Due date is required for high priority tasks'
            })
            
        return data

    def to_representation(self, instance):
        """
        Add cache metadata to representation if available
        """
        representation = super().to_representation(instance)
        
        # Add cache information for debugging if available
        if hasattr(instance, 'cache_timestamp'):
            representation['_cache_info'] = {
                'from_cache': True,
                'cached_at': instance.cache_timestamp
            }
            
        return representation