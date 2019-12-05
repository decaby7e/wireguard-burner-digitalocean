#!/usr/bin/python3

#NOTES FOR FUTURE:
# - Make a droplet object that can be passed to methods in here...
# - Fix issue where generate-wg-configs.sh has ufsit.ddns.net set by default
# - Make parameters to be passed to generate-wg-configs.sh
# - !!! Start using Droplet object to simplify code !!!

import json
import requests

import uuid

import os
import time

from random import randint

## Variables ##

# Droplet variables
droplet_name = str(uuid.uuid1())
droplet_ip = 'unknown'
droplet_id = 'unknown'
droplet_region = "nyc3"

# API variables
api_url_base = 'https://api.digitalocean.com/v2/'
secrets = json.load(open('secrets.json', 'r'))
api_token = secrets['user_token']

ssh_pubkey = secrets['ssh_pubkey']
ssh_key_fingerprint = secrets['ssh_fingerprint']

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {0}'.format(api_token)}

# Miscelaneous
ssh_prefix=''

## Methods ##

def add_ssh_key():
  curr_url = '{0}account/keys'.format(api_url_base)

  data = json.dumps(
    {
      "name": "{0}".format(droplet_name),
      "public_key": "{0}".format(ssh_pubkey)
    }
  )

  requests.post(curr_url, data=data, headers=headers)

def del_ssh_key():
  curr_url = '{0}account/keys/{1}'.format(api_url_base, ssh_key_fingerprint)

  requests.delete(curr_url, headers=headers)

def create_droplet():
  global droplet_id, droplet_ip, ssh_prefix
  
  curr_url = '{0}droplets'.format(api_url_base)

  data = json.dumps({
    "name": "{0}".format(droplet_name),
    "region": "{0}".format(droplet_region),
    "size": "s-1vcpu-1gb",
    "image": "ubuntu-18-04-x64",
    "ssh_keys": ["{0}".format(ssh_key_fingerprint)],
    "backups": False,
    "ipv6": False,
    "user_data": None,
    "private_networking": None,
    "volumes": None,
    "tags": None})

  droplet = requests.post(curr_url, headers=headers, data=data).json()
  droplet_id = droplet["droplet"]["id"]

  curr_url = '{0}droplets/{1}'.format(api_url_base, droplet_id)
  droplet = requests.get(curr_url, headers=headers).json()
  
  droplet_ip = droplet["droplet"]["networks"]["v4"][0]["ip_address"]
  ssh_prefix='ssh -o StrictHostKeyChecking=no -i {0} root@{1}'.format('privkey', droplet_ip)

def destroy_droplet(droplet_id):
  curr_url = '{0}droplets/{1}'.format(api_url_base, droplet_id)

  requests.delete(curr_url, headers=headers)

def init_wg():

  cmd = '{0} \'apt update && add-apt-repository ppa:wireguard/wireguard && apt install -y wireguard git python\''.format(ssh_prefix)
  os.system(cmd)

  print("DEBUG: Getting config starter script...") #DEBUG
  cmd = '{0} \'git clone https://github.com/decaby7e/wireguard-management\''.format(ssh_prefix)
  os.system(cmd)

  print("DEBUG: Generating Wireguard configs...") #DEBUG
  cmd = '{0} \'wireguard-management/generate-wg-configs.sh; cp configs/server/wg0.conf /etc/wireguard/\''.format(ssh_prefix)
  os.system(cmd)

  print("DEBUG: Serving up client configs...") #DEBUG
  listen_port = randint(20000, 50000)
  print('Visit {0}:{1} for configuration files.'.format(droplet_ip, listen_port))
  cmd = '{0} \'python -m SimpleHTTPServer {1}\''.format(ssh_prefix, listen_port)
  os.system(cmd)

  
  print("DEBUG: Enabling ipv4 forwarding...") #DEBUG
  cmd = '{0} \'sysctl -w net.ipv4.ip_forward=1\''.format(ssh_prefix)
  os.system(cmd)

  print("DEBUG: Starting Wireguard server...") #DEBUG
  cmd = '{0} \'wg-quick up wg0\''.format(ssh_prefix)
  os.system(cmd)

## Main ##

def main():
  global ssh_prefix

  server_online = False

  print("> Adding SSH key...")
  add_ssh_key()

  print("> Creating Droplet...")
  create_droplet()

  # #Wait a little for the server to get up and ready for SSH connetions
  # print("DEBUG: Waiting a bit before installing Wireguard...") #DEBUG
  # time.sleep(60)

  print("> Waiting for server to come online...")
  while not server_online:
    cmd = '{0} \'echo Connection Established\''.format(ssh_prefix)
    if(os.system(cmd) == 0):
      server_online = True
      

  print("> Installing Wireguard...")
  init_wg()
  
  input("Press any key to nuke instance. (DISABLE VPN ON CLINET BEFORE NUKING)")
  
  print("> Removing Droplet...")
  destroy_droplet(droplet_id)
  
  print("> Removing SSH key...")
  del_ssh_key()

main()