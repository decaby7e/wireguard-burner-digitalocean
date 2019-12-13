#!/usr/bin/python3

import json
import time
import sys

sys.path.append('../src')

from SSH_Keys import SSH_Keys
from Droplet import Droplet
from Account import Account

def main():
    global droplet
    global account

    try:
        secrets = json.load(open('secrets.json', 'r'))
        token = secrets['user_token']
    except IOError:
        print_error('secrets.json not found')
        return 1

    keys = SSH_Keys('unit-test')

    keys.init()

    privfile = keys.name
    fingerprint = keys.get_pubkey_fingerprint()

    print(privfile)
    print(fingerprint)

    account = Account(token)

    account.add_ssh_key('unit-test', keys.get_pubkey_ssh())

    droplet = Droplet(token, 'unit-test', 'nyc3', privfile, fingerprint)

    droplet.create()
    
    time.sleep(20)

    droplet.run('echo Hello world!')

    droplet.destroy()

    account.del_ssh_key(keys.get_pubkey_fingerprint())

def cleanup():
    droplet.destroy()

    account.del_ssh_key(keys.get_pubkey_fingerprint())

if __name__ == '__main__':
    try:
        main()
    except ValueError:
        cleanup()