from datetime import date as date_cls
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date

from .models import Task, Completion
from .utils import task_streak_until_date


# XP base por dificuldade
XP_BY_DIFFICULTY = {1: 5, 2: 10, 3: 20}

def ping(request):
    return JsonResponse({"ok": True, "app": "tasks"})

@login_required
def day_view(request):
    """
    GET /tasks/api/day/?date=YYYY-MM-DD
    Retorna todas as tasks do usuário e o estado de conclusão naquele dia.
    """
    qdate_str = request.GET.get("date")
    d = parse_date(qdate_str) if qdate_str else None
    if d is None:
        return HttpResponseBadRequest("Use ?date=YYYY-MM-DD")

    user = request.user
    tasks = list(Task.objects.filter(user=user, active=True).values("id", "title", "difficulty"))

    # pega completions desse dia
    completions = Completion.objects.filter(user=user, date=d, completed=True)
    completed_ids = set(completions.values_list("task_id", flat=True))

    # monta resposta com completed: bool
    data = []
    for t in tasks:
        data.append({
            "task_id": t["id"],
            "title": t["title"],
            "difficulty": t["difficulty"],
            "completed": t["id"] in completed_ids,
        })

    # opcional: total de XP do dia (por enquanto só soma awarded_xp)
    total_xp = Completion.objects.filter(user=user, date=d, completed=True).sum("awarded_xp") if hasattr(Completion.objects, "sum") else sum(
        Completion.objects.filter(user=user, date=d, completed=True).values_list("awarded_xp", flat=True)
    )
    
    qdate_str = request.GET.get("date")
    d = parse_date(qdate_str) if qdate_str else None
    if d is None:
        return HttpResponseBadRequest("Use ?date=YYYY-MM-DD")

    user = request.user
    tasks = list(Task.objects.filter(user=user, active=True).values("id", "title", "difficulty"))

    # completions desse dia
    completions = Completion.objects.filter(user=user, date=d, completed=True)
    completed_ids = set(completions.values_list("task_id", flat=True))

    data = []
    for t in tasks:
        task_id = t["id"]
        completed = task_id in completed_ids
        streak_count = task_streak_until_date(user, task_id, d)  # <— NOVO

        data.append({
            "task_id": task_id,
            "title": t["title"],
            "difficulty": t["difficulty"],
            "completed": completed,
            "streak_count": streak_count,  # <— NOVO
        })

    # total_xp do dia (soma awarded_xp)
    total_xp = sum(
        Completion.objects.filter(user=user, date=d, completed=True).values_list("awarded_xp", flat=True)
    )

    return JsonResponse({"date": d.isoformat(), "tasks": data, "total_xp": total_xp})

@csrf_exempt  # DEV: para facilitar teste pelo navegador. Depois tiramos.
@login_required
def complete_view(request):
    """
    POST /tasks/api/complete/
    body JSON: { "task_id": int, "date": "YYYY-MM-DD", "completed": true|false }
    Cria/atualiza a Completion única (task, date).
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    try:
        import json
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    task_id = payload.get("task_id")
    date_str = payload.get("date")
    completed = payload.get("completed")

    if task_id is None or date_str is None or completed is None:
        return HttpResponseBadRequest("Missing fields: task_id, date, completed")

    d = parse_date(date_str)
    if d is None:
        return HttpResponseBadRequest("Invalid date format (YYYY-MM-DD)")

    user = request.user

    # garante que a task é do usuário
    try:
        task = Task.objects.get(id=task_id, user=user, active=True)
    except Task.DoesNotExist:
        return HttpResponseBadRequest("Task not found or not yours")

    # calcula XP base da dificuldade
    base_xp = XP_BY_DIFFICULTY.get(task.difficulty, 5)

    # Se marcar como concluído => awarded_xp = base
    # Se marcar como não concluído => awarded_xp = 0
    obj, _created = Completion.objects.update_or_create(
        task=task, user=user, date=d,
        defaults={
            "completed": bool(completed),
            "awarded_xp": base_xp if completed else 0
        }
    )

    # streak na data após a alteração
    streak_now = task_streak_until_date(user, task.id, d)

    return JsonResponse({
        "ok": True,
        "task_id": task.id,
        "date": d.isoformat(),
        "completed": obj.completed,
        "awarded_xp": obj.awarded_xp,
        "streak_count": streak_now,  # <— útil para feedback imediato no cliente
    })
