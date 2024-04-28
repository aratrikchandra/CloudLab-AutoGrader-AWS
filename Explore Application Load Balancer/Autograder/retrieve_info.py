import re

def parse_alb_log(log):

    # Define a regular expression to extract the status code from the end of the log
    status_code_regex = r'\"(\d{1,3})\" "-" "-"$'

    # Find the status code using the regular expression
    status_code_match = re.search(status_code_regex, log)

    # If the status code is not 200, return an empty dictionary
    if not status_code_match or status_code_match.group(1) != '200':
        return {}
    # Define regular expressions for extracting load balancer name, target group name, and requested URL
    lb_regex = r'app\/([^\/]+)'
    target_group_regex = r'targetgroup\/([^\/]+)'
    url_regex = r'\"GET (\S+)'

    # Find load balancer name, target group name, and requested URL using regular expressions
    lb_match = re.search(lb_regex, log)
    target_group_match = re.search(target_group_regex, log)
    url_match = re.search(url_regex, log)

    # Extract the load balancer name
    lb_name = lb_match.group(1) if lb_match else None

    # Extract the target group name
    target_group_name = target_group_match.group(1) if target_group_match else None

    # Extract the requested URL
    requested_url = url_match.group(1) if url_match else None

    # Check if the requested URL contains "/foo" or "/bar"
    requested_route = None
    if requested_url:
        if '/foo/' in requested_url:
            requested_route = 'foo'
        elif '/bar/' in requested_url:
            requested_route = 'bar'

    # Split the log into fields
    fields = log.split(' ')


    # Extract the client IP and port
    client_ip, client_port = fields[3].split(':')

    # Extract the backend IP
    backend_ip = fields[4].split(':')[0]

    # Return the information as a dictionary
    return {
        'load_balancer_name': lb_name,
        'client_ip': client_ip,
        'client_port': client_port,
        'backend_ip': backend_ip,
        'target_group_name': target_group_name,
        'requested_url': requested_url,
        'requested_route': requested_route
    }



if __name__=='__main__':
    # Test the function with an example log
    log = 'http 2024-04-27T18:31:21.969340Z app/foo-bar-alb/a565518c0b1b7e43 103.21.126.80:28429 10.1.2.126:80 0.001 0.011 0.000 200 200 581 351 "GET http://foo-bar-alb-1966958645.us-east-1.elb.amazonaws.com:80/bar/ HTTP/1.1" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" - - arn:aws:elasticloadbalancing:us-east-1:295848233874:targetgroup/bar-target-group/70b51bf3dcf1c9d7 "Root=1-662d4479-0ed7a4a316bbf6711de4aa5a" "-" "-" 2 2024-04-27T18:31:21.957000Z "forward" "-" "-" "10.1.2.126:80" "200" "-" "-"'

    log2= 'http 2024-04-27T18:31:19.444698Z app/foo-bar-alb/a565518c0b1b7e43 103.21.126.80:11567 10.1.1.148:80 0.000 0.004 0.000 200 200 633 351 "GET http://foo-bar-alb-1966958645.us-east-1.elb.amazonaws.com:80/foo/ HTTP/1.1" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" - - arn:aws:elasticloadbalancing:us-east-1:295848233874:targetgroup/foo-target-group/2f99bfbc5cdd6ebd "Root=1-662d4477-396dda025689439d27d02783" "-" "-" 1 2024-04-27T18:31:19.440000Z "forward" "-" "-" "10.1.1.148:80" "404" "-" "-"'


    print(parse_alb_log(log))
