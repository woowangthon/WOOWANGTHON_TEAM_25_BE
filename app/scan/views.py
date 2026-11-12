# scan 앱은 프론트에서 정보 받고 함수 끌어와서 처리 후 다시 프론트로 내보내게 됩니다.

import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from .serializers import ScanRequestSerializer
from .services import run_scan

logger = logging.getLogger(__name__)


class ScanAPIView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, *args, **kwargs):
        logger.debug("HTTP METHOD: %s", request.method)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logger.info("POST METHOD ENTERED")

        serializer = ScanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # logger.debug(
        #     "Validated business info: %s",
        #     serializer.validated_data.get("business_info", {}),
        # )

        result = run_scan(
            url=serializer.validated_data["url"],
            business_info=serializer.validated_data.get("business_info", {}),
        )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )
