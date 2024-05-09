import asyncio, threading, requests

from threading import Thread, Event
from time import sleep
from django.db import models

from asgiref.sync import sync_to_async

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
            if not self.connected: await self.connect()
            print(f"running {self.identifier} {self.base_url}")
            sleep(3)
            await self.arefresh_from_db()

        if not self.keep_alive_signal: print("Keep alive signal caused stoppage")

    async def connect(self):
        if not self.base_url:
            self.generate_base_url()
        while not self.connected and self.keep_alive_signal:
            try:
                print("trying connection")
                response = self.enable_usb_control()
                if response.ok:
                    print("Connected via USB")
                    self.connected = True
                    self.save()
                    return
            except requests.Timeout as e:
                print("Failed to enable wired control. Retrying wakeup")

            try:
                print("Attempting wake up via BLE")
                # await ble_connect.connect_ble(self.identifier)

            except RuntimeError as e:
                print(f"Error connecting via BLE")

            print("Waiting for camera")
            sleep(10)
            await self.arefresh_from_db()

    def enable_usb_control(self):
        return requests.get(f"{self.base_url}/gopro/camera/control/wired_usb?p=1", timeout=2)

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
        # it does allow the is_alive check when stopping to always work
        return Thread(target=asyncio.run, args=(self.keep_alive_task(),))

class Timelapse(models.Model):
    gopro = models.OneToOneField(GoPro, on_delete=models.PROTECT)
    interval = models.PositiveIntegerField(default=10)
    photos_taken = models.PositiveIntegerField(default=0)
    timelapse_preset_url = models.CharField(
        default="/gopro/camera/presets/load?id=65536", editable=False, max_length=40
    )
    
    task_id = models.IntegerField(default=-1)  # Timelapse thread id
    task_signal = models.BooleanField(default=False, blank=False) # True if timelapse task is active

    def __str__(self):
        return str(self.interval)
    
    def start(self):
        _timelapse_task = self.get_thread(self.task_id, self.timelapse_task())

        if _timelapse_task.is_alive():
            print(f"Timelapse task already running on {self.gopro.identifier}")
            return
        
        print(f"Starting timelapse task for {self.gopro.identifier}")
        self.task_signal = True
        _timelapse_task.start()
        self.task_id = _timelapse_task.ident
        self.save()

    def stop(self):
        _timelapse_task = self.get_thread(self.task_id, self.timelapse_task())

        if not _timelapse_task.is_alive():
            print(f"Timelapse task is not running")
            return

        self.task_signal = False
        self.save()
        if _timelapse_task.is_alive(): # the task may have stopped itself after the signal was set
            _timelapse_task.join()

        self.task_id = -1
        self.save()
        print("Timelapse task stopped")


    async def timelapse_task(self):
        while self.task_signal:
            try:
                print("Shutter")
                self.photos_taken += 1
                sync_to_async(self.save)
                sleep(self.interval)
            except requests.exceptions.RequestException:
                print("Picture not taken")
            await self.arefresh_from_db()


    # This will eventually be refactored to outside this class, hence the reduntant passing of thread_id
    def get_thread(self, thread_id, thread_task):
        # if not self.keep_alive_signal:
        #     print("Signal to stop. not creating a new thread")
        #     return

        if thread_id > 0:
            print(thread_id)
            for thread in threading.enumerate():
                print(thread.ident)
                if thread.ident == thread_id:
                    print("Found")
                    return thread
            print("Not Found")

        print("Creating a new thread") 
        # Although it is not ideal to always make a new thread,
        # it does allow the is_alive check when stopping to always work
        return Thread(target=asyncio.run, args=(thread_task,))
            

