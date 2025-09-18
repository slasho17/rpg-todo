from django.conf import settings
from django.db import models

class Task(models.Model):
    """
    Uma tarefa do usuário. Terá streak por tarefa (calculado depois).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    difficulty = models.IntegerField(default=1)  # 1=easy, 2=medium, 3=hard (ajustável depois)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} (u:{self.user_id})"


class Completion(models.Model):
    """
    Registro de conclusão por data. Atende seu pedido:
    - tem um booleano `completed`
    - amarra task+date para não duplicar completude do mesmo dia
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="completions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="completions")
    date = models.DateField()               # YYYY-MM-DD do fuso America/Sao_Paulo
    completed = models.BooleanField(default=True)
    awarded_xp = models.IntegerField(default=0)  # calcularemos mais tarde no server
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("task", "date"),)  # uma linha por task/dia
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["task", "date"]),
        ]
        ordering = ["-date", "-created_at"]

    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"{self.task_id} @ {self.date} {status}"
