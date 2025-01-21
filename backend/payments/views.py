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
        merchant_id = settings.PHONEPE_MERCHANT_ID
        salt_key = settings.PHONEPE_SALT_KEY
        salt_index = 1
        env = "UAT"  # Set to "PROD" for production

        BASE_URLS = {
            "UAT": "https://api-preprod.phonepe.com/apis/pg-sandbox",
            "PROD": "https://api.phonepe.com/apis/hermes",
        }

        try:
            # Get sponsor object
            sponsor_id = request.data.get("sponsor_id")
            if not sponsor_id:
                return Response({"error": "Sponsor ID is required"}, status=400)

            sponsor = Sponsor.objects.get(id=sponsor_id)
        except Sponsor.DoesNotExist:
            return Response({"error": "Sponsor not found!"}, status=404)

        unique_transaction_id = f"{sponsor.id}_{int(time.time() * 1000)}"
        ui_redirect_url = f"{settings.PHONEPE_RETURN_URL}{unique_transaction_id}/"
        s2s_callback_url = settings.PHONEPE_CALLBACK_URL  # Ensure this is HTTPS

        amount = int(
            sponsor.amount * 100
        )  # Convert to smallest currency unit (e.g., paise)
        id_assigned_to_user_by_merchant = sponsor.id

        # Payment payload
        payload = {
            "merchantId": merchant_id,
            "merchantTransactionId": unique_transaction_id,
            "merchantUserId": id_assigned_to_user_by_merchant,
            "amount": amount,
            "redirectUrl": ui_redirect_url,
            "redirectMode": "REDIRECT",
            "callbackUrl": s2s_callback_url,
            "paymentInstrument": {"type": "PAY_PAGE"},
        }

        # Encode payload
        json_payload = json.dumps(payload)
        base64_payload = base64.b64encode(json_payload.encode("utf-8")).decode("utf-8")

        # Generate checksum
        endpoint = "/pg/v1/pay"
        signature_string = base64_payload + endpoint + salt_key
        checksum = hashlib.sha256(signature_string.encode("utf-8")).hexdigest()
        x_verify = f"{checksum}###{salt_index}"

        headers = {"Content-Type": "application/json", "X-VERIFY": x_verify}
        base_url = BASE_URLS[env]

        # Retry logic
        max_retries = 5
        retry_delay = 1  # Initial delay in seconds

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{base_url}{endpoint}",
                    json={"request": base64_payload},
                    headers=headers,
                )
                print(response.status_code)
                print(response.request.headers)

                # Successful response
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    pay_page_url = (
                        data.get("instrumentResponse", {})
                        .get("redirectInfo", {})
                        .get("url")
                    )

                    # Save payment object
                    with transaction.atomic():
                        Payment.objects.create(
                            sponsor=sponsor,
                            amount=amount,
                            transaction_id=unique_transaction_id,
                            status="Pending",
                        )

                    return Response(
                        {"pay_page_url": pay_page_url}, status=status.HTTP_200_OK
                    )

                # Handle rate limit
                if response.status_code == 429:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue

                # Log errors for debugging
                return Response(
                    {
                        "error": "Failed to initiate payment",
                        "details": response.json(),
                    },
                    status=response.status_code,
                )
            except requests.RequestException as e:
                return Response(
                    {"error": "Payment request failed", "details": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"error": "Payment initiation failed after retries"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PaymentCallbackView(APIView):
    def post(self, request):
        data = request.data
        transaction_id = data.get("merchantTransactionId")
        status = data.get("status")
        amount = data.get("amount")
        sponsor_id = data.get("merchantUserId")

        try:
            sponsor = Sponsor.objects.get(id=sponsor_id)
        except Sponsor.DoesNotExist:
            return Response({"error": "Sponsor not found!"}, status=404)

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found!"}, status=404)

        if status == "SUCCESS":
            sponsor.payment_success = True
            sponsor.save()
            payment.status = "Success"
            payment.save()
            return Response(
                {"detail": "Payment successful!"}, status=status.HTTP_200_OK
            )
        else:
            payment.status = "Failed"
            payment.save()
            return Response(
                {"detail": "Payment failed!"}, status=status.HTTP_400_BAD_REQUEST
            )
