from .views import HomeView, SignUpView, logout_view, LoginView, TaskStatusView, Delete_Task_View
from rest_framework.urls import *

app_name = 'realization'

urlpatterns = [
      path('', HomeView.as_view(), name='home'),
      path("sign_up/", SignUpView.as_view(), name='sign_up'),
      path("login/", LoginView.as_view(), name='login'),
      path('task-status/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
      path("cancel_task/<str:task_id>/", Delete_Task_View.as_view(), name='cancel'),
      path("logout/", logout_view, name="logout")
]