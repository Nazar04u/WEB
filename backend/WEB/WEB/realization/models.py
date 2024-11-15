from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

class HelloModel(models.Model):
    text = models.TextField()


class MonteCarloIntegrationModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    function = models.TextField()  # Store the function expression as a string
    lower_bound = models.FloatField()  # Lower limit of integration
    upper_bound = models.FloatField()  # Upper limit of integration
    estimated_area = models.FloatField(null=True, blank=True)  # Store the result of integration
    graphic = models.ImageField(upload_to='solved/', blank=True, null=True)  # Optional image field
    timestamp = models.DateTimeField(auto_now_add=True)  # Store the time of creation
    time_needed = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} - {self.function} [{self.lower_bound}, {self.upper_bound}]"

    def get_graphic(self):
        if self.graphic and hasattr(self.graphic, 'url'):
            return f'http://localhost:8001/{self.graphic.url}'
        return ''

    class Meta:
        ordering = ['-timestamp']