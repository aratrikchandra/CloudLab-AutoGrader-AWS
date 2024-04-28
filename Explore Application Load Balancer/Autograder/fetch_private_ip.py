import json
import requests
from bs4 import BeautifulSoup
from ipaddress import ip_network, ip_address

# Get the client's public IP
try:
    client_ip = requests.get('https://api.ipify.org').text
except requests.exceptions.RequestException as e:
    print(f"Error occurred while getting client's public IP: {str(e)}")
    client_ip = None

# Load the DNS name of the ALB from the data.json file
try:
    with open('data.json') as f:
        data = json.load(f)
except FileNotFoundError:
    print("data.json file not found.")
    data = {}

# Store the client's public IP in data.json
data['client-ip'] = client_ip

# Define the IP address ranges for the instances
foo_ip_range = ip_network('10.1.0.0/16')
bar_ip_range = ip_network('10.2.0.0/16')

# Send requests to the /foo and /bar routes
try:
    foo_response = requests.get(f'http://{data["DNS_name_of_ALB"]}/foo')
    bar_response = requests.get(f'http://{data["DNS_name_of_ALB"]}/bar')
except requests.exceptions.RequestException as e:
    print(f"Error occurred while sending requests: {str(e)}")
    foo_response = bar_response = None

# Parse the responses to extract the private IP addresses
if foo_response and bar_response:
    foo_soup = BeautifulSoup(foo_response.text, 'html.parser')
    bar_soup = BeautifulSoup(bar_response.text, 'html.parser')

    foo_ip = ip_address(foo_soup.find('p', text=lambda t: t and 'IP Address:' in t).split(': ')[1])
    bar_ip = ip_address(bar_soup.find('p', text=lambda t: t and 'IP Address:' in t).split(': ')[1])

    # Check if the private IP addresses are in the correct ranges
    if foo_ip in foo_ip_range and bar_ip in bar_ip_range:
        print('The student has correctly set up the instances and the ALB.')
        # Store the private IP addresses in the data.json file
        data['foo-instance-private-ip'] = str(foo_ip)
        data['bar-instance-private-ip'] = str(bar_ip)
    else:
        print('The instances or the ALB are not correctly set up.')

# Save the data back to data.json
try:
    with open('data.json', 'w') as f:
        json.dump(data, f)
except IOError:
    print("Error occurred while writing to data.json.")
