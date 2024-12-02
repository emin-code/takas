from django.urls import path
from . import views

app_name = 'takas'

urlpatterns = [
    path('', views.anasayfa, name='anasayfa'),
    path('urun/ekle/', views.urun_ekle, name='urun_ekle'),
    path('urunlerim/', views.urunlerim, name='urunlerim'),
    path('urun/<int:urun_id>/', views.urun_detay, name='urun_detay'),
    path('kategori/<int:kategori_id>/', views.kategori_urunleri, name='kategori_urunleri'),
    path('urun/ara/', views.urun_ara, name='urun_ara'),
    path('takas-teklifi/gonder/<int:urun_id>/', views.takas_teklifi_gonder, name='takas_teklifi_gonder'),
    path('takas-teklifleri/', views.takas_teklifleri, name='takas_teklifleri'),
    path('takas-teklifi/<int:teklif_id>/durum-degistir/', views.takas_teklifi_durum_degistir, name='takas_teklifi_durum_degistir'),
    path('mesajlar/', views.mesajlar, name='mesajlar'),
    path('mesaj/<int:mesaj_id>/okundu/', views.mesaj_okundu_isaretle, name='mesaj_okundu_isaretle'),
    path('satin-al/<int:urun_id>/', views.satin_al, name='satin_al'),
    path('kayit/', views.kayit, name='kayit'),
    path('cikis/', views.cikis_yap, name='cikis'),
    path('profil/', views.profil_goruntule, name='profil'),
    path('profil/duzenle/', views.profil_duzenle, name='profil_duzenle'),
    path('urun/<int:urun_id>/durum-degistir/', views.urun_durum_degistir, name='urun_durum_degistir'),
    path('mesaj/gonder/<int:esnaf_id>/', views.mesaj_gonder, name='mesaj_gonder'),
    path('urun/<int:urun_id>/sil/', views.urun_sil, name='urun_sil'),
    path('urun/<int:urun_id>/one-cikar/', views.urun_one_cikar, name='urun_one_cikar'),
    path('reklam-ver/', views.reklam_ver, name='reklam_ver'),
    path('odeme/<int:odeme_id>/bilgi/', views.odeme_bilgi, name='odeme_bilgi'),
] 