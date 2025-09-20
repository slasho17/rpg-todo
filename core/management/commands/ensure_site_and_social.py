from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
import os

# allauth models
try:
    from allauth.socialaccount.models import SocialApp
except Exception:
    SocialApp = None

class Command(BaseCommand):
    help = "Ensure SITE (id/domain) exists and Google SocialApp is linked (and created if missing)."

    def handle(self, *args, **options):
        site_id = int(getattr(settings, "SITE_ID", 1))
        domain = os.getenv("SITE_DOMAIN", "").strip()
        name = os.getenv("SITE_NAME", "Prod").strip() or "Prod"

        if domain:
            site, _ = Site.objects.get_or_create(id=site_id, defaults={"domain": domain, "name": name})
            site.domain = domain
            site.name = name
            site.save()
            self.stdout.write(self.style.SUCCESS(f"Site {site_id} set to {domain} ({name})"))
        else:
            self.stdout.write(self.style.WARNING("SITE_DOMAIN not set; skipping Site update."))

        # Se allauth estiver disponível, garante SocialApp do Google
        if SocialApp is None:
            self.stdout.write(self.style.WARNING("allauth not available; skipping SocialApp step."))
            return

        google_client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

        app = None
        try:
            app = SocialApp.objects.get(provider="google")
        except SocialApp.DoesNotExist:
            if google_client_id and google_client_secret:
                app = SocialApp.objects.create(
                    provider="google",
                    name="Google",
                    client_id=google_client_id,
                    secret=google_client_secret,
                )
                self.stdout.write(self.style.SUCCESS("Google SocialApp created."))
            else:
                self.stdout.write(self.style.WARNING("No Google SocialApp and no GOOGLE_CLIENT_ID/SECRET; skipping."))
                return

        # Vincula ao site atual, se ainda não estiver
        if site_id not in app.sites.values_list("id", flat=True):
            app.sites.add(site_id)
            self.stdout.write(self.style.SUCCESS(f"Google SocialApp linked to Site {site_id}."))
        else:
            self.stdout.write(self.style.SUCCESS("Google SocialApp already linked to current Site."))
