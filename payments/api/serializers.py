from rest_framework import serializers
from ..models import StudentPayment
class  StudentPaymentPostSerailizer(serializers.ModelSerializer):
     class Meta:
          model=StudentPayment
          fields=("fee_amount","fee_paid","fee_status","student")