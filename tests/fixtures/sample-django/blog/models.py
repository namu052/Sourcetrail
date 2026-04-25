from django.db import models


class UserProfile(models.Model):
    email = models.EmailField()
    is_staff = models.BooleanField(default=False)

    def display_name(self) -> str:
        return self.email.split("@")[0]
