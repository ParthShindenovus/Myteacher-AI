from django.db import models


class LearningSession(models.Model):
    session_id = models.CharField(max_length=128, unique=True)
    state = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.session_id
