import bluetooth as bt
import socket
import threading
from PyOBEX.client import Client

def bluetooth( target_name, file_name ):

	file_contents = read_file( file_name )
	if file_contents == "":
		return 0

	target_address = None
	nearby_devices = bt.discover_devices()

	for bdaddr in nearby_devices:
		if target_name == bt.lookup_name( bdaddr ):
			target_address = bdaddr
			break

	if target_address is not None:
		print( "Found device with MAC Address:  " + target_address )
	else:
		print( "Couldn't find device" )
		return 0

	services = bt.find_service(address = target_address, name = b'OBEX Object Push\x00' )

	if len(services)==0:
		print( "Couldn't find service" )
		return 0

	first_match = services[0]
	port = first_match["port"]
	name = first_match["name"]
	host = first_match["host"]


	client = Client( host, port )
	client.connect()
	client.put( file_name, file_contents )
	client.disconnect()
	return 1

def get_device():
	device_name = raw_input("What is your device name?\n")
	return device_name

def get_method():
	while True:
		method = raw_input("Would you rather use Wifi or Bluetooth? Please type BT or Wifi\n")
		if method != "BT" and method != "Wifi":
			print( "That is not Bluetooth or Wifi" )
		else:
			return method

def get_file_name():
	file_name = raw_input( "What file would you like to send?\n" )
	return file_name


def get_file_name_rcv():
	file_name = raw_input( "What would you like to name this file?\n" )
	return file_name

def read_file(file_name):
	try:
		with open( file_name, "rb" ) as file:
			fileContent = file.read()
			return fileContent
	except IOError:
		print( "File does not exist" )
		return ""
		
def get_device_type():
	dev_type = raw_input( "Would you like to send to a computer or phone? Please enter p for phone or c for computer\n" )
	return dev_type

def get_ip():
	ip = raw_input( "Please enter IP address of device\n" )
	return ip

def get_dir():
	dir_type = raw_input( "Would you like to send or receive a file?\n" )
	return dir_type

def get_port():
	port_num = input( "Please enter port number.\n" )
	return port_num

def send_file():
	dev_type = get_device_type()

	if dev_type == "p":
		device = get_device()
		file_name = get_file_name()
		print( "Sending via bluetooth" )
		ret_val = bluetooth( device, file_name )
		if ret_val == 0:
			print( "Error sending file" )
		elif ret_val == 1:
			print( "Successfully sent file!" )
	elif dev_type == "c":
		dir_type = get_dir()
		
		if dir_type == "send":
			ip = get_ip()
			port_num = get_port()
			SendServer( ip, port_num ).write()
		elif dir_type == "receive":
			ip = get_ip()
			port_num = get_port()
			RcvServer( ip, port_num ).Listen()

class RcvServer( object ):
	def __init__( self, host, port ):
		self.host = host
		self.port = port
		self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.sock.bind( ( self.host, self.port ) )
		print( self.host, self.port )
	def Listen( self ):
		self.sock.listen( 5 )
		while( True ):
			client, address = self.sock.accept()
			print( "Receiving file"  )
			data = client.recv( 1000000000 )
			file_name = get_file_name_rcv()
			new_file = open( file_name, "wb" )
			new_file.write( data )
			print( "Successfully wrote new file" ) 
			new_file.close()
			client.close()
			self.sock.close()
			quit()
			
class SendServer( object ):
	def __init__( self, host, port ):
		self.host = host
		self.port = port
		self.file_name = get_file_name()
		self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.sock.connect( ( self.host, self.port ) )
		print( self.host, self.port )

	def write( self ):
		while( True ):
			print( "Sending to " + self.host )
			contents = read_file( self.file_name )
			self.sock.sendto( contents, (self.host, self.port) )
			self.sock.close()
			quit()

if __name__ == "__main__":
	send_file()
