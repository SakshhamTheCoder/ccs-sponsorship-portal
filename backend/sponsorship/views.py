from .serializers import SponsorshipSerializer
from .models import Sponsor
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
class SponsorshipAddView(APIView):
    def post(self, request):
        name = request.data.get("name")
        company_name = request.data.get("company_name")
        email = request.data.get("email")
        contact = request.data.get("contact")
        amount = request.data.get("amount")
        event = request.data.get("event")

        if (
            not name
            or not company_name
            or not email
            or not contact
            or not amount
            or not event
        ):
            return Response({"error": "All fields are required!"}, status=400)

        sponsor = Sponsor.objects.create(
            name=name,
            company_name=company_name,
            email=email,
            contact=contact,
            amount=amount,
            event=event,
        )

        sponsor.save()

        return Response(SponsorshipSerializer(sponsor).data)
