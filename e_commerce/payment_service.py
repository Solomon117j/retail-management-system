import stripe
from django.conf import settings
from django.utils import timezone
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class PaymentService:
    """
    Stripe Payment Service for handling payment processing
    """

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.currency = settings.STRIPE_CURRENCY

    def create_payment_intent(self, order, payment_method_id=None):
        """
        Create a Stripe PaymentIntent for the order
        """
        try:
            # Convert amount to cents (Stripe expects integer amounts)
            amount_cents = int(order.total_amount * 100)

            payment_intent_data = {
                'amount': amount_cents,
                'currency': self.currency,
                'metadata': {
                    'order_id': str(order.id),
                    'customer_email': order.customer.email if order.customer else order.guest_email,
                },
                'description': f'Order #{order.id}',
                'automatic_payment_methods': {
                    'enabled': True,
                },
            }

            # Add payment method if provided
            if payment_method_id:
                payment_intent_data['payment_method'] = payment_method_id
                payment_intent_data['confirm'] = True
                payment_intent_data['return_url'] = f"{settings.SITE_URL}/e_commerce/orders/{order.id}/"

            payment_intent = stripe.PaymentIntent.create(**payment_intent_data)

            # Update order with payment intent ID
            order.payment_transaction_id = payment_intent.id
            order.payment_status = 'processing'
            order.save()

            logger.info(f"Created PaymentIntent {payment_intent.id} for order {order.id}")

            return {
                'success': True,
                'payment_intent': payment_intent,
                'client_secret': payment_intent.client_secret,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {e}")
            return {
                'success': False,
                'error': str(e),
            }
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            return {
                'success': False,
                'error': 'An unexpected error occurred',
            }

    def confirm_payment_intent(self, payment_intent_id):
        """
        Confirm a PaymentIntent
        """
        try:
            payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)

            return {
                'success': True,
                'payment_intent': payment_intent,
                'status': payment_intent.status,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error confirming payment intent: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    def retrieve_payment_intent(self, payment_intent_id):
        """
        Retrieve a PaymentIntent from Stripe
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'success': True,
                'payment_intent': payment_intent,
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment intent: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    def process_payment(self, order, payment_data):
        """
        Legacy method for backward compatibility - creates and confirms payment intent
        """
        try:
            # Create payment intent
            result = self.create_payment_intent(order)

            if not result['success']:
                return result

            payment_intent = result['payment_intent']

            # For immediate payment processing (not using Elements)
            if 'card_number' in payment_data:
                # Create payment method from card details
                payment_method = stripe.PaymentMethod.create(
                    type='card',
                    card={
                        'number': payment_data['card_number'],
                        'exp_month': payment_data['expiry_month'],
                        'exp_year': payment_data['expiry_year'],
                        'cvc': payment_data['cvv'],
                    },
                    billing_details={
                        'name': payment_data.get('card_holder_name', ''),
                        'email': order.customer.email if order.customer else order.guest_email,
                    },
                )

                # Confirm payment with the payment method
                payment_intent = stripe.PaymentIntent.confirm(
                    payment_intent.id,
                    payment_method=payment_method.id,
                )

            # Update order based on payment status
            if payment_intent.status == 'succeeded':
                order.payment_status = 'completed'
                order.payment_date = timezone.now()
                order.save()

                logger.info(f"Payment succeeded for order {order.id}")
                return {
                    'success': True,
                    'transaction_id': payment_intent.id,
                }

            elif payment_intent.status in ['requires_payment_method', 'requires_confirmation']:
                return {
                    'success': False,
                    'error': 'Payment requires additional action',
                }

            else:
                order.payment_status = 'failed'
                order.save()

                return {
                    'success': False,
                    'error': f'Payment {payment_intent.status}',
                }

        except stripe.error.CardError as e:
            logger.error(f"Card error: {e}")
            order.payment_status = 'failed'
            order.save()
            return {
                'success': False,
                'error': e.error.message,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            order.payment_status = 'failed'
            order.save()
            return {
                'success': False,
                'error': 'Payment processing failed',
            }

        except Exception as e:
            logger.error(f"Unexpected error in payment processing: {e}")
            order.payment_status = 'failed'
            order.save()
            return {
                'success': False,
                'error': 'An unexpected error occurred',
            }

    def process_refund(self, order, amount=None):
        """
        Process a refund for an order
        """
        try:
            if not order.payment_transaction_id:
                return {
                    'success': False,
                    'error': 'No payment transaction found',
                }

            refund_amount = amount or order.total_amount
            refund_cents = int(refund_amount * 100)

            refund = stripe.Refund.create(
                payment_intent=order.payment_transaction_id,
                amount=refund_cents,
                reason='requested_by_customer',
            )

            order.payment_status = 'refunded'
            order.save()

            logger.info(f"Refund processed for order {order.id}: {refund.id}")

            return {
                'success': True,
                'refund_id': refund.id,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe refund error: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    def handle_webhook(self, payload, sig_header):
        """
        Handle Stripe webhook events
        """
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )

            # Handle different event types
            if event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                self._handle_payment_succeeded(payment_intent)

            elif event.type == 'payment_intent.payment_failed':
                payment_intent = event.data.object
                self._handle_payment_failed(payment_intent)

            elif event.type == 'payment_intent.canceled':
                payment_intent = event.data.object
                self._handle_payment_canceled(payment_intent)

            return {'success': True}

        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return {'success': False, 'error': 'Invalid signature'}

        except Exception as e:
            logger.error(f"Webhook handling error: {e}")
            return {'success': False, 'error': str(e)}

    def _handle_payment_succeeded(self, payment_intent):
        """Handle successful payment webhook"""
        from .models import OnlineOrder

        order_id = payment_intent.metadata.get('order_id')
        if order_id:
            try:
                order = OnlineOrder.objects.get(id=order_id)
                order.payment_status = 'completed'
                order.payment_date = timezone.now()
                order.save()
                logger.info(f"Payment confirmed for order {order.id}")
            except OnlineOrder.DoesNotExist:
                logger.error(f"Order {order_id} not found for payment confirmation")

    def _handle_payment_failed(self, payment_intent):
        """Handle failed payment webhook"""
        from .models import OnlineOrder

        order_id = payment_intent.metadata.get('order_id')
        if order_id:
            try:
                order = OnlineOrder.objects.get(id=order_id)
                order.payment_status = 'failed'
                order.save()
                logger.info(f"Payment failed for order {order.id}")
            except OnlineOrder.DoesNotExist:
                logger.error(f"Order {order_id} not found for payment failure")

    def _handle_payment_canceled(self, payment_intent):
        """Handle canceled payment webhook"""
        from .models import OnlineOrder

        order_id = payment_intent.metadata.get('order_id')
        if order_id:
            try:
                order = OnlineOrder.objects.get(id=order_id)
                order.payment_status = 'cancelled'
                order.save()
                logger.info(f"Payment canceled for order {order.id}")
            except OnlineOrder.DoesNotExist:
                logger.error(f"Order {order_id} not found for payment cancellation")
