import json
from retrieve_info import parse_alb_log

def verify_log_entry(log_entry, data, log):
    try:
        # Check if the log_entry is empty
        if not log_entry:
            #print("Log entry is empty.")
            return

        # Check if any key value in log_entry is empty
        for key, value in log_entry.items():
            if not value:
                # print(f"Value for {key} in log entry is empty.")
                return

        # Check if the client IP, client port, and ALB name match the content of data.json
        if log_entry['client_ip'] == data['client-ip'] and \
           log_entry['load_balancer_name'] == data['alb-name']:
            # If the log is related to "/foo" route
            if log_entry['requested_route'] == 'foo':
                # Check if the target group name and backend IP match the "/foo" route
                if log_entry['target_group_name'] != data['foo-target-group']:
                   print(f"Log entry does not match target group for /foo route. The log is: {log}")
                elif log_entry['backend_ip'] != data['foo-instance-private-ip']:
                    print(f"Log entry does not match backend instance ip for /foo route. The log is: {log}")
                else:
                    print(f'Log entry matches Target Group: {data["foo-target-group"]} and instance ip: {data["foo-instance-private-ip"]} for /foo route.')
            # If the log is related to "/bar" route
            elif log_entry['requested_route'] == 'bar':
                # Check if the target group name and backend IP match the "/bar" route
                if log_entry['target_group_name'] != data['bar-target-group']:
                   print(f"Log entry does not match target group for /bar route. The log is: {log}")
                elif log_entry['backend_ip'] != data['bar-instance-private-ip']:
                    print(f"Log entry does not match backend instance ip for /bar route. The log is: {log}")
                else:
                    print(f'Log entry matches Target Group: {data["bar-target-group"]} and instance ip: {data["bar-instance-private-ip"]} for /bar route.')
            else:
                print("Log entry is not related to /foo or /bar route.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Load data from data.json
try:
    with open('data.json') as json_file:
        data = json.load(json_file)
except FileNotFoundError:
    print("data.json file not found.")
    data = {}

# Open and read access.log file
try:
    with open('access.log', 'r') as log_file:
        for line in log_file:
            log_entry = parse_alb_log(line)
            verify_log_entry(log_entry, data, line)
except FileNotFoundError:
    print("access.log file not found.")
