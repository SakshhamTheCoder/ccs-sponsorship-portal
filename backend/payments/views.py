from .serializers import PaymentSerializer
from .models import Payment
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import requests
import json
import base64
import hashlib
import time
from django.conf import settings
from sponsorship.models import Sponsor
from django.db import transaction


class PaymentGatewayView(APIView):
    def post(self, request):

        # Load settings and constants
        merchant_id = settings.PHONEPE_MERCHANT_ID
        salt_key = settings.PHONEPE_SALT_KEY
        salt_index = 1
        env = "UAT"  # Set to "PROD" for production

        BASE_URLS = {
            "UAT": "https://api-preprod.phonepe.com/apis/pg-sandbox",
            "PROD": "https://api.phonepe.com/apis/hermes",
        }

        # Validate and get sponsor
        sponsor_id = request.data.get("sponsor_id")
        if not sponsor_id:
            return Response({"error": "Sponsor ID is required"}, status=400)

        try:
            sponsor = Sponsor.objects.get(id=sponsor_id)
        except Sponsor.DoesNotExist:
            return Response({"error": "Sponsor not found!"}, status=404)

        # Generate unique transaction details
        unique_transaction_id = f"{sponsor.id}_{int(time.time() * 1000)}"
        ui_redirect_url = f"{settings.PHONEPE_RETURN_URL}{unique_transaction_id}/"
        s2s_callback_url = settings.PHONEPE_CALLBACK_URL  # Must be HTTPS

        # Calculate payment amount in smallest currency unit (paise

        # Prepare payment payload
        payload = {
            "merchantId": merchant_id,
            "merchantTransactionId": unique_transaction_id,
            "merchantUserId": sponsor.id,
            "amount": int(sponsor.amount * 100),
            "redirectUrl": ui_redirect_url,
            "redirectMode": "REDIRECT",
            "callbackUrl": s2s_callback_url,
            "paymentInstrument": {"type": "PAY_PAGE"},
        }

        # Encode payload and generate checksum
        json_payload = json.dumps(payload)
        base64_payload = base64.b64encode(json_payload.encode("utf-8")).decode("utf-8")
        endpoint = "/pg/v1/pay"
        signature_string = base64_payload + endpoint + salt_key
        checksum = hashlib.sha256(signature_string.encode("utf-8")).hexdigest()
        x_verify = f"{checksum}###{salt_index}"

        # Set headers and make request
        headers = {"Content-Type": "application/json", "X-VERIFY": x_verify}
        base_url = BASE_URLS[env]

        response = requests.post(
            f"{base_url}{endpoint}",
            json={"request": base64_payload},
            headers=headers,
        )

        # Handle response
        if response.status_code == 200:
            data = response.json().get("data", {})
            pay_page_url = (
                data.get("instrumentResponse", {}).get("redirectInfo", {}).get("url")
            )

            # Save payment object
            with transaction.atomic():
                Payment.objects.create(
                    sponsor=sponsor,
                    amount=sponsor.amount,
                    transaction_id=unique_transaction_id,
                    status="Pending",
                )

            return Response({"pay_page_url": pay_page_url}, status=status.HTTP_200_OK)

        else:
            return Response(
                {
                    "error": "Failed to initiate payment",
                    "details": response.json(),
                },
                status=response.status_code,
            )


class PaymentCallbackView(APIView):
    def post(self, request):
        print(request.data)
        b64_payload = request.data.get("response")
        payload = json.loads(base64.b64decode(b64_payload).decode("utf-8"))

        if not payload:
            return Response(
                {"detail": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST
            )
        merchant_transaction_id = payload.get("data").get("merchantTransactionId")
        status = payload.get("code")

        try:
            payment = Payment.objects.get(transaction_id=merchant_transaction_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found!"}, status=404)
        sponsor = payment.sponsor
        payment.status = status

        if status == "PAYMENT_SUCCESS":
            sponsor.payment_success = True
            sponsor.save()
            payment.status = status
            payment.save()
            return Response(
                {"detail": "Payment successful!"}, status=status.HTTP_200_OK
            )
        else:
            payment.status = status
            payment.save()
            return Response(
                {"detail": "Payment failed!"}, status=status.HTTP_400_BAD_REQUEST
            )


class PaymentStatusView(APIView):
    def post(self, request):
        txnid = request.data.get("txnid")
        try:
            payment = Payment.objects.get(transaction_id=txnid)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found!"}, status=404)

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)
