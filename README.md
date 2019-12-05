# Wireguard Burner Script(s)
Create a Wireguard VPN for one-time use and destroy it once finished.

## Structure

This project is split into two seperate components: the Droplet object and the management script that handles creating, destroying, and configuring the VPN.
For a full project description, [please read this blog post](https://blog.ranvier.net/2019/11/wireguard-burner-vpn/).

In the future, it is possible that I will move the Droplet object to its own repository.

## Setup

To run this script, please follow these steps:

1. Install the requirements: `pip install -r requirements.txt`

2. Create a secrets.json file in the script directory and fill out your appropriate information.

   2a. The script currently depends on SSH public and private key *files* in the script directory.
       To create these: `ssh-keygen -t rsa -b 4096 -C "temp-ssh-key" -f privkey`

   2b. Generate your SSH fingerpint: `ssh-keygen -l -E md5 -f privkey.pub`

   2c. To create a Digital Ocean API key, [please see this tutorial](https://www.digitalocean.com/docs/api/create-personal-access-token/).

3. Run the script! `./wg-burner`

## Future improvements

- Add parameters to wg-burner.py to specify number of clients, time to keep server up, etc.

- Steps 2a - 2b will be automated in the future with an additional script.
