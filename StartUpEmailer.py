#!/usr/bin/env python
# coding: Latin-1
import subprocess
import smtplib
import datetime
import socket
import fcntl
import struct
from   email.mime.text import MIMEText
from   configparser    import SafeConfigParser

#	Read the settings from the attached config FileExistsError
config = SafeConfigParser()
config.read("StartUpEmailer.ini")
#	Addresses
toAddress    = config.get("email",   "toAddress")
fromAddress  = config.get("email",   "fromAddress")
fromPassword = config.get("email",   "fromPassword")
#	Config
fromType     = config.get("config",  "fromType")
#	Message
subject      = config.get("message", "subject")
message      = config.get("message", "message")
#	Set up the lo, wlan0, today, and machine name values
global eth0IP
global loIP
global wlan0IP
global today
global machineName
eth0IP      = "No IP Found"
loIP        = "No IP Found"
wlan0IP     = "No IP Found"
today       = datetime.date.today()  # Get current time/date
machineName = socket.getfqdn()

#	Get the IP address via technowizardry
def getIPAddress(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR, whatever that is
		struct.pack('256s', bytes(ifname[:15], 'utf-8'))
	)[20:24])

#	Parse any string with the provided IP addresses and machine address
def parseIPs(text):
	global eth0IP
	global loIP
	global wlan0IP
	global today
	global machineName
	text = text.replace("{ETH0_IP}",      eth0IP)
	text = text.replace("{LO_IP}",        loIP)
	text = text.replace("{WLAN0_IP}",     wlan0IP)
	text = text.replace("{TODAY}",        today.strftime("%b %d %Y"))
	text = text.replace("{MACHINE_NAME}", machineName)
	return text

#	Set up the SMTP server
smtpserver = smtplib.SMTP('smtp.gmail.com', 587) # Server to use.
smtpserver.ehlo()  # Says 'hello' to the server
smtpserver.starttls()  # Start TLS encryption
smtpserver.ehlo()
smtpserver.login(fromAddress, fromPassword)  # Log in to server
#	eth0
try:
	eth0IP = getIPAddress("eth0")
except OSError:
	eth0IP = "No IP found"
#	lo
try:
	loIP = getIPAddress("lo")
except OSError:
	loIP = "No IP found"
#	wlan0
try:
	wlan0IP = getIPAddress("wlan0")
except OSError:
	wlan0IP = "No IP found"
#	Ready the email for sending
email            = MIMEText(parseIPs(message))
email["Subject"] = parseIPs(subject)
email["From"]    = fromAddress
email["To"]      = toAddress
#	Send the email
smtpserver.sendmail(fromAddress, [toAddress], email.as_string())
#	Close the smtp server
smtpserver.quit()