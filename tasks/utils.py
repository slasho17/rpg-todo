from datetime import datetime, timedelta
import zoneinfo
from .models import Completion

TZ = zoneinfo.ZoneInfo("America/Sao_Paulo")

def today_sp_date():
    return datetime.now(TZ).date()

def task_streak_until_date(user, task_id, target_date):
    """
    Conta quantos dias consecutivos a task estava 'completed=True'
    retrocedendo a partir de target_date.
    Ex.: se completou em target_date, target_date-1, target_date-2,
    mas NÃO em target_date-3 => streak = 3.
    """
    d = target_date
    streak = 0
    while True:
        exists = Completion.objects.filter(
            user=user, task_id=task_id, date=d, completed=True
        ).exists()
        if not exists:
            break
        streak += 1
        d = d - timedelta(days=1)
    return streak
