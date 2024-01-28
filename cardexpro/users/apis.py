from rest_framework import status
from django.http import HttpRequest
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from cardexpro.api.mixins import ApiAuthMixin
from cardexpro.users.services import register
from drf_spectacular.utils import extend_schema
from django.core.validators import MinLengthValidator
from cardexpro.users.models import BaseUser, Activity
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .validators import number_validator, special_char_validator, letter_validator
from cardexpro.api.pagination import LimitOffsetPagination, get_paginated_response_context
from cardexpro.common.services import error_response, success_response, handle_validation_error




class RegisterApi(APIView):

    class InputRegisterSerializer(serializers.Serializer):
        email = serializers.EmailField(max_length=255)
        password = serializers.CharField(
                validators=[
                        number_validator,
                        letter_validator,
                        special_char_validator,
                        MinLengthValidator(limit_value=8)
                    ]
                )
        confirm_password = serializers.CharField(max_length=255)
        
        def validate_email(self, email):
            if BaseUser.objects.filter(email=email).exists():
                raise serializers.ValidationError("Email already taken")
            return email

        def validate(self, data):
            if not data.get("password") or not data.get("confirm_password"):
                raise serializers.ValidationError("Please fill password and confirm password")
            
            if data.get("password") != data.get("confirm_password"):
                raise serializers.ValidationError("confirm password is not equal to password")
            return data


    class OutPutRegisterSerializer(serializers.ModelSerializer):

        token = serializers.SerializerMethodField("get_token")

        class Meta:
            model = BaseUser 
            fields = ("email", "token", "created_at", "updated_at")

        def get_token(self, user):
            data = dict()
            token_class = RefreshToken

            refresh = token_class.for_user(user)

            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            return data


    @extend_schema(request=InputRegisterSerializer, responses=OutPutRegisterSerializer)
    def post(self, request):
        serializer = self.InputRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = register(
                    email=serializer.validated_data.get("email"),
                    password=serializer.validated_data.get("password"),
                    )
        except Exception as ex:
            return Response(
                    f"Database Error {ex}",
                    status=status.HTTP_400_BAD_REQUEST
                    )
        return Response(self.OutPutRegisterSerializer(user, context={"request": request}).data)

class ActivitiesApi(ApiAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class FilterActivitiesSerializer(serializers.Serializer):
        # body = serializers.JSONField(required=False)
        pass

    class InputActivitiesSerializer(serializers.Serializer):
        body = serializers.JSONField(required=True)

    class OutPutActivitiesSerializer(serializers.ModelSerializer):
        class Meta:
            model = Activity
            fields = ('id', 'user', 'body',)

    @extend_schema(request=InputActivitiesSerializer, responses=OutPutActivitiesSerializer, tags=['Activities'])
    def post(self, request: HttpRequest):
        serializer = self.InputActivitiesSerializer(data=request.data)
        validation_result = handle_validation_error(serializer=serializer)
        if not isinstance(validation_result, bool):
            return Response(validation_result, status=status.HTTP_400_BAD_REQUEST)

        try:
            activity = Activity.create_activity(user=request.user, **serializer.validated_data)
        except Exception as ex:
            response = error_response(message=str(ex))
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.OutPutActivitiesSerializer(activity, context={"request": request}).data)

    @extend_schema(parameters=[FilterActivitiesSerializer], responses=OutPutActivitiesSerializer, tags=['Activities'])
    def get(self, request: HttpRequest):
        filter_serializer = self.FilterActivitiesSerializer(data=request.query_params)
        validation_result = handle_validation_error(serializer=filter_serializer)
        if not isinstance(validation_result, bool):  # if validation_result response is not boolean
            return Response(validation_result, status=status.HTTP_400_BAD_REQUEST)

        try:
            activities = Activity.get_activity(user=request.user)
        except Exception as ex:
            response = error_response(message=str(ex))
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return get_paginated_response_context(
            request=request,
            pagination_class=self.Pagination,
            serializer_class=self.OutPutActivitiesSerializer,
            queryset=activities,
            view=self,
        )