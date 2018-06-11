## Easy way to look at the Raspberry Pi video streams with a GUI
## for the Greenberg lab
## SCT June 2018

import paramiko
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
else:
	import tkinter as tk
import time
import socket
from raspberry_pi import Raspberry_Pi

def pi_connect(address,ID):
	## Connect to a raspberry pi at location address.
	try:
		ID = [address,ID]
		this_pi = Raspberry_Pi(ID,master)
		ListOfPis.append(this_pi)
	except socket.gaierror:
		print(sys.exc_info())
		connection_error()

def connection_error():
	error_window = tk.Toplevel(master)
	tk.Label(error_window,text="Error (I haven't implemented something to tell you exactly what yet).\nMake sure you're on HMS Private network and reset\nIf there's still a problem, call me (907-764-1248)").pack()
	tk.Button(error_window,text="OK",command=lambda: okay_error(error_window)).pack()

def okay_error(error_window):
	error_window.destroy()
	close_down()

def close_down():
	for pi in ListOfPis:
		pi.close_pi()
	master.destroy()

def add_address():
	pass

master = tk.Tk()
master.title('Raspberry Pi Manager')
menubar = tk.Menu(master,tearoff=0)
menubar.add_command(label="New address", command=lambda: add_address())
menubar.add_command(label="Quit", command=master.quit)
master.config(menu=menubar)

ListOfPis = []

tk.Label(master, text="Pi address").grid(row=0)

# PUT THE IP ADDRESSES OF EACH PI HERE
# you can use a dictionary to make aliases and do it that way
# if you need help remembering who's who
ListOfAddresses=[ "10.119.221.142",
	"10.119.214.244",
	"10.444.235.26"]

ListOfAliases=["Box 1",
	"Box 2",
	"Not a real Pi"]

alias_address_map = dict(zip(ListOfAliases,ListOfAddresses))

add = tk.StringVar(master)
add.set(ListOfAliases[0]) # default value

w = tk.OptionMenu(master, add, *ListOfAliases)
w.grid(row=0, column=1)
print(alias_address_map[add.get()],add.get())
conn_button = tk.Button(master, text='Connect', command=lambda: pi_connect(alias_address_map[add.get()],add.get()))
conn_button.grid(row=0, column=2)
tk.Button(master, text='Quit', command=lambda: close_down()).grid(row=7, column=0, pady=4)
master.mainloop()
