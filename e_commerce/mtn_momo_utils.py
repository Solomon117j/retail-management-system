import requests
import json
import uuid
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class MTNMoMoAPI:
    """MTN Mobile Money API integration"""

    def __init__(self):
        self.api_key = settings.MTN_MOMO_API_KEY
        self.api_secret = settings.MTN_MOMO_API_SECRET
        self.environment = settings.MTN_MOMO_ENVIRONMENT
        self.base_url = 'https://sandbox.momodeveloper.mtn.com' if self.environment == 'sandbox' else 'https://momodeveloper.mtn.com'
        self.access_token = None

    def get_access_token(self):
        """Get OAuth2 access token"""
        try:
            url = f"{self.base_url}/collection/token/"
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'Authorization': f'Basic {self.api_secret}',
                'Content-Type': 'application/json'
            }

            response = requests.post(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get('access_token')
            return self.access_token
        except Exception as e:
            logger.error(f"Failed to get MTN MoMo access token: {str(e)}")
            raise

    def request_to_pay(self, amount, currency, phone_number, order_id, description="Payment for order"):
        """Initiate a request to pay"""
        try:
            if not self.access_token:
                self.get_access_token()

            url = f"{self.base_url}/collection/v1_0/requesttopay"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Reference-Id': str(uuid.uuid4()),
                'X-Target-Environment': self.environment,
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': self.api_key
            }

            payload = {
                "amount": str(amount),
                "currency": currency,
                "externalId": str(order_id),
                "payer": {
                    "partyIdType": "MSISDN",
                    "partyId": phone_number
                },
                "payerMessage": description,
                "payeeNote": description
            }

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            return {
                'reference_id': headers['X-Reference-Id'],
                'status': 'pending'
            }
        except Exception as e:
            logger.error(f"Failed to initiate MTN MoMo payment: {str(e)}")
            raise

    def check_payment_status(self, reference_id):
        """Check the status of a payment request"""
        try:
            if not self.access_token:
                self.get_access_token()

            url = f"{self.base_url}/collection/v1_0/requesttopay/{reference_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Target-Environment': self.environment,
                'Ocp-Apim-Subscription-Key': self.api_key
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            return {
                'status': data.get('status'),
                'amount': data.get('amount'),
                'currency': data.get('currency'),
                'transaction_id': data.get('financialTransactionId')
            }
        except Exception as e:
            logger.error(f"Failed to check MTN MoMo payment status: {str(e)}")
            raise

def create_mtn_momo_payment(order):
    """Create MTN MoMo payment for an order"""
    api = MTNMoMoAPI()

    # Get phone number from customer or guest
    phone_number = None
    if order.customer:
        phone_number = order.customer.phone
    elif order.guest_phone:
        phone_number = order.guest_phone

    if not phone_number:
        raise ValueError("Phone number is required for MTN MoMo payment")

    # Format phone number (ensure it starts with country code)
    if not phone_number.startswith('+'):
        phone_number = f"+{phone_number}"

    result = api.request_to_pay(
        amount=order.total_amount,
        currency=settings.PAYMENT_CURRENCY,
        phone_number=phone_number,
        order_id=order.id,
        description=f"Payment for Order #{order.id}"
    )

    return result

def verify_mtn_momo_payment(order, reference_id):
    """Verify MTN MoMo payment status"""
    api = MTNMoMoAPI()
    status_info = api.check_payment_status(reference_id)

    if status_info['status'] == 'SUCCESSFUL':
        order.payment_status = 'completed'
        order.save()
        return True
    elif status_info['status'] == 'FAILED':
        order.payment_status = 'failed'
        order.save()
        return False

    return None  # Still pending
