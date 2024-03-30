import paramiko
import json

def check_vm_access():
    # Load data from file
    with open('data.txt', 'r') as f:
        data = json.load(f)

    # Initialize scores
    scores = {
        'connect_public_vm': 0,
        'private_ip_public_vm': 0
    }

    # Check VM access
    key = paramiko.RSAKey.from_private_key_file("instructor_public_vm.pem")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())



    # Check if the SSH connection to the public VM is established and if the student actually SSHed into the public VM
    try:
        ssh.connect(hostname=data['public_ip'], username="instructor", pkey=key)
        stdin,stdout,stderr = ssh.exec_command("sudo cat /var/log/secure | grep sshd")
        ssh_log = stdout.read().decode().strip()
        if 'Accepted publickey for ec2-user' in ssh_log:
            print("SSH log check passed.")
            print("Check 1: SSH :Connect to the public VM")
            print("Success")
            scores['connect_public_vm'] = 1
        else:
            print("Check 1: SSH :Connect to the public VM")
            print(f"Failed")
            print("The student did not SSH into the public VM.")
            return scores
    except Exception as e:
        print("SSH log check failed")
        print("Check 1: SSH :Connect to the public VM")
        print(f"Failed: {e}")
        return scores

    # Check private IP of the public VM
    stdin, stdout, stderr = ssh.exec_command("curl http://169.254.169.254/latest/meta-data/local-ipv4")
    if data['private_ip_public_vm'] in stdout.read().decode():
        print("Check 2: Private IP of the public VM is correct")
        print("Success")
        scores['private_ip_public_vm'] = 1
    else:
        print("Check 2: Private IP of the public VM is correct")
        print("Failed")


    ssh.close()

    return scores

if __name__ == "__main__":
    scores = check_vm_access()
    print("\nScores:")
    for check, score in scores.items():
        print(f"{check}: {score}")
    total_score = sum(scores.values())
    print(f"\nTotal Score: {total_score}")
