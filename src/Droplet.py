#!/usr/bin/python3

import json
import requests
import os
import subprocess
import time

class Droplet:
    def __init__(self, token, name, region, ssh_privkey_file, ssh_key_fingerprint):
        self.api_url_base = 'https://api.digitalocean.com/v2/'
        self.status = 'destroyed'
        
        self.token = token
        self.name = name
        self.region = region

        self.privkey = ssh_privkey_file
        self.ssh_key_fingerprint = ssh_key_fingerprint
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(self.token)
        }

    #Creates a new Droplet with the given information
    def create(self):
        # Create a new Droplet with object information
        active_url = '{0}droplets'.format(self.api_url_base)
        data = json.dumps({
            "name": "{0}".format(self.name),
            "region": "{0}".format(self.region),
            "size": "s-1vcpu-1gb",
            "image": "ubuntu-18-04-x64",
            "ssh_keys": ["{0}".format(self.ssh_key_fingerprint)],
            "backups": False,
            "ipv6": False,
            "user_data": None,
            "private_networking": None,
            "volumes": None,
            "tags": None})
        response = requests.post(active_url, headers=self.headers, data=data)
        

        if response:
            new_droplet = response.json()
            self.id = new_droplet["droplet"]["id"]
            self.status = 'created'

            print( 'Droplet {0} created.'.format(self.id) )
        else:
            print( 'Error: {0}'.format(response.json()['message']) )
            return False


        # Give some time between creation and getting the full Droplet information
        time.sleep(2)


        # Get the full Droplet JSON
        active_url='{0}droplets/{1}'.format(self.api_url_base, self.id)
        response = requests.get(active_url, headers=self.headers)
        
        if response:
            self.droplet_JSON = response.json()
            self.ip = self.droplet_JSON["droplet"]["networks"]["v4"][0]["ip_address"]
            print ( 'Droplet IP: {0}'.format(self.ip) )
            return True
        else:
            return False

    #Destroys the Droplet
    def destroy(self):
        if(self.status == 'created'):
            active_url = '{0}droplets/{1}'.format(self.api_url_base, self.id)
            requests.delete(active_url, headers=self.headers)

            print( 'Droplet {0} destroyed.'.format(self.id) )

            self.status = 'destroyed'
            self.id = None
            self.ip = None
            self.droplet_JSON = None

            return True
        
        else:
            return False

    #Runs a command in the Droplet given a command and a private key
    def run(self, command_string):
        if self.status == 'created':
            ssh_prefix='ssh -o StrictHostKeyChecking=no -i {0} root@{1}'.format(self.privkey, self.ip)
            cmd='{0} \' {1} \''.format(ssh_prefix, command_string)
            
            return os.system(cmd)
        
        else:
            return None