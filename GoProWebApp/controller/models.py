from pathlib import Path
from django.conf import settings
import asyncio, threading, requests

from threading import Thread, Event
from time import sleep
from requests.exceptions import RequestException
from django.db import models

from asgiref.sync import sync_to_async

from .thread_manager import ThreadManager

# Create your models here.
class Image(models.Model):
	date_time = models.DateTimeField(auto_now_add=True)
	path = models.FilePathField()
	name = models.CharField(max_length=20)
	size = models.FloatField(null=True)

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
	

	# TODO: feature on hold, linked to issue #28
	# @classmethod
	# def from_db(cls, db, field_names, values):
	# 	instance = super().from_db(db, field_names, values)
	# 	instance.restore()
	# 	return instance
	#
	# def restore(self):
	# 	if self.connected:
	# 		print("I was running at somepoint")
	# 		# TODO: call keep_alive, if returns ok then restore thread
	# 		self.connected = ThreadManager.check_thread(self.keep_alive_id)
	# 		self.save()
	# 		return
	# 	else:
	# 		print("I'm not running")

	def start(self): #TODO rename to [dis]connect
		if self.keep_alive_signal:
			print("Keep alive signal is already active, verifying thread")
			if ThreadManager.check_thread(self.keep_alive_id):
				print("thread verified as running")
				return
			print("Signal was active, but no thread was found")

		print(f"Starting keep alive signal for GoPro {self.identifier}")
		self.keep_alive_signal = True
		self.save()
		self.keep_alive_id = ThreadManager.start(self.keep_alive_id, self.keep_alive_task()).ident
		self.save()

	def stop(self):
		if not self.keep_alive_signal:
			print("Keep alive signal is not active")
			return
		# Set the signal to send keep alive loop and stop attempting reconnect
		self.keep_alive_signal = False
		self.save()
		# if the thread is still running, then stop it
		ThreadManager.stop(self.keep_alive_id, self.keep_alive_task())
		self.keep_alive_id = -1
		self.save()
		print("Keep alive signal stopped")

	async def keep_alive_task(self):
		url = self.base_url + "/gopro/camera/keep_alive"
		while self.keep_alive_signal:
			try:
				if not self.connected: 
					print("not connected")
					await self.connect()
				# print(f"running {self.identifier} {self.base_url}")
				requests.get(url, timeout=2) #TODO refactor outside of function
			except RequestException:
				print("Failed to communicate with GoPro")
				self.connected = False
				self.save()
			sleep(3)
			# await self.arefresh_from_db() # TODO this resets self.connect to False, I thought it would update to the most recent value

		if not self.keep_alive_signal: 
			print("Keep alive signal caused stoppage")

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
					await sync_to_async(self.save)()
					return
			except requests.Timeout as e:
				print("Failed to enable wired control. Retrying wakeup")

			try:
				print("Attempting wake up via BLE")
				# TODO await ble_connect.connect_ble(self.identifier)

			except RuntimeError as e:
				print(f"Error connecting via BLE")

			print("Waiting for camera")
			sleep(10)
			# await self.arefresh_from_db()
		print("connected")

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
	
	def get_status(self) -> dict:
		try:
			status = {}
			response_json = requests.get(self.base_url + "/gopro/camera/state", timeout=2).json()
			status['battery'] = response_json['status']['2']
			status['photos_remain'] = response_json['status']['34']
			status['photos_taken'] = response_json['status']['38']
			status['free_space_kb'] = response_json['status']['54']
			return status

		except RequestException as e:
			print("Failed to get status")
	
	async def start_shutter(self) -> int:
		try:
			print("Shutter")
			response = requests.get(self.base_url + "/gopro/camera/shutter/start", timeout=2)
			return response.status_code
		
		except RequestException as e:
			print("Failed to start shutter")

	async def download_latest(self, delete) -> str:
		# Determine folder and name of latest media
		response = requests.get(self.base_url + '/gopro/media/list', timeout=2).json()
		latest_img_dir = response['media'][-1]['d']
		latest_img_name = response['media'][-1]['fs'][-1]['n']

		# Start single file download
		await self.download_media(latest_img_dir, latest_img_name)

		if delete:
			self.delete_media(latest_img_dir, latest_img_name)

		# return dest_path / latest_img_dir / latest_img_name
	
	async def download_media(self, srcfolder, srcimage):
		# Target URL
		url = self.base_url + f"/videos/DCIM/{srcfolder}/{srcimage}"
		# Path file will be saved in
		path = (Path(__file__).parent / "media/images").resolve()

		try:
			#Download Image
			with requests.get(url, timeout=2, stream=True) as response:
				response.raise_for_status()
				with open(f"{path}/{srcimage}", 'wb') as f:
					f.write(response.content)

			# Store image reference in db
			image = Image(path=path, name=srcimage)
			await sync_to_async(image.save)()

		except requests.exceptions.RequestException as e:
			print("error")

	def delete_media(self, srcfolder, srcimage):
		url = self.base_url + f"/gopro/media/delete/file?path={srcfolder}/{srcimage}"
		requests.get(url, timeout=2)

	def set_auto_powerdown_off(self) -> int:
		try:
			OPTIONS = "setting=59&option=0"
			response = requests.get(self.base_url + "/gopro/camera/setting" + "?" + OPTIONS, timeout=2)
			return response.status_code
		except RequestException as e:
			print("Failed to turn auto powerdown off")

	def set_auto_powerdown_on(self) -> int:
		try:
			url = self.base_url + "/gopro/camera/setting?setting=59&option=4"
			response = requests.get(url, timeout=2)
			return response.status_code
		except RequestException as e:
			print("Failed to turn autopower down on")


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
		if self.task_signal:
			print(f"Timelapse task already running on {self.gopro.identifier}")
			return
		
		print(f"Starting timelapse task for {self.gopro.identifier}")
		self.task_id = ThreadManager.start(thread_id=self.task_id, thread_target=self.timelapse_task()).ident
		self.task_signal = True
		self.save()

	def stop(self):
		if not self.task_signal:
			print(f"Timelapse task is not running")
			return

		self.task_signal = False
		self.save()
		ThreadManager.stop(thread_id=self.task_id, thread_target=self.timelapse_task)

		self.task_id = -1
		self.save()
		print("Timelapse task stopped")


	async def timelapse_task(self):
		inter = 3
		while self.task_signal:
			try:
				await self.gopro.start_shutter()
				self.photos_taken += 1
				sleep(inter)
				await self.gopro.download_latest(delete=True)
				await sync_to_async(self.save)()
				sleep(self.interval-inter)
			except RequestException:
				print("Picture not taken")
			# await self.arefresh_from_db()

