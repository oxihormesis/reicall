from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.forms import ModelForm
from call_tracking.models import Campaign, LeadSources, PurchasedNumbers


class AreaCodeForm(forms.Form):
    """Form for specifying the area code when searching for available numbers"""
    area_code = forms.CharField(min_length=3, max_length=3, required=False)

class CampaignForm(ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'channel', 'lead_sources']

class LeadSourceForm(ModelForm):
    class Meta:
        model = LeadSources
        fields = ['name', 'incoming_number', 'forwarding_number']


class PurchaseNumberForm(forms.Form):
    """Form for purchasing a number from the Twilio API"""
    phone_number = PhoneNumberField()


class AddExistingNumberForm(ModelForm):
    class Meta:
        model = PurchasedNumbers
        fields = ['phone_number']