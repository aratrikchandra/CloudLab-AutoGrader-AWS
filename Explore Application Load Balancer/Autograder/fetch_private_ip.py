import json
import requests
from bs4 import BeautifulSoup
from ipaddress import ip_network, ip_address

# Load the DNS name of the ALB from the data.json file
with open('data.json') as f:
    data = json.load(f)
alb_dns_name = data['DNS_name_of_ALB']

# Define the IP address ranges for the instances
foo_ip_range = ip_network('10.1.0.0/16')
bar_ip_range = ip_network('10.2.0.0/16')

# Send requests to the /foo and /bar routes
foo_response = requests.get(f'http://{alb_dns_name}/foo')
bar_response = requests.get(f'http://{alb_dns_name}/bar')

# Parse the responses to extract the private IP addresses
foo_soup = BeautifulSoup(foo_response.text, 'html.parser')
bar_soup = BeautifulSoup(bar_response.text, 'html.parser')

foo_ip = ip_address(foo_soup.find('p', text=lambda t: t and 'IP Address:' in t).split(': ')[1])
bar_ip = ip_address(bar_soup.find('p', text=lambda t: t and 'IP Address:' in t).split(': ')[1])

with open('data.json', 'w') as f:
    json.dump(data, f)

# Check if the private IP addresses are in the correct ranges
if foo_ip in foo_ip_range and bar_ip in bar_ip_range:
    print('The student has correctly set up the instances and the ALB.')
    # Store the private IP addresses in the data.json file
    data['foo_private_ip'] = str(foo_ip)
    data['bar_private_ip'] = str(bar_ip)
else:
    print('The instances or the ALB are not correctly set up.')
