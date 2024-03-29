import paramiko
import json

def check_vm_access():
    # Load data from file
    with open('data.txt', 'r') as f:
        data = json.load(f)

    # Initialize scores
    scores = {
        'connect_public_vm': 0,
        'private_ip_public_vm': 0,
        'ping_private_vm': 0,
        'ssh_private_vm': 0 
    }

    # Check VM access
    key = paramiko.RSAKey.from_private_key_file("instructor_public_vm.pem")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Transfer the private key for the private VM to the public VM
    try:
        private_key_private_vm = "instructor_private_vm.pem"
        ssh.connect(hostname=data['public_ip'], username="instructor", pkey=key)
        stdin, stdout, stderr = ssh.exec_command(f"if [ -f /home/instructor/{private_key_private_vm} ]; then rm -f /home/instructor/{private_key_private_vm}; fi")
        sftp = ssh.open_sftp()
        sftp.put(private_key_private_vm, "/home/instructor/instructor_private_vm.pem")
        sftp.close()
        # Change the permissions of the private key
        ssh.exec_command(f"chmod 400 /home/instructor/{private_key_private_vm}")
    except Exception as e:
        print(f"Failed to transfer the private key for the private VM to the public VM: {e}")
        return scores


    # Check if the SSH connection to the public VM is established and if the student actually SSHed into the public VM
    #result, messages = check_ssh_log(data['public_ip'],"instructor_public_vm.pem","instructor")
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


    # Check if we can ping the private VM
    stdin, stdout, stderr = ssh.exec_command(f"ping -c 1 {data['private_ip_private_vm']}")
    if "1 packets transmitted, 1 received" in stdout.read().decode():
        print("Check 3: Ping the private VM from the public VM")
        print("Success")
        scores['ping_private_vm'] = 1

    else:
        print("Check 3: Ping the private VM from the public VM")
        print("Failed")

    # Note: we have to transfer the ssh key for private vm which is "instructor_private_vm.pem" into public vm otherwise we can not log into private vm
    # Check if the SSH connection to the public VM is established and if the student actually SSHed into the public VM
    # SSH from the public VM to the private VM
    try:
        stdin, stdout, stderr = ssh.exec_command(f"ssh -i {private_key_private_vm} instructor@{data['private_ip_private_vm']} 'sudo cat /var/log/secure | grep sshd'")
        ssh_log = stdout.read().decode().strip()
        if 'Accepted publickey for ec2-user' in ssh_log:
            print("SSH log check passed.")
            print("Check 4: SSH :Connect to the private VM")
            print("Success")
            scores['ssh_private_vm'] = 1
        else:
            print("The student did not SSH into the VM.")
            print("Check 4: SSH :Connect to the private VM")
            print(f"Failed")
            return scores
    except Exception as e:
        print("SSH log check failed")
        print("Check 4: SSH :Connect to the private VM")
        print(f"Failed")

    try:
        stdin, stdout, stderr = ssh.exec_command(f"ssh -i {private_key_private_vm} instructor@{data['private_ip_private_vm']} 'timeout 5 curl ifconfig.me'")
        ip = stdout.read().decode().strip()
        if ip:
            print(f"The private VM is not private, it has a public IP: {ip}")
            scores['ssh_private_vm'] = 0
            scores['ping_private_vm'] = 0
        else:
            print("The private VM is indeed private.")
    except Exception as e:
        print(f"Error while checking private vm is private or not: {e}")

    ssh.close()

    return scores

if __name__ == "__main__":
    scores = check_vm_access()
    print("\nScores:")
    for check, score in scores.items():
        print(f"{check}: {score}")
    total_score = sum(scores.values())
    print(f"\nTotal Score: {total_score}")
