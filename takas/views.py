from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import (
    IsletmeTuru, EsnafProfili, Urun, TakasTeklifi, Kategori, Mesaj,
    OneCikarmaSecenegi, UrunOneCikarma, ReklamAlani, Reklam, Odeme
)
from .forms import (
    UrunForm, TakasTeklifiForm, KayitFormu, MesajForm, ProfilDuzenlemeForm,
    UrunOneCikarmaForm, ReklamForm
)
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from .utils import create_payment_form, verify_payment
from decimal import Decimal
from datetime import datetime, timedelta

def anasayfa(request):
    kategoriler = Kategori.objects.filter(aktif=True).prefetch_related('alt_kategoriler')
    vitrin_urunleri = Urun.objects.filter(
        aktif=True,
        vitrin=True
    ).select_related('esnaf', 'kategori', 'marka').order_by('-olusturma_tarihi')[:8]
    
    son_urunler = Urun.objects.filter(
        aktif=True
    ).select_related('esnaf', 'kategori', 'marka').order_by('-olusturma_tarihi')[:8]
    
    context = {
        'kategoriler': kategoriler,
        'vitrin_urunleri': vitrin_urunleri,
        'son_urunler': son_urunler,
    }
    return render(request, 'takas/anasayfa.html', context)

@login_required
def urun_ekle(request):
    if request.method == 'POST':
        form = UrunForm(request.POST, request.FILES)
        if form.is_valid():
            urun = form.save(commit=False)
            urun.esnaf = request.user.esnafprofili
            urun.save()
            messages.success(request, 'Ürün başarıyla eklendi.')
            return redirect('takas:urunlerim')
    else:
        form = UrunForm()
    
    return render(request, 'takas/urun_form.html', {'form': form})

@login_required
def urunlerim(request):
    urunler = Urun.objects.filter(esnaf=request.user.esnafprofili)
    return render(request, 'takas/urunlerim.html', {'urunler': urunler})

def urun_detay(request, urun_id):
    urun = get_object_or_404(Urun, id=urun_id)
    
    # Aynı kategoriden benzer ürünleri al
    benzer_urunler = Urun.objects.filter(
        kategori=urun.kategori,
        aktif=True
    ).exclude(
        id=urun.id
    ).order_by('-olusturma_tarihi')[:4]
    
    context = {
        'urun': urun,
        'benzer_urunler': benzer_urunler,
    }
    return render(request, 'takas/urun_detay.html', context)

def isletme_turleri_urunleri(request, isletme_tur_id):
    isletme_tur = get_object_or_404(IsletmeTuru, id=isletme_tur_id)
    urunler = Urun.objects.filter(
        esnaf__isletme_turu=isletme_tur,
        aktif=True
    ).order_by('-olusturma_tarihi')
    
    context = {
        'isletme_tur': isletme_tur,
        'urunler': urunler,
    }
    return render(request, 'takas/isletme_turleri_urunleri.html', context)

def urun_ara(request):
    query = request.GET.get('q', '')
    if query:
        urunler = Urun.objects.filter(
            Q(ad__icontains=query) |
            Q(aciklama__icontains=query) |
            Q(esnaf__firma_adi__icontains=query),
            aktif=True
        ).order_by('-olusturma_tarihi')
    else:
        urunler = []
    
    context = {
        'urunler': urunler,
        'query': query,
    }
    return render(request, 'takas/urun_arama.html', context)

@login_required
def takas_teklifi_gonder(request, urun_id):
    istenen_urun = get_object_or_404(Urun, id=urun_id)
    
    # Giriş yapmamış kullanıcılar için bilgilendirme sayfası
    if not request.user.is_authenticated:
        context = {
            'istenen_urun': istenen_urun,
            'mesaj': 'Takas teklifi gönderebilmek için giriş yapmanız gerekiyor.',
            'giris_url': '/login/?next=/takas-teklifi/gonder/{}/'.format(urun_id)
        }
        return render(request, 'takas/takas_bilgi.html', context)
    
    # Esnaf profili kontrolü
    try:
        esnaf_profili = request.user.esnafprofili
    except EsnafProfili.DoesNotExist:
        context = {
            'istenen_urun': istenen_urun,
            'mesaj': 'Takas teklifi gönderebilmek için firma bilgilerinizi tamamlamanız gerekiyor.',
            'kayit_url': '/kayit/'
        }
        return render(request, 'takas/takas_bilgi.html', context)
    
    # Kendi ürününe teklif vermeyi engelle
    if istenen_urun.esnaf == request.user.esnafprofili:
        messages.error(request, 'Kendi ürününüze teklif veremezsiniz.')
        return redirect('takas:urun_detay', urun_id=urun_id)
    
    # Ürünün takas için uygun olup olmadığını kontrol et
    if istenen_urun.durum not in ['takas', 'her_ikisi']:
        messages.error(request, 'Bu ürün takas için uygun değil.')
        return redirect('takas:urun_detay', urun_id=urun_id)
    
    # Kullanıcının takas edilebilir ürünlerini kontrol et
    takas_edilebilir_urunler = Urun.objects.filter(
        esnaf=request.user.esnafprofili,
        aktif=True,
        durum__in=['takas', 'her_ikisi']
    )
    
    if not takas_edilebilir_urunler.exists():
        context = {
            'istenen_urun': istenen_urun,
            'mesaj': 'Takas teklifi yapabilmek için önce takas edilebilir bir ürün eklemelisiniz.',
            'urun_ekle_url': '/urun/ekle/'
        }
        return render(request, 'takas/takas_bilgi.html', context)
    
    if request.method == 'POST':
        form = TakasTeklifiForm(request.POST, user=request.user)
        if form.is_valid():
            teklif = form.save(commit=False)
            teklif.teklif_veren = request.user.esnafprofili
            teklif.teklif_alan = istenen_urun.esnaf
            teklif.istenen_urun = istenen_urun
            
            # Aynı ürün için daha önce bekleyen teklif var mı kontrol et
            mevcut_teklif = TakasTeklifi.objects.filter(
                teklif_veren=request.user.esnafprofili,
                istenen_urun=istenen_urun,
                durum='beklemede'
            ).first()
            
            if mevcut_teklif:
                messages.warning(request, 'Bu ürün için zaten bekleyen bir teklifiniz var.')
                return redirect('takas:urun_detay', urun_id=urun_id)
            
            teklif.save()
            messages.success(request, 'Takas teklifiniz başarıyla gönderildi. Karşı tarafın yanıtını bekleyin.')
            return redirect('takas:urun_detay', urun_id=urun_id)
    else:
        form = TakasTeklifiForm(user=request.user)
    
    context = {
        'form': form,
        'istenen_urun': istenen_urun,
    }
    return render(request, 'takas/takas_teklifi_form.html', context)

def kayit(request):
    if request.method == 'POST':
        form = KayitFormu(request.POST)
        if form.is_valid():
            user = form.save()
            EsnafProfili.objects.create(
                user=user,
                firma_adi=form.cleaned_data['firma_adi'],
                isletme_turu=form.cleaned_data['isletme_turu'],
                adres=form.cleaned_data['adres'],
                telefon=form.cleaned_data['telefon']
            )
            login(request, user)
            messages.success(request, 'Hesabınız başarıyla oluşturuldu.')
            return redirect('takas:anasayfa')
    else:
        form = KayitFormu()
    return render(request, 'takas/kayit.html', {'form': form})

def kategori_urunleri(request, kategori_id):
    kategori = get_object_or_404(Kategori, id=kategori_id, aktif=True)
    urunler = Urun.objects.filter(
        kategori=kategori,
        aktif=True
    ).select_related('esnaf', 'marka').order_by('-olusturma_tarihi')
    
    context = {
        'kategori': kategori,
        'urunler': urunler,
    }
    return render(request, 'takas/kategori_urunleri.html', context)

def cikis_yap(request):
    logout(request)
    return redirect('takas:anasayfa')

@login_required
def urun_durum_degistir(request, urun_id):
    urun = get_object_or_404(Urun, id=urun_id, esnaf=request.user.esnafprofili)
    
    if request.method == 'POST':
        yeni_durum = request.POST.get('durum')
        if yeni_durum == 'aktif':
            urun.aktif = True
            messages.success(request, 'Ürün başarıyla aktif hale getirildi.')
        elif yeni_durum == 'pasif':
            urun.aktif = False
            messages.success(request, 'Ürün başarıyla pasif hale getirildi.')
        urun.save()
    
    return redirect('takas:urunlerim')

@login_required
def mesaj_gonder(request, esnaf_id):
    alici = get_object_or_404(EsnafProfili, id=esnaf_id)
    
    if request.method == 'POST':
        form = MesajForm(request.POST)
        if form.is_valid():
            mesaj = form.save(commit=False)
            mesaj.gonderen = request.user.esnafprofili
            mesaj.alici = alici
            mesaj.save()
            messages.success(request, 'Mesajınız başarıyla gönderildi.')
            return redirect('takas:urun_detay', urun_id=request.POST.get('urun_id'))
    else:
        form = MesajForm()
    
    context = {
        'form': form,
        'alici': alici,
        'urun_id': request.GET.get('urun_id')
    }
    return render(request, 'takas/mesaj_form.html', context)

@login_required
def satin_al(request, urun_id):
    urun = get_object_or_404(Urun, id=urun_id)
    
    # Kendi ürününü satın almayı engelle
    if urun.esnaf == request.user.esnafprofili:
        messages.error(request, 'Kendi ürününüzü satın alamazsınız.')
        return redirect('takas:urun_detay', urun_id=urun_id)
    
    # Ürünün satış için uygun olup olmadığını kontrol et
    if urun.durum not in ['satis', 'her_ikisi']:
        messages.error(request, 'Bu ürün satış için uygun değil.')
        return redirect('takas:urun_detay', urun_id=urun_id)
    
    # Ürünün fiyatı yoksa satın alınamaz
    if not urun.fiyat:
        messages.error(request, 'Bu ürünün fiyatı belirtilmemiş.')
        return redirect('takas:urun_detay', urun_id=urun_id)
    
    context = {
        'urun': urun,
        'mesaj': 'Satın alma işlemi için satıcı ile iletişime geçin.',
        'iletisim_bilgileri': {
            'firma': urun.esnaf.firma_adi,
            'telefon': urun.esnaf.telefon,
            'adres': urun.esnaf.adres,
            'whatsapp': urun.esnaf.whatsapp if urun.esnaf.whatsapp else None
        }
    }
    return render(request, 'takas/satin_al.html', context)

@login_required
def takas_teklifleri(request):
    # Esnaf profili kontrolü
    try:
        esnaf_profili = request.user.esnafprofili
    except EsnafProfili.DoesNotExist:
        messages.warning(request, 'Takas tekliflerini görüntüleyebilmek için önce firma bilgilerinizi tamamlamanız gerekiyor. Lütfen kayıt formunu doldurun.')
        return redirect('takas:kayit')
    
    # Gelen teklifler
    alinan_teklifler = TakasTeklifi.objects.filter(
        teklif_alan=esnaf_profili
    ).select_related(
        'teklif_veren', 'verilen_urun', 'istenen_urun'
    ).order_by('-olusturma_tarihi')
    
    # Gönderilen teklifler
    gonderilen_teklifler = TakasTeklifi.objects.filter(
        teklif_veren=esnaf_profili
    ).select_related(
        'teklif_alan', 'verilen_urun', 'istenen_urun'
    ).order_by('-olusturma_tarihi')
    
    context = {
        'alinan_teklifler': alinan_teklifler,
        'gonderilen_teklifler': gonderilen_teklifler,
    }
    return render(request, 'takas/takas_teklifleri.html', context)

@login_required
def takas_teklifi_durum_degistir(request, teklif_id):
    teklif = get_object_or_404(TakasTeklifi, id=teklif_id, teklif_alan=request.user.esnafprofili)
    
    if request.method == 'POST':
        yeni_durum = request.POST.get('durum')
        if yeni_durum in ['kabul_edildi', 'reddedildi']:
            teklif.durum = yeni_durum
            teklif.save()
            
            if yeni_durum == 'kabul_edildi':
                messages.success(request, 'Takas teklifi kabul edildi. Teklifi gönderen kişi ile iletişime geçebilirsiniz.')
            else:
                messages.info(request, 'Takas teklifi reddedildi.')
                
    return redirect('takas:takas_teklifleri')

@login_required
def mesajlar(request):
    # Esnaf profili kontrolü
    try:
        esnaf_profili = request.user.esnafprofili
    except EsnafProfili.DoesNotExist:
        messages.warning(request, 'Mesajlarınızı görüntüleyebilmek için önce firma bilgilerinizi tamamlamanız gerekiyor. Lütfen kayıt formunu doldurun.')
        return redirect('takas:kayit')
    
    # Gelen mesajlar
    alinan_mesajlar = Mesaj.objects.filter(
        alici=esnaf_profili
    ).select_related('gonderen', 'alici').order_by('-olusturma_tarihi')
    
    # Gönderilen mesajlar
    gonderilen_mesajlar = Mesaj.objects.filter(
        gonderen=esnaf_profili
    ).select_related('gonderen', 'alici').order_by('-olusturma_tarihi')
    
    # Okunmamış mesaj sayısı
    okunmamis_mesaj_sayisi = alinan_mesajlar.filter(okundu=False).count()
    
    context = {
        'alinan_mesajlar': alinan_mesajlar,
        'gonderilen_mesajlar': gonderilen_mesajlar,
        'okunmamis_mesaj_sayisi': okunmamis_mesaj_sayisi,
    }
    return render(request, 'takas/mesajlar.html', context)

@login_required
def mesaj_okundu_isaretle(request, mesaj_id):
    mesaj = get_object_or_404(Mesaj, id=mesaj_id, alici=request.user.esnafprofili)
    mesaj.okundu = True
    mesaj.save()
    return redirect('takas:mesajlar')

@login_required
def profil_goruntule(request):
    esnaf = request.user.esnafprofili
    urunler = Urun.objects.filter(esnaf=esnaf)
    
    # Aktif reklamlar ve öne çıkarılan ürünler
    reklamlar = Reklam.objects.filter(esnaf=esnaf).order_by('-baslangic_tarihi')
    one_cikanlar = UrunOneCikarma.objects.filter(urun__esnaf=esnaf).order_by('-baslangic_tarihi')
    
    return render(request, 'takas/profil.html', {
        'esnaf': esnaf,
        'urunler': urunler,
        'reklamlar': reklamlar,
        'one_cikanlar': one_cikanlar,
    })

@login_required
def profil_duzenle(request):
    try:
        profil = request.user.esnafprofili
    except EsnafProfili.DoesNotExist:
        messages.warning(request, 'Profil bilgilerinizi düzenleyebilmek için önce firma bilgilerinizi tamamlamanız gerekiyor.')
        return redirect('takas:kayit')
    
    if request.method == 'POST':
        form = ProfilDuzenlemeForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil bilgileriniz başarıyla güncellendi.')
            return redirect('takas:profil')
    else:
        form = ProfilDuzenlemeForm(instance=profil)
    
    context = {
        'form': form,
        'profil': profil
    }
    return render(request, 'takas/profil_duzenle.html', context)

def urun_sil(request, urun_id):
    # Admin veya ürün sahibi kontrolü
    urun = get_object_or_404(Urun, id=urun_id)
    
    # Admin veya ürün sahibi değilse reddet
    if not (request.user.is_staff or (hasattr(request.user, 'esnafprofili') and urun.esnaf == request.user.esnafprofili)):
        messages.error(request, 'Bu işlem için yetkiniz bulunmuyor.')
        return redirect('takas:urun_detay', urun_id=urun_id)
    
    if request.method == 'POST':
        # Admin silme işlemi ise kullanıcıya bildirim gönder
        if request.user.is_staff and urun.esnaf != getattr(request.user, 'esnafprofili', None):
            Mesaj.objects.create(
                gonderen=None,  # Sistem mesajı
                alici=urun.esnaf,
                konu='Ürününüz Kaldırıldı',
                icerik=f'"{urun.ad}" isimli ürününüz yönetici tarafından kaldırılmıştır. Lütfen ürün paylaşım kurallarımıza uygun paylaşım yapınız.'
            )
            messages.success(request, 'Ürün başarıyla silindi ve kullanıcıya bildirim gönderildi.')
        else:
            messages.success(request, 'Ürün başarıyla silindi.')
        
        urun.delete()
        
        # Admin panelinden silme işlemi yapıldıysa admin paneline yönlendir
        if request.user.is_staff and request.META.get('HTTP_REFERER', '').endswith('/admin/'):
            return redirect('admin:takas_urun_changelist')
            
        return redirect('takas:urunlerim')
        
    return redirect('takas:urun_detay', urun_id=urun_id)

@login_required
def urun_one_cikar(request, urun_id):
    urun = get_object_or_404(Urun, id=urun_id, esnaf=request.user.esnafprofili)
    
    if request.method == 'POST':
        form = UrunOneCikarmaForm(request.POST)
        if form.is_valid():
            secenek = form.cleaned_data['secenek']
            
            # Öne çıkarma kaydı oluştur
            one_cikarma = form.save(commit=False)
            one_cikarma.urun = urun
            one_cikarma.bitis_tarihi = datetime.now() + timedelta(days=secenek.sure_gun)
            one_cikarma.aktif = False  # Ödeme onaylanana kadar aktif değil
            one_cikarma.save()
            
            # Ödeme kaydı oluştur
            odeme = Odeme.objects.create(
                esnaf=request.user.esnafprofili,
                odeme_tipi='one_cikarma',
                tutar=secenek.fiyat,
                urun_one_cikarma=one_cikarma,
                durum='bekliyor'
            )
            
            messages.success(request, 'Ödeme bilgileri e-posta adresinize gönderildi. Ödemeniz onaylandıktan sonra ürününüz öne çıkarılacaktır.')
            return redirect('takas:odeme_bilgi', odeme_id=odeme.id)
    else:
        form = UrunOneCikarmaForm()
    
    return render(request, 'takas/urun_one_cikar.html', {
        'form': form,
        'urun': urun
    })

@login_required
def reklam_ver(request):
    if request.method == 'POST':
        form = ReklamForm(request.POST, request.FILES)
        if form.is_valid():
            reklam = form.save(commit=False)
            reklam.esnaf = request.user.esnafprofili
            reklam.aktif = False  # Ödeme onaylanana kadar aktif değil
            
            # Toplam tutarı hesapla
            gunluk_ucret = reklam.reklam_alani.gunluk_ucret
            gun_sayisi = form.cleaned_data['sure']
            toplam_tutar = gunluk_ucret * Decimal(gun_sayisi)
            
            reklam.save()
            
            # Ödeme kaydı oluştur
            odeme = Odeme.objects.create(
                esnaf=request.user.esnafprofili,
                odeme_tipi='reklam',
                tutar=toplam_tutar,
                reklam=reklam,
                durum='bekliyor'
            )
            
            messages.success(request, 'Ödeme bilgileri e-posta adresinize gönderildi. Ödemeniz onaylandıktan sonra reklamınız yayınlanacaktır.')
            return redirect('takas:odeme_bilgi', odeme_id=odeme.id)
    else:
        form = ReklamForm()
    
    return render(request, 'takas/reklam_ver.html', {
        'form': form
    })

@login_required
def odeme_bilgi(request, odeme_id):
    odeme = get_object_or_404(Odeme, id=odeme_id, esnaf=request.user.esnafprofili)
    return render(request, 'takas/odeme_bilgi.html', {
        'odeme': odeme,
        'banka_bilgileri': {
            'banka_adi': 'Ziraat Bankası',
            'hesap_sahibi': 'TakasOnline Ltd. Şti.',
            'iban': 'TR00 0000 0000 0000 0000 0000 00',
            'aciklama': f'TAKAS-{odeme.id}'
        }
    })