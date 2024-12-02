from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Urun, TakasTeklifi, EsnafProfili, IsletmeTuru, Kategori, Marka, Mesaj, UrunOneCikarma, Reklam
from datetime import datetime, timedelta

class UrunForm(forms.ModelForm):
    ad = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ürün adını girin'
        })
    )
    aciklama = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ürün özelliklerini ve detaylarını yazın'
        })
    )
    kategori = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    miktar = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1'
        })
    )
    birim = forms.ChoiceField(
        choices=Urun.STOK_BIRIMI,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    fiyat = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        })
    )
    durum = forms.ChoiceField(
        choices=Urun.DURUM_SECENEKLERI,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    resim = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kategori'].queryset = Kategori.objects.filter(aktif=True)

        # Alan etiketlerini Türkçeleştir
        self.fields['ad'].label = 'Ürün Adı'
        self.fields['aciklama'].label = 'Açıklama'
        self.fields['kategori'].label = 'Kategori'
        self.fields['miktar'].label = 'Miktar'
        self.fields['birim'].label = 'Birim'
        self.fields['fiyat'].label = 'Fiyat (TL)'
        self.fields['durum'].label = 'İşlem Türü'
        self.fields['resim'].label = 'Ürün Fotoğrafı'

    class Meta:
        model = Urun
        fields = ['ad', 'aciklama', 'kategori', 'miktar', 'birim', 'fiyat', 'durum', 'resim']

class TakasTeklifiForm(forms.ModelForm):
    verilen_urun = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Teklif Edeceğiniz Ürün',
        help_text='Takas etmek istediğiniz kendi ürününüzü seçin'
    )
    mesaj = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Karşı tarafa iletmek istediğiniz notları buraya yazabilirsiniz...'
        }),
        required=False,
        label='Notunuz (İsteğe Bağlı)'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['verilen_urun'].queryset = Urun.objects.filter(
                esnaf=user.esnafprofili,
                aktif=True,
                durum__in=['takas', 'her_ikisi']
            ).order_by('-olusturma_tarihi')
            
            # Eğer takas edilebilir ürün yoksa uyarı mesajı ekle
            if not self.fields['verilen_urun'].queryset.exists():
                self.fields['verilen_urun'].help_text = 'Takas edilebilir ürününüz bulunmuyor. Önce takas için ürün eklemelisiniz.'

    class Meta:
        model = TakasTeklifi
        fields = ['verilen_urun', 'mesaj']

class MesajForm(forms.ModelForm):
    konu = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mesaj konusu'
        })
    )
    icerik = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Mesajınızı yazın'
        })
    )

    class Meta:
        model = Mesaj
        fields = ['konu', 'icerik']

class ProfilDuzenlemeForm(forms.ModelForm):
    firma_adi = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    isletme_turu = forms.ModelChoiceField(
        queryset=IsletmeTuru.objects.filter(aktif=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    adres = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    telefon = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    whatsapp = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Örnek: +905xxxxxxxxx'
        })
    )
    vergi_no = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    vergi_dairesi = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = EsnafProfili
        fields = ['firma_adi', 'isletme_turu', 'adres', 'telefon', 'whatsapp', 'vergi_no', 'vergi_dairesi']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['firma_adi'].label = 'Firma Adı'
        self.fields['isletme_turu'].label = 'İşletme Türü'
        self.fields['adres'].label = 'Adres'
        self.fields['telefon'].label = 'Telefon'
        self.fields['whatsapp'].label = 'WhatsApp (İsteğe Bağlı)'
        self.fields['vergi_no'].label = 'Vergi No (İsteğe Bağlı)'
        self.fields['vergi_dairesi'].label = 'Vergi Dairesi (İsteğe Bağlı)'

class KayitFormu(UserCreationForm):
    firma_adi = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    isletme_turu = forms.ModelChoiceField(
        queryset=IsletmeTuru.objects.filter(aktif=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    adres = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    telefon = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'firma_adi', 'isletme_turu', 'adres', 'telefon')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Alan etiketlerini Türkçeleştir
        self.fields['username'].label = 'Kullanıcı Adı'
        self.fields['email'].label = 'E-posta'
        self.fields['password1'].label = 'Parola'
        self.fields['password2'].label = 'Parola (Tekrar)'
        self.fields['firma_adi'].label = 'Firma Adı'
        self.fields['isletme_turu'].label = 'İşletme Türü'
        self.fields['adres'].label = 'Adres'
        self.fields['telefon'].label = 'Telefon'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user 

class UrunOneCikarmaForm(forms.ModelForm):
    class Meta:
        model = UrunOneCikarma
        fields = ['secenek']
        widgets = {
            'secenek': forms.RadioSelect(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['secenek'].label = 'Öne Çıkarma Paketi'
        self.fields['secenek'].empty_label = None
        self.fields['secenek'].queryset = self.fields['secenek'].queryset.filter(aktif=True)

class ReklamForm(forms.ModelForm):
    sure = forms.IntegerField(
        label='Reklam Süresi (Gün)',
        min_value=1,
        max_value=365,
        initial=30,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Reklam
        fields = ['reklam_alani', 'baslik', 'resim', 'link']
        widgets = {
            'reklam_alani': forms.Select(attrs={'class': 'form-select'}),
            'baslik': forms.TextInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reklam_alani'].queryset = self.fields['reklam_alani'].queryset.filter(aktif=True)
        self.fields['reklam_alani'].empty_label = None
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.baslangic_tarihi = datetime.now()
        instance.bitis_tarihi = instance.baslangic_tarihi + timedelta(days=self.cleaned_data['sure'])
        if commit:
            instance.save()
        return instance