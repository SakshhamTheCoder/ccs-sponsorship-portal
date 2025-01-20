from .serializers import PaymentSerializer
from .models import Payment
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
class PaymentAddView(APIView):
    def post(self, request):
        pass
