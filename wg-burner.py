#!/usr/bin/python3

from Droplet import Droplet

import json
import requests

import uuid

import os
import time
from random import randint

api_url_base = 'https://api.digitalocean.com/v2/'

## Methods ##

def add_ssh_key(token, name, pubkey):
  curr_url = '{0}account/keys'.format(api_url_base)

  headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(token)
        }

  data = json.dumps(
    {
      "name": "{0}".format(name),
      "public_key": "{0}".format(pubkey)
    }
  )

  requests.post(curr_url, data=data, headers=headers)

def del_ssh_key(token, fingerprint):
  curr_url = '{0}account/keys/{1}'.format(api_url_base, fingerprint)

  headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer {0}'.format(token)
          }

  requests.delete(curr_url, headers=headers)

def init_wg(droplet):
  droplet.run('apt update && add-apt-repository ppa:wireguard/wireguard && apt install -y wireguard git python qrencode')

  droplet.run('git clone https://github.com/decaby7e/wireguard-management')

  droplet.run('wireguard-management/generate-wg-configs.sh -i {0}; cp configs/server/wg0.conf /etc/wireguard/'.format(droplet.ip))

  # INSECURE: Exposes client and server private keys
  # print("DEBUG: Serving up client configs...") #DEBUG
  # listen_port = randint(20000, 50000)
  # print('Visit {0}:{1} for configuration files.'.format(droplet.ip, listen_port))
  # print('Press ctrl-c when finished.')
  # cmd = 'python -m SimpleHTTPServer {0}'.format(listen_port)
  # droplet.run(cmd)

  droplet.run('qrencode -t ansiutf8 < configs/client-2/wg2.conf')
  input('> Press enter when done.')

  droplet.run('sysctl -w net.ipv4.ip_forward=1')

  droplet.run('wg-quick up wg0')

## Main ##

def main():
  global droplet

  secrets = json.load(open('secrets.json', 'r'))
  token=secrets['user_token']
  droplet = Droplet(token, str(uuid.uuid1()), 'nyc3', secrets['ssh_fingerprint'])

  print("> Adding SSH key...")
  add_ssh_key(token, droplet.name, secrets['ssh_pubkey'])

  print("> Creating Droplet...")
  droplet.create()

  server_online = False
  print("> Waiting for server to come online...")
  while not server_online:
    if(droplet.run('echo Connection Established') == 0):
      server_online = True

  print("> Starting Instance...")
  init_wg(droplet)
  
  input("Press any key to nuke instance. (DISABLE VPN ON CLINET BEFORE NUKING)")
  
  print("> Removing Droplet...")
  droplet.destroy()
  
  print("> Removing SSH key...")
  del_ssh_key(token, secrets['ssh_fingerprint'])

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print('Error: {0}'.format(e))
    print('Error: Exception caught. Cleaning up...')
    droplet.destroy()
