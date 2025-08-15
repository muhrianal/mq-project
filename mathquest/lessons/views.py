from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Lesson
from .serializers import LessonSerializer

class LessonListView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class LessonDetailView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
