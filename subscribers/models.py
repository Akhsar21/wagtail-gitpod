from django.db import models

# Create your models here.


class Subscriber(models.Model):
    email = models.EmailField(max_length=100, blank=False, null=False,
                              help_text="Email address")
    full_name = models.CharField(max_length=100, blank=False, null=False,
                                 help_text="First and last name")

    def __str__(self):
        """Str repr of this object."""
        return self.full_name
