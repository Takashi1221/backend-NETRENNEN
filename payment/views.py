import json
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from decouple import config, Csv
import stripe


# 環境変数の読み込み
stripe.api_key = config('STRIPE_WEBHOOK_SECRET')

# Stripe WebHook
@csrf_exempt
def stripe_webhooks(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
        
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        print("Stripe決済されました！！！")
        payment_intent = event.data.object # contains a stripe.PaymentIntent
        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)
        
    elif event.type == 'invoice.payment_succeeded':
        print(event.data.object.customer_email)
        User = get_user_model()
        user = User.objects.get(email=event.data.object.customer_email)
        user.is_subscribed = True
        user.save()
        
    elif event.type == 'customer.subscription.deleted':
        print("サブスクが解約されました！！！")
        
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)