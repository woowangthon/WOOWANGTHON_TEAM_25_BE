from urllib.parse import urlsplit

from rest_framework import serializers


class ScanRequestSerializer(serializers.Serializer):
    url = serializers.URLField(
        required=True,
        max_length=2048,
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