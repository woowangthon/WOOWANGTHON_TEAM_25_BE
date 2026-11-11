# scan 앱은 프론트에서 정보 받고 함수 끌어와서 처리 후 다시 프론트로 내보내게 됩니다.
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from .serializers import ScanRequestSerializer
from .services import run_scan
import logging

logger = logging.getLogger(__name__)
class ScanAPIView(APIView):
    permission_classes = [AllowAny]
    logger.info("왜 안되냐 \n")
    def dispatch(self, request, *args, **kwargs):
        print(
            f"🔥 METHOD: {request.method}",
            flush=True
        )

        return super().dispatch(request, *args, **kwargs)
    def post(self, request,  *args, **kwargs):
        print("========== POST METHOD ENTERED ==========")
        logger.warning("POST METHOD ENTERED")
        logger.error("POST METHOD ERROR TEST")

        print("REQUEST DATA:", request.data)
        serializer = ScanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
       
        result = run_scan(
            url=serializer.validated_data["url"],
            business_info=serializer.validated_data.get("business_info", {})
        )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )