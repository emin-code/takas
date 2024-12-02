import iyzipay
import json
from django.conf import settings

# İyzico API anahtarları
options = {
    'api_key': settings.IYZICO_API_KEY,
    'secret_key': settings.IYZICO_SECRET_KEY,
    'base_url': 'sandbox-api.iyzipay.com' if settings.DEBUG else 'api.iyzipay.com'
}

def create_payment_form(odeme, callback_url):
    buyer = {
        'id': str(odeme.esnaf.user.id),
        'name': odeme.esnaf.user.first_name,
        'surname': odeme.esnaf.user.last_name,
        'email': odeme.esnaf.user.email,
        'identityNumber': '11111111111',  # TC Kimlik No
        'registrationAddress': odeme.esnaf.adres,
        'city': 'Istanbul',  # Varsayılan şehir
        'country': 'Turkey',
        'ip': '85.34.78.112'  # Müşteri IP adresi
    }

    address = {
        'contactName': odeme.esnaf.firma_adi,
        'city': 'Istanbul',
        'country': 'Turkey',
        'address': odeme.esnaf.adres,
    }

    basket_items = [
        {
            'id': str(odeme.id),
            'name': f"{odeme.get_odeme_tipi_display()} Ödemesi",
            'category1': odeme.get_odeme_tipi_display(),
            'itemType': 'VIRTUAL',
            'price': str(odeme.tutar)
        }
    ]

    request = {
        'locale': 'tr',
        'conversationId': str(odeme.id),
        'price': str(odeme.tutar),
        'paidPrice': str(odeme.tutar),
        'currency': 'TRY',
        'basketId': str(odeme.id),
        'paymentGroup': 'PRODUCT',
        'callbackUrl': callback_url,
        'enabledInstallments': ['2', '3', '6', '9'],
        'buyer': buyer,
        'shippingAddress': address,
        'billingAddress': address,
        'basketItems': basket_items
    }

    checkout_form_initialize = iyzipay.CheckoutFormInitialize().create(request, options)
    return json.loads(checkout_form_initialize.read().decode('utf-8'))

def verify_payment(token):
    request = {
        'locale': 'tr',
        'conversationId': '123456789',
        'token': token
    }
    
    result = iyzipay.CheckoutForm().retrieve(request, options)
    return json.loads(result.read().decode('utf-8')) 