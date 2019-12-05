#!/bin/bash

usage() {
    echo "Usage: generate-ssh-key.sh [-l keyfile] | [-c keyfile]"
    echo "-l     Prints out the MD5 fingerprint of the specified key"
    echo "-c     Creates a key with name 'keyfile'"
}

# print_key_fingerprint(String keyfile)
print_key_fingerprint() {

  if [ -e $1 ]; then
    echo $(ssh-keygen -l -E md5 -f $1 | cut -d ' ' -f 2 | cut -c 5-)
  else
    echo "Error: File does not exist."
  fi
}

#generate_key(String filename)
generate_key() {
    ssh-keygen -t rsa -b 4096 -C "$1" -f $1
}

if (( $# == 0 )); then
    echo "Error: Not enough arguments."
    usage
    exit 1
elif [ $1 == "-c" ]; then
    if [ -e $2 ]; then
        echo "Error: File already exists."
    else
        generate_key $2
    fi
elif [ $1 == "-l" ]; then
    print_key_fingerprint $2
else
    usage
    exit 1
fi
