#!/usr/bin/python3

from Droplet import Droplet

import json
import requests

import uuid

import hashlib
import base64
from Crypto.PublicKey import RSA

import os
from sys import exit
from signal import signal, SIGINT

import time
from random import randint

api_url_base = 'https://api.digitalocean.com/v2/'
droplet = None

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

  # NOT FLEXIBLE: Only shows QR code! Maybe use as an option...
  # droplet.run('qrencode -t ansiutf8 < configs/client-2/wg2.conf')
  # input('> Press enter when done.')

  droplet.run('cat configs/client-2/wg2.conf')

  droplet.run('sysctl -w net.ipv4.ip_forward=1')

  droplet.run('wg-quick up wg0')

def gen_ssh_keys(keyfile):
  key = RSA.generate(2048)
  f = open(keyfile, "wb")
  f.write(key.exportKey('PEM'))
  f.close()

  pubkey = key.publickey()
  f = open("{0}.pub".format(keyfile), "wb")
  f.write(pubkey.exportKey('OpenSSH'))
  f.close()

  os.system('chmod 600 {0}'.format(keyfile))

def gen_fingerprint(ssh_pubkey):
  pubkey = ssh_pubkey.split()[1]
  rawhex = hashlib.md5(base64.b64decode(pubkey.encode('utf-8'))).hexdigest()
  newhex = ''
  count = 0

  for i in rawhex:
    if(count == 2):
      newhex += ':'
      newhex += i
      count = 0
    else:
      newhex += i
    
    count += 1

  return newhex

def print_error(message):
  print('Error: {}'.format(message))

## Main ##

def main():
  global droplet
  global token
  global fingerprint

  try:
    secrets = json.load(open('auth/secrets.json', 'r'))
    token = secrets['user_token']
  except IOError:
    print_error('secrets.json not found')
    return 1
  
  keyfile = 'auth/burnerkey'
  gen_ssh_keys(keyfile)

  privkey = open(keyfile).read()
  ssh_pubkey = open('{0}.pub'.format(keyfile), 'r').read()
  fingerprint = gen_fingerprint(ssh_pubkey)

  droplet = Droplet(token, 'burner-' + str( uuid.uuid1() ), 'nyc3', keyfile, fingerprint)

  print("> Adding SSH key...")
  add_ssh_key(token, droplet.name, ssh_pubkey)

  print("> Creating Droplet...")
  droplet.create()

  server_online = False
  print("> Waiting for server to come online...")
  while not server_online:
    print(droplet.run('echo Connection Established')[1])
    if(droplet.run('echo Connection Established')[1] == 0):
      server_online = True
    else:
      time.sleep(3)

  print("> Starting Instance...")
  init_wg(droplet)
  
  input("> Press any key to nuke instance. (DISABLE VPN ON CLINET BEFORE NUKING)")
  
  print("> Removing Droplet...")
  droplet.destroy()
  
  print("> Removing SSH key...")
  del_ssh_key(token, fingerprint)

def sigint_handler(signal_received, frame):
  print('> SIGINT caught. Cleaning up...')
  cleanup()
  exit(0)

def cleanup():
  try:
    droplet.destroy()
    del_ssh_key(token, fingerprint)
    print('> SSH Keys removed')
  except:
    print_error('Could not destroy droplets. Were they created?')

if __name__ == '__main__':
  try:
    signal(SIGINT, sigint_handler)
    main()
  except Exception as e:
    print_error(e)
    print_error('Exception caught. Cleaning up...')
    cleanup()
