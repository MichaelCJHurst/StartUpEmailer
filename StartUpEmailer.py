"""
StartUp Emailer
Sends an email via Google's api, to be used when turned on
"""
#!/usr/bin/env python
# coding: Latin-1
import datetime
import os
import smtplib
import socket
from   configparser import SafeConfigParser
from   email.mime.text import MIMEText

def main():
	""" Where the program starts """
	# Get the values from the config
	config = read_config()
	# Then get the IP address
	ip_address = get_ip_address()
	# If there is no IP address, return
	if ip_address is None:
		return
	# Then use both the config and ip address to write the subject and message
	subject = parse(config["subject"], ip_address)
	body    = parse(config["message"], ip_address)
	# Send the email
	send_email(config, subject, body)

def read_config():
	""" Reads the contents of the config file """
	parser = SafeConfigParser()
	config = {}
	parser.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "StartUpEmailer.ini"))
	# Addresses
	config["toAddress"]    = parser.get("email",   "toAddress")
	config["fromAddress"]  = parser.get("email",   "fromAddress")
	config["fromPassword"] = parser.get("email",   "fromPassword")
	# Config
	config["fromType"]     = parser.get("config",  "fromType")
	# Message
	config["subject"]      = parser.get("message", "subject")
	config["message"]      = parser.get("message", "message")
	# Return the configuration
	return config

def get_ip_address():
	""" Gets the IP address of this device """
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.connect(("8.8.8.8", 80))
		ip_address = sock.getsockname()[0]
		sock.close()
	except OSError:
		return None
	return ip_address

def parse(text, ip_address):
	""" Writes the email subject and body """
	today = datetime.date.today().strftime("%b %d %Y")
	machine_name = socket.getfqdn()
	# Parse the string
	text = text.replace("{IP_ADDRESS}",   ip_address)
	text = text.replace("{TODAY}",        today)
	text = text.replace("{MACHINE_NAME}", machine_name)
	return text

def send_email(config, subject, body):
	""" Sends the email """
	# If gmail - the only working version for now
	if config["fromType"] == "gmail":
		# Set up the SMTP server
		smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
		smtp_server.ehlo()
		# Start encrypting
		smtp_server.starttls()
		# Log in to the smtp server
		smtp_server.login(config["fromAddress"], config["fromPassword"])
		# prepare the email for sending
		email            = MIMEText(body)
		email["Subject"] = subject
		email["From"]    = config["fromAddress"]
		email["To"]      = config["toAddress"]
		# Send the email
		smtp_server.sendmail(config["fromAddress"], [config["toAddress"]], email.as_string())
		# Close the smtp server
		smtp_server.quit()
	else:
		print("Invalid from type")
	return

if __name__ == "__main__":
	main()
