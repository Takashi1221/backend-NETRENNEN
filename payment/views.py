import json
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
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
    if event.type == 'checkout.session.completed':
        session = event.data.object
        customer_email = session.get('customer_email')
        subscription_id = session.get('subscription')
        
        if customer_email:
            try:
                User = get_user_model()
                user = User.objects.get(email=customer_email)
                user.is_subscribed = True
                user.subscription_id = subscription_id
                user.save()
                print(f"User {user.email} subscription updated successfully.")
            except User.DoesNotExist:
                print(f"User with email {customer_email} does not exist.")

        
    elif event.type == 'customer.subscription.deleted':
        session = event.data.object
        subscription_id = session.get('subscription')
        User = get_user_model()
        user = User.objects.get(subscription_id=subscription_id)
        user.is_subscribed = False
        user.subscription_id = ''
        user.save()
        print("サブスクが解約されました！！！")
        
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)
