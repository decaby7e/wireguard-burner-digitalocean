#!/usr/bin/python3

import requests
import json

class Account:
    api_url_base = 'https://api.digitalocean.com/v2/'

    def __init__(self, token):
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(token)
        }

    def add_ssh_key(self, name, pubkey_string):
        curr_url = '{0}account/keys'.format(Account.api_url_base)

        data = json.dumps(
            {
            "name": "{0}".format(name),
            "public_key": "{0}".format(pubkey_string)
            }
        )

        requests.post(curr_url, data=data, headers=self.headers)

    def del_ssh_key(self, token, fingerprint):
        global api_url_base

        curr_url = '{0}account/keys/{1}'.format(Account.api_url_base, fingerprint)

        requests.delete(curr_url, headers=self.headers)