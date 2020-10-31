from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^', include('call_tracking.urls')),
    url(r'^accounts/', include('accounts.urls'), name="accounts"),
    # Include the Django admin
    url(r'^admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()