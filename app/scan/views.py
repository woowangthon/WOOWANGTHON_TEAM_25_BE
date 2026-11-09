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

    def post(self, request):
            # logger.info("SCAN API REQUEST RECEIVED")
            # logger.debug("Request data: %s", request.data)

        serializer = ScanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
            # if not serializer.is_valid():
            #     logger.warning(
            #         "Serializer validation failed: %s",
            #         serializer.errors,
            #     )

        result = run_scan(
            url=serializer.validated_data["url"],
            business_info=serializer.validated_data.get("business_info", {})
        )
            # logger.info(
            #     "SCAN COMPLETED: scan_id=%s",
            #     result["scan_id"],
            # )
        return Response(
            result,
            status=status.HTTP_200_OK,
        )