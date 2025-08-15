from django.urls import path
from .views import LessonListView, LessonDetailView
from submissions.views import LessonSubmitView

urlpatterns = [
    path("", LessonListView.as_view(), name="lessons-list"),
    path("<int:pk>/", LessonDetailView.as_view(), name="lesson-detail"),
    path("<int:id>/submit", LessonSubmitView.as_view(), name="lesson-submit"),
]
