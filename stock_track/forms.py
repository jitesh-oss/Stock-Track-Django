from django import forms
from django.forms import ModelForm
from .models import Stocksmain

class inputForm(forms.Form):
    exchange_name = forms.CharField(label='Exchange', max_length=50, widget=forms.TextInput(attrs={'class': "form-control"}))
    st_name = forms.CharField(label='Stock Name', max_length=255, widget=forms.TextInput(attrs={'class': "form-control"}))
    st_code = forms.CharField(label='Stock Code', max_length=50, widget=forms.TextInput(attrs={'class': "form-control"}))
    st_buyprice = forms.FloatField(label='Buy Price', widget=forms.TextInput(attrs={'class': "form-control"}))
    st_targetprice = forms.FloatField(label='Target', widget=forms.TextInput(attrs={'class': "form-control"}))
    st_stoploss = forms.FloatField(label='Stoploss', widget=forms.TextInput(attrs={'class': "form-control"}))
    st_ltp = forms.FloatField(label='Last Traded Price', widget=forms.TextInput(attrs={'class': "form-control"}))
    bought_on = forms.DateTimeField(label='Bought On', widget=forms.TextInput(attrs={'class': "form-control"}))

class inputForm1(ModelForm):
    class Meta:
        model = Stocksmain
        fields = ['exchange_name', 'st_name', 'st_code', 'st_buyprice', 'st_targetprice', 'st_stoploss', 'st_ltp', 'bought_on']