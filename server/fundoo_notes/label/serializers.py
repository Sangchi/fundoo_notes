from rest_framework import serializers
from .models import Label



class LabelSerializer(serializers.ModelSerializer):

    class Meta:
        model=Label
        fields='__all__'
    

    def validate_name(self, value):
        if isinstance(value, int):
            raise serializers.ValidationError("The name field cannot be an integer.")
        return value