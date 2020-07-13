# Wireguard Burner Script(s)

Create a Wireguard VPN for one-time use and destroy it once finished.

## Structure

This project is split into two seperate components: the Droplet object and the management script that handles creating, destroying, and configuring the VPN.
For a full project description, [please read this blog post](https://blog.ranvier.net/2019/11/wireguard-burner-vpn/).

## Setup

To run this script, please follow these steps:

1. Install the requirements: `pip install -r requirements.txt`

2. Create a secrets.json file in the script directory and fill out your appropriate information.

  1. To create a Digital Ocean API key, [please see this tutorial](https://www.digitalocean.com/docs/api/create-personal-access-token/).


3. Run the script! `./run.sh`

## To Do

- [ ] Add parameters to wg-burner.py to specify number of clients, time to keep server up, etc.

- [ ] In the future, it is possible that I will move the Droplet object to its own repository with some additonal content.

- [ ] Find a better way to wait for the droplet to come online. (Current implementation just bombards the server with SSH requests until it accepts one...)

- [ ] Add support for other cloud providers

- [ ] Proper client interface (for Windows, Mac, Linux, Android, and iOS)
