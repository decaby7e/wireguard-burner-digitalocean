#!/usr/bin/python3

from Droplet import Droplet
from SSH_Keys import SSH_Keys
from Account import Account

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

## Main ##

def main():
  global droplet
  global token
  global fingerprint

  name = 'burner-' + str( uuid.uuid1() )
  keyfile = 'auth/burnerkey'

  try:
    secrets = json.load(open('auth/secrets.json', 'r'))
    token = secrets['user_token']
  except IOError:
    print_error('secrets.json not found')
    return 1
  
  keys = SSH_Keys(keyfile)
  keys.init()
  fingerprint = keys.get_pubkey_fingerprint()
  pubkey = keys.get_pubkey_ssh()

  account = Account(token)
  droplet = Droplet(token, name, 'nyc3', keyfile, fingerprint)

  print("> Adding SSH key...")
  account.add_ssh_key(name, pubkey)

  print("> Creating Droplet...")
  droplet.create()

  print("> Waiting for server to come online...")
  while not droplet.is_online():
    print('> Server offline. Trying again...')
    time.sleep(3)

  print("> Starting Instance...")
  init_wg(droplet)
  
  input("> Press any key to nuke instance. (DISABLE VPN ON CLINET BEFORE NUKING)")
  
  print("> Removing Droplet...")
  droplet.destroy()
  
  print("> Removing SSH key...")
  account.del_ssh_key(fingerprint)

## Handlers ##

def sigint_handler(signal_received, frame):
  print('> SIGINT caught. Cleaning up...')
  cleanup()
  exit(0)

def cleanup():
  try:
    droplet.destroy()
    account.del_ssh_key(fingerprint)
    print('> SSH Keys removed')
  except Exception as e:
    print_error(e)
    print_error('Could not complete cleanup. Were all objects created?')

def print_error(message):
  print('Error: {}'.format(message))

## Runner ##

if __name__ == '__main__':
  try:
    signal(SIGINT, sigint_handler)
    main()
  except Exception as e:
    print_error(e)
    print_error('Exception caught. Cleaning up...')
    cleanup()
