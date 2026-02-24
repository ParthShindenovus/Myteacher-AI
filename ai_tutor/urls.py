from django.urls import path

from ai_tutor.views import DecomposeQuestionAPIView, NormalizeInputAPIView

urlpatterns = [
    path("normalize/", NormalizeInputAPIView.as_view(), name="normalize-input"),
    path("decompose/", DecomposeQuestionAPIView.as_view(), name="decompose-question"),
]
