import asyncio, threading
from threading import Thread, Event
from time import sleep
from django.db import models

# Create your models here.
class GoPro(models.Model):
    identifier = models.CharField(
        max_length=4,
        default='4933'
    )
    base_url = models.URLField(
        blank=True
    )
    connected = models.BooleanField(
        default=False, 
        blank=False
    )
    keep_alive_id = models.IntegerField(default=-1)
    keep_alive_signal = models.BooleanField(
        default=False,
        blank=False
    )

    def __str__(self):
        return self.identifier

    def start(self):
        if not self.base_url:
            self.generate_base_url()

        _keep_alive = self.get_thread()

        if not _keep_alive.is_alive():
            print(f"Starting keep alive signal for GoPro {self.identifier}")
            # self.set_auto_powerdown_off()
            self.keep_alive_signal = True
            _keep_alive.start()
            self.keep_alive_id = _keep_alive.ident
            self.save()
        else:
            print("Keep alive signal is already active")

    def stop(self):
        # Set the signal to send keep alive loop and stop attempting reconnect
        self.keep_alive_signal = False
        self.save()
        # if the thread is still running, then stop it
        _keep_alive = self.get_thread()
        if _keep_alive.is_alive():
            _keep_alive.join()
        self.connected = False
        self.save()
        print("Keep alive signal stopped")

    async def keep_alive_task(self):
        while self.keep_alive_signal:
            print(f"running {self.identifier} {self.base_url}")
            sleep(3)
            await self.arefresh_from_db()

        if not self.keep_alive_signal: print("Keep alive signal caused stoppage")

    def is_alive(self) -> bool:
        return self.get_thread().is_alive()
    
    def generate_base_url(self) -> str:
        base_url = f"http://172.2{self.identifier[1]}.1{self.identifier[2]}{self.identifier[3]}.51:8080"
        self.base_url = base_url
        self.save()
        return base_url

    def is_connected(self) -> bool:
        return self.connected
    
    def get_thread(self):
        # if not self.keep_alive_signal:
        #     print("Signal to stop. not creating a new thread")
        #     return

        if self.keep_alive_id > 0:
            print(self.keep_alive_id)
            for thread in threading.enumerate():
                print(thread.ident)
                if thread.ident == self.keep_alive_id:
                    print("Found")
                    return thread
            print("Not Found")

        print("Creating a new thread") 
        # Although it is not ideal to always make a new thread,
        # it does allow the is_alive check above to always work
        return Thread(target=asyncio.run, args=(self.keep_alive_task(),))

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

