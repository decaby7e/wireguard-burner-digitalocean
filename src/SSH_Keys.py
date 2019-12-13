#!/usr/bin/python3

import hashlib
import base64

from Crypto.PublicKey import RSA

import os

class SSH_Keys:
    def __init__(self, name):
        self.name = name
        self.fingerprint = None

    ## Generator methods ##

    def generate_private_key(self):
        self.privkey = RSA.generate(2048)

    def generate_public_key(self):
        self.pubkey = self.privkey.publickey()

    ## Writer methods ##

    def write_privkey_file(self):
        f = open(self.name, "wb")
        f.write(self.privkey.exportKey('PEM'))
        f.close()
        os.system('chmod 600 {0}'.format(self.name))

    def write_pubkey_file(self):
        f = open("{0}.pub".format(self.name), "wb")
        f.write(self.pubkey.exportKey('OpenSSH'))
        f.close()

    ## Remover methods ##

    def del_privkey_file(self):
        os.remove(self.name)

    def del_pubkey_file(self):
        os.remove('{}.pub'.format(self.name))

    ## Getter methods ##

    def get_pubkey_fingerprint(self):
        if self.fingerprint == None:
            pubkey_string = base64.b64decode(str( self.pubkey.exportKey('OpenSSH'), 'utf-8' ).split()[1])
            rawhex = hashlib.md5( pubkey_string ).hexdigest()
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

            self.fingerprint = newhex
            return newhex
        
        else:
            return self.fingerprint

    def get_pubkey_ssh(self):
        return str( self.pubkey.exportKey('OpenSSH'), 'utf-8' )

    ## Init and cleanup methods ##

    def init(self):
        self.generate_private_key()
        self.generate_public_key()
        self.write_privkey_file()
        self.write_pubkey_file()
        self.get_pubkey_fingerprint()

    def cleanup(self):
        self.del_privkey_file()
        self.del_pubkey_file()

   