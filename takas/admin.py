from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from .models import (
    IsletmeTuru, EsnafProfili, Urun, TakasTeklifi, Mesaj, Kategori, 
    AltKategori, Marka, OneCikarmaSecenegi, UrunOneCikarma, ReklamAlani, Reklam, Odeme
)

@admin.register(EsnafProfili)
class EsnafProfiliAdmin(admin.ModelAdmin):
    list_display = ('firma_adi', 'isletme_turu', 'telefon', 'teslimat_secenegi', 'aktif')
    list_filter = ('isletme_turu', 'teslimat_secenegi', 'aktif')
    search_fields = ('firma_adi', 'user__username', 'vergi_no')
    actions = ['toplu_kullanici_sil']
    list_per_page = 20

    def has_delete_permission(self, request, obj=None):
        return True

    def delete_model(self, request, obj):
        if obj.user:
            # Kullanıcının tüm verilerini sil
            Urun.objects.filter(esnaf=obj).delete()
            TakasTeklifi.objects.filter(teklif_veren=obj).delete()
            TakasTeklifi.objects.filter(teklif_alan=obj).delete()
            Mesaj.objects.filter(gonderen=obj).delete()
            Mesaj.objects.filter(alici=obj).delete()
            # Kullanıcı ve profilini sil
            user = obj.user
            obj.delete()
            user.delete()

    def toplu_kullanici_sil(self, request, queryset):
        for profil in queryset:
            self.delete_model(request, profil)
        self.message_user(request, f'{queryset.count()} kullanıcı başarıyla silindi.')
    toplu_kullanici_sil.short_description = 'Seçili kullanıcıları sil'

@admin.register(Urun)
class UrunAdmin(admin.ModelAdmin):
    list_display = ('ad', 'esnaf', 'kategori', 'marka', 'fiyat', 'miktar', 'birim', 'durum', 'vitrin', 'aktif')
    list_filter = ('kategori', 'alt_kategori', 'marka', 'durum', 'vitrin', 'aktif', 'esnaf__isletme_turu')
    search_fields = ('ad', 'esnaf__firma_adi', 'marka__ad')
    ordering = ['-olusturma_tarihi']
    actions = ['toplu_urun_sil']
    list_per_page = 20

    def has_delete_permission(self, request, obj=None):
        return True

    def toplu_urun_sil(self, request, queryset):
        silinecek_sayisi = queryset.count()
        queryset.delete()
        self.message_user(request, f'{silinecek_sayisi} ürün başarıyla silindi.')
    toplu_urun_sil.short_description = 'Seçili ürünleri sil'

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('ad', 'sira', 'aktif')
    list_filter = ('aktif',)
    search_fields = ('ad',)
    ordering = ['sira', 'ad']
    list_per_page = 20

@admin.register(AltKategori)
class AltKategoriAdmin(admin.ModelAdmin):
    list_display = ('kategori', 'ad', 'sira', 'aktif')
    list_filter = ('kategori', 'aktif')
    search_fields = ('ad', 'kategori__ad')
    ordering = ['kategori', 'sira', 'ad']
    list_per_page = 20

@admin.register(Marka)
class MarkaAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aktif')
    list_filter = ('aktif',)
    search_fields = ('ad',)
    list_per_page = 20

@admin.register(IsletmeTuru)
class IsletmeTuruAdmin(admin.ModelAdmin):
    list_display = ('ad', 'minimum_siparis_tutari', 'aktif')
    list_filter = ('aktif',)
    search_fields = ('ad',)
    list_per_page = 20

@admin.register(TakasTeklifi)
class TakasTeklifiAdmin(admin.ModelAdmin):
    list_display = ('teklif_veren', 'teklif_alan', 'durum', 'olusturma_tarihi')
    list_filter = ('durum',)
    search_fields = ('teklif_veren__firma_adi', 'teklif_alan__firma_adi')
    list_per_page = 20

@admin.register(Mesaj)
class MesajAdmin(admin.ModelAdmin):
    list_display = ('gonderen', 'alici', 'konu', 'okundu', 'olusturma_tarihi')
    list_filter = ('okundu',)
    search_fields = ('konu', 'icerik', 'gonderen__firma_adi', 'alici__firma_adi')
    list_per_page = 20

@admin.register(OneCikarmaSecenegi)
class OneCikarmaSecenegiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'konum', 'sure_gun', 'fiyat', 'aktif')
    list_filter = ('konum', 'aktif')
    search_fields = ('ad',)

@admin.register(UrunOneCikarma)
class UrunOneCikarmaAdmin(admin.ModelAdmin):
    list_display = ('urun', 'secenek', 'baslangic_tarihi', 'bitis_tarihi', 'aktif', 'odeme_durumu')
    list_filter = ('aktif', 'odeme_durumu')
    search_fields = ('urun__ad', 'urun__esnaf__firma_adi')
    date_hierarchy = 'baslangic_tarihi'

@admin.register(ReklamAlani)
class ReklamAlaniAdmin(admin.ModelAdmin):
    list_display = ('ad', 'konum', 'boyut', 'gunluk_ucret', 'aktif')
    list_filter = ('konum', 'aktif')
    search_fields = ('ad',)

@admin.register(Reklam)
class ReklamAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'esnaf', 'reklam_alani', 'baslangic_tarihi', 'bitis_tarihi', 'aktif', 'odeme_durumu')
    list_filter = ('aktif', 'odeme_durumu', 'reklam_alani')
    search_fields = ('baslik', 'esnaf__firma_adi')
    date_hierarchy = 'baslangic_tarihi'

@admin.register(Odeme)
class OdemeAdmin(admin.ModelAdmin):
    list_display = ('esnaf', 'odeme_tipi', 'tutar', 'durum', 'olusturma_tarihi')
    list_filter = ('odeme_tipi', 'durum')
    search_fields = ('esnaf__firma_adi',)
    date_hierarchy = 'olusturma_tarihi'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Ödeme onaylandığında ilgili kaydı aktifleştir
        if obj.durum == 'onaylandi':
            if obj.urun_one_cikarma:
                obj.urun_one_cikarma.aktif = True
                obj.urun_one_cikarma.odeme_durumu = 'onaylandi'
                obj.urun_one_cikarma.save()
            elif obj.reklam:
                obj.reklam.aktif = True
                obj.reklam.odeme_durumu = 'onaylandi'
                obj.reklam.save()
    
    def has_add_permission(self, request):
        return False  # Ödemeler sadece sistem tarafından oluşturulabilir 