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
foo_ip_range = ip_network('10.1.1.0/16', strict=False)
bar_ip_range = ip_network('10.1.2.0/16', strict=False)


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

    foo_strong = foo_soup.find('strong', string='IP Address:')
    # print(foo_strong)
    bar_strong = bar_soup.find('strong', string='IP Address:')

    if foo_strong and bar_strong:
        foo_ip_text = foo_strong.next_sibling.strip()
        # print(foo_ip_text)
        bar_ip_text = bar_strong.next_sibling.strip()

        if foo_ip_text and bar_ip_text:
            foo_ip = ip_address(foo_ip_text)
            #print(type(foo_ip))
            bar_ip = ip_address(bar_ip_text)

            # Check if the private IP addresses are in the correct ranges
            if foo_ip in foo_ip_range and bar_ip in bar_ip_range:
                print('The student has correctly set up the instances and the ALB.')
                # Store the private IP addresses in the data.json file
                data['foo-instance-private-ip'] = str(foo_ip)
                data['bar-instance-private-ip'] = str(bar_ip)
            else:
                print('The instances or the ALB are not correctly set up.')
        else:
            print('Could not find IP addresses in the responses.')
    else:
        print('Could not find the expected text in the responses.')




# Save the data back to data.json
try:
    with open('data.json', 'w') as f:
        json.dump(data, f)
except IOError:
    print("Error occurred while writing to data.json.")
