from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

def hello(request):
    user = request.user
    msg = f"Hello, {user.username}! RPG To-Do" if user.is_authenticated else "Hello, RPG To-Do!"
    return HttpResponse(f"""
        <html><body>
            <h1>{msg}</h1>
            <p><a href='/accounts/login/'>Login</a> | <a href='/accounts/logout/'>Logout</a></p>
            <p><a href='/admin/'>Admin</a> | <a href='/tasks/ping/'>Tasks Ping</a></p>
        </body></html>
    """)

urlpatterns = [
    path("", hello, name="hello"),
    path("admin/", admin.site.urls),
    path("tasks/", include("tasks.urls")),      # OK
    path("accounts/", include("allauth.urls")), # OK
]
