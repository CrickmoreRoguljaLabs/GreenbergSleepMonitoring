# a way to keep all the buttons in one place for a window corresponding to a Pi
# The most spaghetti of codes. Perhaps some day I'll rewrite it to be pretty. For now, it just works.
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
	import tkinter as tk
from PIL import ImageTk, Image
import time
import os
#import multiprocessing
import threading

class Command_Window(object):
	def __init__(self, window, pi):
		self.window = window
		self.logFrame = tk.Frame(self.window)
		self.logFrame.pack(side=tk.LEFT)
		self.videoFrame = tk.Frame(self.window)
		self.videoFrame.pack(side=tk.RIGHT)
		self.button_dict = {}
		self.streaming = False
		self.pi = pi
		#self.stream = None
		self.panel = tk.Label(self.videoFrame)
		self.make_video_frame()
		#self.stop_vid = threading.Event()

	def set_title(self, title):
		self.window.title(title)
		self.title = title

	def quit_button(self,command):
		botFrame = tk.Frame(self.window)
		botFrame.pack(side=tk.BOTTOM, anchor=tk.SW)
		button = tk.Button(botFrame, text="Quit", command=command)
		button.pack(anchor=tk.W)
		self.button_dict["Quit"] = button

######################################
######################################
######### VIDEO AND STREAMING #########
######################################
######################################

	def make_video_frame(self):
		# establishes the frame for controlling the video stuff
		self.panel = tk.Label(self.videoFrame)
		self.start_vid_button = tk.Button(self.videoFrame,text="Start video",command = lambda: self.demo_start_video())
		self.start_vid_button.pack()
		self.video_name_entry = tk.Entry(self.videoFrame)
		self.video_name_entry.insert(0,"Name of the video")
		self.video_name_entry.pack()
		self.savevid = tk.IntVar()
		self.savevid_box = tk.Checkbutton(self.videoFrame, text="Save video", variable=self.savevid)
		self.savevid_box.pack()

	def demo_start_video(self):
		# for testing before ssh is implemented 
		self.start_vid_button.destroy()
		self.video_name = self.video_name_entry.get()
		if self.savevid:
			self.pi.create_video_file(self.video_name)
		else:
			self.pi.create_video_file()
		self.video_name_entry.destroy()
		self.savevid_box.destroy()

		#self.window.demo_play_video()
		self.stream_thread = threading.Thread(target=self.demo_play_video)
		self.stream_thread.start()
		self.stop_vid_button = tk.Button(self.videoFrame,text="Stop video",command = lambda: self.stop_video())
		self.stop_vid_button.pack(side=tk.BOTTOM)
		self.open_stream_button = tk.Button(self.videoFrame, text="Open stream", command = lambda: self.open_stream())
		self.open_stream_button.pack(side=tk.BOTTOM)

	def demo_play_video(self, port=8000):
		self.streaming = True
		name_label = tk.Label(self.videoFrame,text='%s' %(self.video_name))
		name_label.pack()
		while self.streaming:
			dir_path = os.path.dirname(os.path.realpath(__file__))
			image_path = "%s/cameraman.jpg" %(dir_path)
			img = ImageTk.PhotoImage(Image.open(image_path))
			self.panel.image = img
			self.panel.config(image = img)
			self.panel.pack()
		self.panel.destroy()
		name_label.destroy()
		self.make_video_frame()
		self.stop_vid_button.destroy()
		self.open_stream_button.destroy()

	def stop_video(self):
		self.streaming = False
		self.pi.terminate_video_file()

	def open_stream(self):
		self.stream_view_thread = threading.Thread(target=self.view_stream)
		self.stream_view_thread.start()

	def view_stream(self):
		# this is the hacky way using gstreamer without interfacing with tkinter. I will do it better soon
		receive_string = "gst-launch-1.0 tcpclientsrc host=%s port=5000 ! application/x-gdp, payload=96 ! gdpdepay ! rtph264depay ! decodebin ! autovideosink" %(self.pi.IP_ADDRESS,)
		os.system(receive_string)

###################################
##### NOTES AND LOGGING ###########
###################################

	def rename_log_button(self, expt):
		### Lets you rename the log
		try:
			self.rename_log_button.destroy()
		except:
			pass
		self.rename_log_button = tk.Button(self.logFrame, text='Rename log',command=lambda: self.rename_log(expt))
		self.rename_log_button.pack(side=tk.LEFT, anchor=tk.W)

	def rename_log(self, expt):
		### renames the log
		name_window = tk.Toplevel(self.window)
		name_window.title("Log name is %s" %(expt.name_of_video))
		name_entry = tk.Entry(name_window)
		name_entry.insert(tk.END, "Enter new name")
		name_entry.pack(side=tk.LEFT)
		addnote = tk.Button(name_window,command=lambda: self.change_name(name=name_entry.get(), expt=expt, window = name_window), text= "Rename") 
		addnote.pack()

	def change_name(self, name, expt, window):
		expt.change_name(name)
		window.destroy()

	def note_button(self, expt):
		### Creates an "add note" button, ties it to the current expt
		try:
			self.add_note_button.destroy()
		except:
			pass
		self.add_note_button = tk.Button(self.logFrame, text='Add note to log',command=lambda: self.add_note(expt))
		self.add_note_button.pack(side=tk.LEFT, anchor=tk.W)

	def add_note(self, expt):
		### Opens a new window to add a note
		note_window = tk.Toplevel(self.window)
		note_window.title("Add note to experiment (%s)" %(expt.name_of_log))

		# Custom notes
		custom_frame = tk.Frame(note_window)
		custom_frame.pack(side=tk.TOP)
		note_entry = tk.Entry(custom_frame)
		note_entry.insert(tk.END, "Type note here")
		note_entry.pack(side=tk.LEFT)
		addnote = tk.Button(custom_frame,command=lambda: expt.note_change(note_entry.get()), text = "Add note" ) 
		addnote.pack()

######################################
########## CLEAN UP ##################
######################################

	def remove_button(self,name_of_button):
		self.button_dict[name_of_button].pack_forget()

	def destroy(self):
		self.window.destroy()
