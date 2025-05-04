from django.urls import path

from habits.apps import HabitsConfig
from habits.views import HabitListCreateView, PublicHabitListView, HabitDetailView

app_name = HabitsConfig.name
urlpatterns = [
    path("habits/", HabitListCreateView.as_view(), name="habit-list-create"),
    path("habits/public/", PublicHabitListView.as_view(), name="public-habits"),
    path("habits/<int:pk>/", HabitDetailView.as_view(), name="habit-detail"),
]
