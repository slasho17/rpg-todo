from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

def hello(request):
    from django.conf import settings
    return HttpResponse(f"SITE_ID={settings.SITE_ID}, USERNAME_REQUIRED={getattr(settings, 'ACCOUNT_USERNAME_REQUIRED', '??')}")


urlpatterns = [
    path("", hello, name="hello"),
    path("admin/", admin.site.urls),
    path("tasks/", include("tasks.urls")),      # OK
    path("accounts/", include("allauth.urls")), # OK
]
