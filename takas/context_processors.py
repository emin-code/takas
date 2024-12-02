from .models import Mesaj
from django.db.models import ObjectDoesNotExist

def okunmamis_mesaj_sayisi(request):
    if request.user.is_authenticated:
        try:
            sayisi = Mesaj.objects.filter(
                alici=request.user.esnafprofili,
                okundu=False
            ).count()
            return {'okunmamis_mesaj_sayisi': sayisi}
        except (ObjectDoesNotExist, AttributeError):
            return {'okunmamis_mesaj_sayisi': 0}
    return {'okunmamis_mesaj_sayisi': 0} 