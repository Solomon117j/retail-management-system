import hashlib
import hmac
import requests
import urllib.parse
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class PayFastAPI:
    """PayFast API integration"""

    def __init__(self):
        self.merchant_id = settings.PAYFAST_MERCHANT_ID
        self.merchant_key = settings.PAYFAST_MERCHANT_KEY
        self.passphrase = settings.PAYFAST_PASSPHRASE
        self.environment = settings.PAYFAST_ENVIRONMENT

        if self.environment == 'sandbox':
            self.base_url = 'https://sandbox.payfast.co.za'
        else:
            self.base_url = 'https://www.payfast.co.za'

    def generate_signature(self, data):
        """Generate PayFast signature"""
        # Sort parameters alphabetically
        sorted_data = sorted(data.items())

        # Create signature string
        signature_string = '&'.join([f"{key}={value}" for key, value in sorted_data if value])

        # Add passphrase if provided
        if self.passphrase:
            signature_string += f"&passphrase={self.passphrase}"

        # Generate HMAC SHA256 signature
        signature = hmac.new(
            self.merchant_key.encode(),
            signature_string.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def create_payment_url(self, order, return_url=None, cancel_url=None, notify_url=None):
        """Create PayFast payment URL"""
        try:
            # Prepare payment data
            payment_data = {
                'merchant_id': self.merchant_id,
                'merchant_key': self.merchant_key,
                'amount': f"{order.total_amount:.2f}",
                'item_name': f"Order #{order.id}",
                'item_description': f"Payment for Order #{order.id}",
                'return_url': return_url or f"{settings.SITE_URL}{reverse('e_commerce:checkout_success')}",
                'cancel_url': cancel_url or f"{settings.SITE_URL}{reverse('e_commerce:cart')}",
                'notify_url': notify_url or f"{settings.SITE_URL}{reverse('e_commerce:payfast_notify')}",
                'email_address': order.customer.email if order.customer else order.guest_email,
                'name_first': order.customer.first_name if order.customer else order.guest_first_name,
                'name_last': order.customer.last_name if order.customer else order.guest_last_name,
                'm_payment_id': str(order.id),
                'custom_str1': str(order.id),  # Store order ID for reference
            }

            # Generate signature
            payment_data['signature'] = self.generate_signature(payment_data)

            # Build query string
            query_string = urllib.parse.urlencode(payment_data)

            # Return full payment URL
            return f"{self.base_url}/eng/process?{query_string}"

        except Exception as e:
            logger.error(f"Failed to create PayFast payment URL: {str(e)}")
            raise

    def verify_notification(self, post_data):
        """Verify PayFast ITN (Instant Transaction Notification)"""
        try:
            # Get signature from POST data
            received_signature = post_data.get('signature')

            # Remove signature from data for verification
            verification_data = {k: v for k, v in post_data.items() if k != 'signature'}

            # Generate expected signature
            expected_signature = self.generate_signature(verification_data)

            # Compare signatures
            if hmac.compare_digest(received_signature, expected_signature):
                return True
            else:
                logger.warning("PayFast signature verification failed")
                return False

        except Exception as e:
            logger.error(f"PayFast notification verification failed: {str(e)}")
            return False

    def process_payment_notification(self, post_data):
        """Process PayFast payment notification"""
        try:
            if not self.verify_notification(post_data):
                return {'status': 'invalid_signature'}

            payment_status = post_data.get('payment_status')
            order_id = post_data.get('custom_str1')
            amount = post_data.get('amount_gross')
            pf_payment_id = post_data.get('pf_payment_id')

            return {
                'status': 'valid',
                'payment_status': payment_status,
                'order_id': order_id,
                'amount': amount,
                'pf_payment_id': pf_payment_id,
                'data': post_data
            }

        except Exception as e:
            logger.error(f"Failed to process PayFast notification: {str(e)}")
            return {'status': 'error', 'error': str(e)}

def create_payfast_payment(order):
    """Create PayFast payment for an order"""
    api = PayFastAPI()
    payment_url = api.create_payment_url(order)

    return {
        'payment_url': payment_url,
        'status': 'pending'
    }

def process_payfast_notification(post_data):
    """Process PayFast payment notification"""
    api = PayFastAPI()
    return api.process_payment_notification(post_data)
