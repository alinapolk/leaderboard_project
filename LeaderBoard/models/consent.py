from django.db import models
from django.contrib.auth.models import User


class UserConsent(models.Model):
    """Согласие на обработку персональных данных"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    consent_date = models.DateField(auto_now_add=True)
    is_given = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_consent'

    def __str__(self):
        status_text = "дано" if self.is_given else "не дано"
        return f"{self.user.username} - согласие {status_text}"