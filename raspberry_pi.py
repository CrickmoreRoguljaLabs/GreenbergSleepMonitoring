# Adapted from SCT raspberry_pi Pi Control
import paramiko
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
	import tkinter as tk
import time
from command_window import Command_Window
from logExperimentPC import Experiment

use_ssh = True
test_video = True

class Raspberry_Pi(object):
	# Defines the raspberry pi class with address IP_ADDRESS, controls shell interactions with the Pi using paramiko
	
	def __init__(self,ID,master, stream_port=5000):
		self.IP_ADDRESS = ID[0]
		self.stream_port = stream_port
		self.window = Command_Window(tk.Toplevel(master),pi=self)
		self.window.set_title(ID[1])
		self.expt = Experiment(IP_ADDRESS=self.IP_ADDRESS)
		self.window.quit_button(lambda: self.close_pi())
		self.window.rename_log_button(self.expt)
		self.window.note_button(self.expt)

		if use_ssh:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(ID[0],username='pi',password='raspberry')
			self.ssh = ssh
			self.sftp_client = self.ssh.open_sftp()
	
	def create_video_file(self, videoName=None):
		# create a stream targeted to "receiver"
		if not ( (videoName is None) or (videoName is "Name of video") ):
			stream_string = "raspivid -t 0 -fps 20 -h 720 -w 1400 -b 1000000 -o - | tee %s.h264 | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=%s port=5000"%(videoName,self.IP_ADDRESS)
			self.stdin_v, self.stdout_v, self.stderr_v = self.ssh.exec_command(stream_string, get_pty=True)
			self.expt.note_change("Began video: %s" %(videoName))
			self.expt.change_name(videoName)
			self.expt.change_time_zero()
			self.expt.note_change("Reset time")
		else:
			stream_string = "raspivid -t 0 -fps 20 -h 720 -w 1400 -b 1000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=%s port=5000"%(videoName,self.IP_ADDRESS)
			self.stdin_v, self.stdout_v, self.stderr_v = self.ssh.exec_command(stream_string, get_pty=True)
		self.videoName = videoName

	def terminate_video_file(self):
		# terminates the video initiated by create_video_file
		self.stdin_v.write("\x03")
		self.expt.note_change("Ended video: %s" %self.videoName)

	def close_pi(self):
		# End the ssh session and close the window
		if use_ssh:
			self.ssh.close()
		#if not self.window.stream is None:
		#	self.window.stream.stop()
		self.window.destroy()