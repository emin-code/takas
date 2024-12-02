from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
from django.core.files import File

class Kategori(models.Model):
    ad = models.CharField(max_length=100, verbose_name='Kategori Adı')
    aciklama = models.TextField(blank=True, verbose_name='Açıklama')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Font Awesome İkon Kodu')
    resim = models.ImageField(upload_to='kategori_resimleri/', blank=True, verbose_name='Kategori Resmi')
    sira = models.PositiveIntegerField(default=0, verbose_name='Sıralama')
    aktif = models.BooleanField(default=True, verbose_name='Aktif mi?')

    def __str__(self):
        return self.ad

    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        ordering = ['sira', 'ad']

class AltKategori(models.Model):
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE, related_name='alt_kategoriler', verbose_name='Ana Kategori')
    ad = models.CharField(max_length=100, verbose_name='Alt Kategori Adı')
    aciklama = models.TextField(blank=True, verbose_name='Açıklama')
    resim = models.ImageField(upload_to='altkategori_resimleri/', blank=True, verbose_name='Alt Kategori Resmi')
    sira = models.PositiveIntegerField(default=0, verbose_name='Sıralama')
    aktif = models.BooleanField(default=True, verbose_name='Aktif mi?')

    def __str__(self):
        return f"{self.kategori.ad} - {self.ad}"

    class Meta:
        verbose_name = 'Alt Kategori'
        verbose_name_plural = 'Alt Kategoriler'
        ordering = ['kategori', 'sira', 'ad']

class Marka(models.Model):
    ad = models.CharField(max_length=100, verbose_name='Marka Adı')
    aciklama = models.TextField(blank=True, verbose_name='Açıklama')
    logo = models.ImageField(upload_to='marka_logolari/', blank=True, verbose_name='Marka Logosu')
    aktif = models.BooleanField(default=True, verbose_name='Aktif mi?')

    def __str__(self):
        return self.ad

    class Meta:
        verbose_name = 'Marka'
        verbose_name_plural = 'Markalar'
        ordering = ['ad']

class IsletmeTuru(models.Model):
    ad = models.CharField(max_length=100, verbose_name='İşletme Türü')
    aciklama = models.TextField(blank=True, verbose_name='Açıklama')
    minimum_siparis_tutari = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Minimum Sipariş Tutarı (TL)')
    aktif = models.BooleanField(default=True, verbose_name='Aktif mi?')

    def __str__(self):
        return self.ad
    
    class Meta:
        verbose_name = 'İşletme Türü'
        verbose_name_plural = 'İşletme Türleri'

class EsnafProfili(models.Model):
    TESLIMAT_SECENEKLERI = [
        ('kendim', 'Kendim Teslim Ediyorum'),
        ('anlasmali', 'Anlaşmalı Kargo'),
        ('her_ikisi', 'Her İkisi de'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    isletme_turu = models.ForeignKey(IsletmeTuru, on_delete=models.SET_NULL, null=True, verbose_name='İşletme Türü')
    firma_adi = models.CharField(max_length=200, verbose_name='Firma Adı')
    logo = models.ImageField(upload_to='firma_logolari/', blank=True, verbose_name='Firma Logosu')
    adres = models.TextField(verbose_name='Adres')
    telefon = models.CharField(max_length=20, verbose_name='Telefon')
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name='WhatsApp')
    vergi_no = models.CharField(max_length=50, blank=True, verbose_name='Vergi No')
    vergi_dairesi = models.CharField(max_length=100, blank=True, verbose_name='Vergi Dairesi')
    teslimat_secenegi = models.CharField(
        max_length=20,
        choices=TESLIMAT_SECENEKLERI,
        default='kendim',
        verbose_name='Teslimat Seçeneği'
    )
    minimum_siparis_tutari = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Minimum Sipariş Tutarı (TL)'
    )
    aktif = models.BooleanField(default=True, verbose_name='Aktif mi?')
    
    def __str__(self):
        return self.firma_adi

    class Meta:
        verbose_name = 'İşletme Profili'
        verbose_name_plural = 'İşletme Profilleri'

class Urun(models.Model):
    DURUM_SECENEKLERI = [
        ('takas', 'Sadece Takas'),
        ('satis', 'Sadece Satış'),
        ('her_ikisi', 'Hem Takas Hem Satış'),
    ]

    STOK_BIRIMI = [
        ('adet', 'Adet'),
        ('kg', 'Kilogram'),
        ('gr', 'Gram'),
        ('lt', 'Litre'),
        ('paket', 'Paket'),
        ('koli', 'Koli'),
    ]
    
    ilan_no = models.CharField(max_length=10, unique=True, editable=False, null=True, blank=True, verbose_name='İlan No')
    esnaf = models.ForeignKey(EsnafProfili, on_delete=models.CASCADE)
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True, verbose_name='Ana Kategori')
    alt_kategori = models.ForeignKey(AltKategori, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Alt Kategori')
    marka = models.ForeignKey(Marka, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Marka')
    ad = models.CharField(max_length=200, verbose_name='Ürün Adı')
    aciklama = models.TextField(verbose_name='Açıklama')
    resim = models.ImageField(upload_to='urun_resimleri/', blank=True, verbose_name='Ürün Resmi')
    miktar = models.PositiveIntegerField(verbose_name='Stok Miktarı')
    birim = models.CharField(max_length=50, choices=STOK_BIRIMI, default='adet', verbose_name='Birim')
    fiyat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Satış Fiyatı (TL)')
    minimum_siparis_miktari = models.PositiveIntegerField(default=1, verbose_name='Minimum Sipariş Miktarı')
    kdv_orani = models.PositiveIntegerField(default=18, verbose_name='KDV Oranı (%)')
    durum = models.CharField(
        max_length=20, 
        choices=DURUM_SECENEKLERI, 
        default='satis',
        verbose_name='İşlem Türü'
    )
    aktif = models.BooleanField(default=True, verbose_name='Aktif mi?')
    vitrin = models.BooleanField(default=False, verbose_name='Vitrinde Göster')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturma Tarihi')
    guncelleme_tarihi = models.DateTimeField(auto_now=True, verbose_name='Güncelleme Tarihi')
    
    def __str__(self):
        return f"{self.ad} - {self.esnaf.firma_adi}"

    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        ordering = ['-olusturma_tarihi']

    def save(self, *args, **kwargs):
        if not self.ilan_no:
            # Son ilan numarasını bul
            son_ilan = Urun.objects.order_by('-ilan_no').first()
            if son_ilan:
                try:
                    son_no = int(son_ilan.ilan_no)
                    yeni_no = son_no + 1
                except ValueError:
                    yeni_no = 1000001
            else:
                yeni_no = 1000001
            
            self.ilan_no = str(yeni_no)
        
        super().save(*args, **kwargs)
        
        if self.resim:
            img = Image.open(self.resim.path)
            
            # En boy oranını koru
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                
                # JPEG kalitesini düşür
                output = BytesIO()
                img = img.convert('RGB')
                img.save(output, format='JPEG', quality=70, optimize=True)
                output.seek(0)
                
                # Dosyayı kaydet
                self.resim = File(output, name=self.resim.name)
                super().save(*args, **kwargs)

class TakasTeklifi(models.Model):
    DURUM_SECENEKLERI = [
        ('beklemede', 'Beklemede'),
        ('kabul_edildi', 'Kabul Edildi'),
        ('reddedildi', 'Reddedildi'),
    ]
    
    teklif_veren = models.ForeignKey(EsnafProfili, on_delete=models.CASCADE, related_name='verilen_teklifler')
    teklif_alan = models.ForeignKey(EsnafProfili, on_delete=models.CASCADE, related_name='alinan_teklifler')
    verilen_urun = models.ForeignKey(Urun, on_delete=models.CASCADE, related_name='verilen_urun')
    istenen_urun = models.ForeignKey(Urun, on_delete=models.CASCADE, related_name='istenen_urun')
    durum = models.CharField(max_length=20, choices=DURUM_SECENEKLERI, default='beklemede')
    mesaj = models.TextField(blank=True)
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.teklif_veren.firma_adi} -> {self.teklif_alan.firma_adi}"

    class Meta:
        verbose_name = 'Takas Teklifi'
        verbose_name_plural = 'Takas Teklifleri'

class Mesaj(models.Model):
    gonderen = models.ForeignKey(EsnafProfili, on_delete=models.CASCADE, related_name='gonderilen_mesajlar')
    alici = models.ForeignKey(EsnafProfili, on_delete=models.CASCADE, related_name='alinan_mesajlar')
    konu = models.CharField(max_length=200)
    icerik = models.TextField()
    okundu = models.BooleanField(default=False)
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.gonderen.firma_adi} -> {self.alici.firma_adi}: {self.konu}"

    class Meta:
        verbose_name = 'Mesaj'
        verbose_name_plural = 'Mesajlar'
        ordering = ['-olusturma_tarihi']
    
class OneCikarmaSecenegi(models.Model):
    KONUM_SECENEKLERI = [
        ('vitrin', 'Vitrin'),
        ('kategori_ust', 'Kategori Üstü'),
        ('anasayfa_ust', 'Anasayfa Üstü'),
    ]
    
    ad = models.CharField(max_length=100, verbose_name='Paket Adı')
    konum = models.CharField(max_length=20, choices=KONUM_SECENEKLERI, verbose_name='Konum')
    sure_gun = models.IntegerField(verbose_name='Süre (Gün)')
    fiyat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Fiyat (TL)')
    aciklama = models.TextField(blank=True, verbose_name='Açıklama')
    aktif = models.BooleanField(default=True, verbose_name='Aktif mi?')

    class Meta:
        verbose_name = 'Öne Çıkarma Seçeneği'
        verbose_name_plural = 'Öne Çıkarma Seçenekleri'
        ordering = ['fiyat']

    def __str__(self):
        return f"{self.ad} - {self.fiyat} TL"

class UrunOneCikarma(models.Model):
    ODEME_DURUMLARI = [
        ('bekliyor', 'Ödeme Bekliyor'),
        ('onaylandi', 'Onaylandı'),
        ('iptal', 'İptal Edildi'),
    ]
    
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE, related_name='one_cikarma_kayitlari')
    secenek = models.ForeignKey(OneCikarmaSecenegi, on_delete=models.CASCADE)
    baslangic_tarihi = models.DateTimeField(auto_now_add=True)
    bitis_tarihi = models.DateTimeField()
    aktif = models.BooleanField(default=False)
    odeme_durumu = models.CharField(max_length=20, choices=ODEME_DURUMLARI, default='bekliyor')

    class Meta:
        verbose_name = 'Ürün Öne Çıkarma'
        verbose_name_plural = 'Ürün Öne Çıkarma'

    def __str__(self):
        return f"{self.urun.ad} - {self.secenek.ad}"

class ReklamAlani(models.Model):
    KONUM_SECENEKLERI = [
        ('header', 'Üst Banner'),
        ('sidebar', 'Yan Banner'),
        ('footer', 'Alt Banner'),
        ('kategori', 'Kategori Sayfası'),
    ]
    
    ad = models.CharField(max_length=100)
    konum = models.CharField(max_length=20, choices=KONUM_SECENEKLERI)
    boyut = models.CharField(max_length=50)  # Örn: "728x90"
    gunluk_ucret = models.DecimalField(max_digits=10, decimal_places=2)
    aktif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.ad} ({self.boyut})"

    class Meta:
        verbose_name = 'Reklam Alanı'
        verbose_name_plural = 'Reklam Alanları'

class Reklam(models.Model):
    ODEME_DURUMLARI = [
        ('bekliyor', 'Ödeme Bekliyor'),
        ('onaylandi', 'Onaylandı'),
        ('iptal', 'İptal Edildi'),
    ]
    
    esnaf = models.ForeignKey(EsnafProfili, on_delete=models.CASCADE)
    reklam_alani = models.ForeignKey(ReklamAlani, on_delete=models.CASCADE)
    baslik = models.CharField(max_length=200)
    resim = models.ImageField(upload_to='reklam_resimleri/')
    link = models.URLField()
    baslangic_tarihi = models.DateTimeField(auto_now_add=True)
    bitis_tarihi = models.DateTimeField()
    aktif = models.BooleanField(default=False)
    odeme_durumu = models.CharField(max_length=20, choices=ODEME_DURUMLARI, default='bekliyor')
    
    def __str__(self):
        return f"{self.baslik} - {self.esnaf.firma_adi}"

    class Meta:
        verbose_name = 'Reklam'
        verbose_name_plural = 'Reklamlar'

class Odeme(models.Model):
    ODEME_TIPLERI = [
        ('one_cikarma', 'Öne Çıkarma'),
        ('reklam', 'Reklam'),
    ]
    
    ODEME_DURUMLARI = [
        ('bekliyor', 'Bekliyor'),
        ('onaylandi', 'Onaylandı'),
        ('iptal', 'İptal'),
    ]
    
    esnaf = models.ForeignKey(EsnafProfili, on_delete=models.CASCADE)
    odeme_tipi = models.CharField(max_length=20, choices=ODEME_TIPLERI)
    tutar = models.DecimalField(max_digits=10, decimal_places=2)
    durum = models.CharField(max_length=20, choices=ODEME_DURUMLARI, default='bekliyor')
    urun_one_cikarma = models.OneToOneField(UrunOneCikarma, on_delete=models.CASCADE, null=True, blank=True)
    reklam = models.OneToOneField(Reklam, on_delete=models.CASCADE, null=True, blank=True)
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_odeme_tipi_display()} - {self.esnaf.firma_adi} - {self.tutar} TL"

    class Meta:
        verbose_name = 'Ödeme'
        verbose_name_plural = 'Ödemeler'
    