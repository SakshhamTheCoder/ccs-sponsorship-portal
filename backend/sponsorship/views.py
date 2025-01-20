from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Sponsor
from .serializers import SponsorshipSerializer
from payments.models import Payment
from payments.serializers import PaymentSerializer
import uuid  # For generating transaction IDs


class SponsorshipAddView(APIView):
    def post(self, request):
        # Extract data from the request
        data = request.data
        name = data.get("name")
        company_name = data.get("company_name")
        email = data.get("email")
        contact = data.get("contact")
        amount = data.get("amount")
        event = data.get("event")

        # Validate fields
        if not all([name, company_name, email, contact, amount, event]):
            return Response({"error": "All fields are required!"}, status=400)

        try:
            # Create Sponsor entry
            sponsor = Sponsor.objects.create(
                name=name,
                company_name=company_name,
                email=email,
                contact=contact,
                amount=amount,
                event=event,
                payment_success=False,  # Default to False
            )

            # Create Payment entry with pending status
            payment = Payment.objects.create(
                sponsor=sponsor,
                amount=amount,
                transaction_id=str(uuid.uuid4()),  # Generate a unique transaction ID
                status="Pending",
            )

            # Return the Sponsor and Payment details
            return Response(
                {
                    "sponsor": SponsorshipSerializer(sponsor).data,
                    "payment": PaymentSerializer(payment).data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=500)
