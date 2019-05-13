from django.conf.urls import include, url
from django.contrib import admin

from call_tracking.views import home, landing_view

urlpatterns = [
    url(r'^$', landing_view, name='landing'),
    url(r'^username', home, name='home'),
    url(r'^call-tracking', include('call_tracking.urls')),
    url(r'^accounts', include('accounts.urls'), name="accounts"),

    # Include the Django admin
    url(r'^admin/', include(admin.site.urls)),
]
