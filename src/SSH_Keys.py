#!/usr/bin/python3

import hashlib
import base64
from Crypto.PublicKey import RSA
import os

class SSH_Keys:
    def __init__(self, name):
        self.name = name
        self.fingerprint = None

    def generate_private_key(self):
        self.privkey = RSA.generate(2048)

    def generate_public_key(self):
        self.pubkey = self.privkey.publickey()

    def write_privkey_file(self):
        f = open(self.name, "wb")
        f.write(self.privkey.exportKey('PEM'))
        f.close()
        os.system('chmod 600 {0}'.format(self.name))

    def write_pubkey_file(self):
        f = open("{0}.pub".format(self.name), "wb")
        f.write(self.pubkey.exportKey('OpenSSH'))
        f.close()

    def init(self):
        self.generate_private_key()
        self.generate_public_key()
        self.write_privkey_file()
        self.write_pubkey_file()
        self.get_pubkey_fingerprint( self.pubkey )

    def get_pubkey_fingerprint(self, pubkey):
        if self.fingerprint == None:
            pubkey_string = str( pubkey.exportKey('OpenSSH'), 'utf-8' ).split()[1]
            rawhex = hashlib.md5( base64.b64decode(pubkey_string) ).hexdigest()
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

        
        

if __name__ == '__main__':
    ssh_key = SSH_Key('test_key')
    ssh_key.init()
