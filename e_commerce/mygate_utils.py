import requests
import hashlib
import hmac
import json
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class MyGateAPI:
    """MyGate API integration"""

    def __init__(self):
        self.merchant_id = settings.MYGATE_MERCHANT_ID
        self.application_id = settings.MYGATE_APPLICATION_ID
        self.environment = settings.MYGATE_ENVIRONMENT

        if self.environment == 'sandbox':
            self.base_url = 'https://api.mygate.co.za/api/v1'
        else:
            self.base_url = 'https://api.mygate.co.za/api/v1'

    def generate_signature(self, data, secret_key):
        """Generate HMAC SHA256 signature"""
        # Sort parameters alphabetically
        sorted_keys = sorted(data.keys())

        # Create signature string
        signature_string = ''.join([str(data[key]) for key in sorted_keys])

        # Generate HMAC SHA256 signature
        signature = hmac.new(
            secret_key.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def create_payment(self, order, return_url=None, cancel_url=None):
        """Create MyGate payment"""
        try:
            # Prepare payment data
            payment_data = {
                'merchantId': self.merchant_id,
                'applicationId': self.application_id,
                'amount': str(order.total_amount),
                'currency': settings.PAYMENT_CURRENCY,
                'reference': str(order.id),
                'description': f"Payment for Order #{order.id}",
                'returnUrl': return_url or f"{settings.SITE_URL}{reverse('e_commerce:checkout_success')}",
                'cancelUrl': cancel_url or f"{settings.SITE_URL}{reverse('e_commerce:cart')}",
                'customer': {
                    'email': order.customer.email if order.customer else order.guest_email,
                    'firstName': order.customer.first_name if order.customer else order.guest_first_name,
                    'lastName': order.customer.last_name if order.customer else order.guest_last_name,
                }
            }

            # Add phone if available
            if order.customer and order.customer.phone:
                payment_data['customer']['phone'] = order.customer.phone
            elif order.guest_phone:
                payment_data['customer']['phone'] = order.guest_phone

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            url = f"{self.base_url}/payments"
            response = requests.post(url, headers=headers, json=payment_data)
            response.raise_for_status()

            data = response.json()

            return {
                'payment_id': data.get('id'),
                'payment_url': data.get('paymentUrl'),
                'status': 'pending'
            }

        except Exception as e:
            logger.error(f"Failed to create MyGate payment: {str(e)}")
            raise

    def check_payment_status(self, payment_id):
        """Check MyGate payment status"""
        try:
            url = f"{self.base_url}/payments/{payment_id}"
            headers = {
                'Accept': 'application/json'
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            return {
                'status': data.get('status'),
                'amount': data.get('amount'),
                'currency': data.get('currency'),
                'reference': data.get('reference'),
                'transaction_id': data.get('transactionId')
            }

        except Exception as e:
            logger.error(f"Failed to check MyGate payment status: {str(e)}")
            raise

    def process_webhook(self, webhook_data):
        """Process MyGate webhook notification"""
        try:
            # Verify webhook signature if secret is available
            # Note: MyGate webhook signature verification would require a secret key
            # This is a placeholder for signature verification

            event_type = webhook_data.get('eventType')
            payment_id = webhook_data.get('paymentId')
            status = webhook_data.get('status')
            order_reference = webhook_data.get('reference')

            return {
                'event_type': event_type,
                'payment_id': payment_id,
                'status': status,
                'order_reference': order_reference,
                'data': webhook_data
            }

        except Exception as e:
            logger.error(f"Failed to process MyGate webhook: {str(e)}")
            return {'status': 'error', 'error': str(e)}

def create_mygate_payment(order):
    """Create MyGate payment for an order"""
    api = MyGateAPI()
    result = api.create_payment(order)

    return result

def verify_mygate_payment(order, payment_id):
    """Verify MyGate payment status"""
    api = MyGateAPI()
    status_info = api.check_payment_status(payment_id)

    if status_info['status'] == 'COMPLETED':
        order.payment_status = 'completed'
        order.save()
        return True
    elif status_info['status'] == 'FAILED':
        order.payment_status = 'failed'
        order.save()
        return False

    return None  # Still pending

def process_mygate_webhook(webhook_data):
    """Process MyGate webhook notification"""
    api = MyGateAPI()
    return api.process_webhook(webhook_data)
