from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings
import os

class Command(BaseCommand):
    help = "Ensure current SITE_ID domain/name and bind Google SocialApp to this site"

    def handle(self, *args, **options):
        site_id = int(getattr(settings, "SITE_ID", 1))
        domain = os.getenv("SITE_DOMAIN", "").strip()
        name = os.getenv("SITE_NAME", "Prod").strip() or "Prod"

        if not domain:
            self.stdout.write(self.style.WARNING("SITE_DOMAIN not set; skipping Site update."))
        else:
            site, _ = Site.objects.get_or_create(id=site_id, defaults={"domain": domain, "name": name})
            # Caso já exista, atualiza
            site.domain = domain
            site.name = name
            site.save()
            self.stdout.write(self.style.SUCCESS(f"Site {site_id} set to {domain} ({name})"))

        # Vincula o SocialApp do Google (se existir) ao site atual
        try:
            app = SocialApp.objects.get(provider="google")
        except SocialApp.DoesNotExist:
            self.stdout.write(self.style.WARNING("No Google SocialApp found; create it in admin later."))
            return

        if site_id not in app.sites.values_list("id", flat=True):
            app.sites.add(site_id)
            self.stdout.write(self.style.SUCCESS(f"Google SocialApp linked to Site {site_id}."))
        else:
            self.stdout.write(self.style.SUCCESS("Google SocialApp already linked to current Site."))
