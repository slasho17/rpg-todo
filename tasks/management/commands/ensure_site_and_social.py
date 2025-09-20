from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
import os

try:
    from allauth.socialaccount.models import SocialApp
except Exception:
    SocialApp = None

class Command(BaseCommand):
    help = "Ensure Site(domain/name) exists and Google SocialApp is linked."

    def handle(self, *args, **options):
        desired_site_id = int(getattr(settings, "SITE_ID", 1))
        domain = os.getenv("SITE_DOMAIN", "").strip()
        name = (os.getenv("SITE_NAME", "") or "Prod").strip()

        if not domain:
            self.stdout.write(self.style.WARNING("SITE_DOMAIN not set; skipping Site update."))
            target_site = Site.objects.get(id=desired_site_id)
        else:
            # 1) Procura pelo domínio (único)
            target_site = Site.objects.filter(domain=domain).first()

            if target_site:
                # Atualiza nome se mudou
                changed = False
                if target_site.name != name:
                    target_site.name = name
                    target_site.save()
                    changed = True
                self.stdout.write(self.style.SUCCESS(
                    f"Using existing Site id={target_site.id} domain={target_site.domain} "
                    + ("(name updated)" if changed else "(ok)")
                ))
            else:
                # 2) Se não existe por domínio, tenta reaproveitar o id desejado
                site_by_id = Site.objects.filter(id=desired_site_id).first()
                if site_by_id:
                    # Evita colisão de domínio: como não existe outro com esse domínio,
                    # podemos atualizar este registro para o domínio desejado.
                    site_by_id.domain = domain
                    site_by_id.name = name
                    site_by_id.save()
                    target_site = site_by_id
                    self.stdout.write(self.style.SUCCESS(
                        f"Updated Site id={target_site.id} to domain={domain} ({name})"
                    ))
                else:
                    # 3) Cria um novo (tentando usar o id desejado quando possível)
                    target_site = Site.objects.create(id=desired_site_id, domain=domain, name=name)
                    self.stdout.write(self.style.SUCCESS(
                        f"Created Site id={target_site.id} domain={domain} ({name})"
                    ))

        # Se o SITE_ID das configs não bate com o id real do Site, avisa (não quebra)
        if desired_site_id != target_site.id:
            self.stdout.write(self.style.WARNING(
                f"Settings.SITE_ID={desired_site_id} differs from DB site id={target_site.id}. "
                f"Set env SITE_ID={target_site.id} and redeploy for consistency."
            ))

        # --- SocialApp Google ---
        if SocialApp is None:
            self.stdout.write(self.style.WARNING("allauth not available; skipping SocialApp step."))
            return

        google_client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

        app = SocialApp.objects.filter(provider="google").first()
        if not app:
            if google_client_id and google_client_secret:
                app = SocialApp.objects.create(
                    provider="google",
                    name="Google",
                    client_id=google_client_id,
                    secret=google_client_secret,
                )
                self.stdout.write(self.style.SUCCESS("Google SocialApp created."))
            else:
                self.stdout.write(self.style.WARNING(
                    "Google SocialApp not found and GOOGLE_CLIENT_ID/SECRET not set; skipping."
                ))
                return

        # Vincula ao site encontrado (se ainda não estiver)
        if target_site.id not in app.sites.values_list("id", flat=True):
            app.sites.add(target_site)
            self.stdout.write(self.style.SUCCESS(f"Google SocialApp linked to Site id={target_site.id}."))
        else:
            self.stdout.write(self.style.SUCCESS("Google SocialApp already linked to current Site."))
