from django.db import models

# Create your models here.

class app_details(models.Model):
    app_id = models.CharField(max_length=50)
    app_name = models.CharField(max_length=50)
    developer = models.CharField(max_length=50)
    developer_email = models.EmailField(max_length=50)
    icon_url = models.CharField(max_length=100)
