from django.conf.urls import url
#url is just an alias for re_path
from django.urls import path, re_path

from . import views
from .views import available_numbers, purchase_number, forward_call, LeadSourceUpdateView, leads_by_source, leads_by_city, leads_by_zipcode, CallInfoView, CallAudioView, new_campaign, CampaignUpdateView, home, landing_view, lead_source_view, VueCallsList, phone_numbers_view, AddExistingNumber

app_name = 'call_tracking'
urlpatterns = [
    #moved from ROOT_URLCONF
    url(r'^$', views.landing_view, name='landing'),
    url(r'^home', views.home, name='home'),
    url(r'^lead-sources', views.lead_source_view, name='lead_sources'),
    url(r'^phone-numbers', views.phone_numbers_view, name='phone_numbers'),
    url(r'^add-numbers', views.AddExistingNumber.as_view(), name='add_numbers'),
    path('recent-activity', views.CallsList.as_view(), name='recent-activity'),
    path('call/token/', views.get_token, name='get_call_token'),
    path('call/', views.call, name='call'),
    path('twl/callback', views.call_status_callback, name='status_callback'),
    path('caller-info', views.caller_info_view, name='get_caller_info'),

    # URLs for searching for and purchasing a new Twilio number
    url(r'^available-numbers$', available_numbers, name='available_numbers'),
    url(r'^purchase-number$', purchase_number, name='purchase_number'),

    # Endpoint Twilio will use for incoming calls
    url(r'^forward-call$', forward_call, name='forward_call'),

    # Lead Source edit and delete views
    url(r'^(?P<pk>[0-9]+)/edit$',
        LeadSourceUpdateView.as_view(),
        name='edit_lead_source'),
    
    # Call recording audio view
    url(r'^(?P<pk>[0-9]+)/call-audio$',
        CallAudioView.as_view(),
        name='call_audio'),

    # Call information view
    url(r'^(?P<pk>[0-9]+)/call-info$',
        CallInfoView.as_view(),
        name='call_info'),

    # List Campaigns
    url(r'^campaigns', views.campaigns, name='campaigns'),

    # Create Campaign
    url(r'new-campaign$', new_campaign, name='new_campaign'),

    # Campaigns edit and delete views
    url(r'^campaign/(?P<pk>[0-9]+)/edit$',
        CampaignUpdateView.as_view(),
        name='edit_campaign'),

    # Lead Source create
    url(r'new_lead_source$', views.newleadsource, name='new_lead_source'),

    # JSON URLs for the bar chart data
    url(r'^leads-by-source$', leads_by_source, name='leads_by_source'),
    url(r'^leads-by-zipcode$', leads_by_zipcode, name='leads_by_zipcode'),
    url(r'^leads-by-city$', leads_by_city, name='leads_by_city')
]
