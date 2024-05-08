from django.db import models

# Create your models here.
class GoPro(models.Model):
    identifier = models.CharField(
        max_length=4, 
        unique=True,
        default='4933',
        primary_key=True
    )
    base_url = models.URLField(blank=True)
    connected = models.BooleanField(
        default=False, 
        blank=False
    )

    def __str__(self):
        return self.identifier
    
    def generate_base_url(self) -> str:
        return f"http://172.2{self.identifier[-3]}.1{self.identifier[-2:]}.51:8080"

    def is_connected(self) -> bool:
        return self.connected

class Timelapse(models.Model):
    gopro = models.OneToOneField(GoPro, on_delete=models.PROTECT)
    interval = models.PositiveIntegerField(default=10)
    photos_taken = models.PositiveIntegerField(default=0)
    timelapse_preset_url = models.URLField(
        default="/gopro/camera/presets/load?id=65536"
    )
    # Timelapse thread id
    task_id = models.PositiveIntegerField(blank=True)

    def __str__(self):
        return str(self.interval)


