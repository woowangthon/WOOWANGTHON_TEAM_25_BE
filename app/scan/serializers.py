
from urllib.parse import urlsplit

from rest_framework import serializers


class BusinessInfoSerializer(serializers.Serializer):
    business_name = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=255,
    )
    representative_name = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=100,
    )
    business_number = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=20,
    )
    address = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=500,
    )


class ScanRequestSerializer(serializers.Serializer):
    url = serializers.URLField(
        required=True,
        max_length=2048,
    )
    business_info = BusinessInfoSerializer(
        required=False,
        default=dict,
    )

    def validate_url(self, value):
        parsed = urlsplit(value)

        if parsed.scheme.lower() not in ("http", "https"):
            raise serializers.ValidationError(
                "HTTP 또는 HTTPS URL만 허용됩니다."
            )

        if not parsed.hostname:
            raise serializers.ValidationError(
                "유효한 도메인이 필요합니다."
            )

        if parsed.username or parsed.password:
            raise serializers.ValidationError(
                "인증 정보가 포함된 URL은 허용하지 않습니다."
            )

        return value
