#!/bin/bash -ex 

# Check if "instructor_public_vm.pem" exists and delete it if it does
if [ -f /home/ec2-user/instructor_public_vm.pem ]; then
    sudo rm /home/ec2-user/instructor_public_vm.pem
fi
# Create a new user account for the instructor
sudo adduser instructor

# Assign sudo privileges to the instructor account
echo 'instructor ALL=(ALL) NOPASSWD:ALL' | sudo tee -a /etc/sudoers

# Create a .ssh directory for the instructor account
sudo mkdir /home/instructor/.ssh
sudo chmod 700 /home/instructor/.ssh

# Generate a temporary SSH key pair for the instructor account
sudo ssh-keygen -t rsa -b 2048 -f /home/instructor/.ssh/id_rsa -N "" -q
sudo mv /home/instructor/.ssh/id_rsa.pub /home/instructor/.ssh/authorized_keys
sudo chmod 600 /home/instructor/.ssh/authorized_keys
sudo chown -R instructor:instructor /home/instructor/.ssh

# Copy the private key to the ec2-user account
sudo cp /home/instructor/.ssh/id_rsa /home/ec2-user/instructor_public_vm.pem
sudo chown ec2-user:ec2-user /home/ec2-user/instructor_public_vm.pem
sudo chmod 400 /home/ec2-user/instructor_public_vm.pem

# Set a cron job to delete the instructor account and its home directory after 2 hours
echo "sudo userdel -rf instructor" | script -c "/usr/bin/at now + 80 minutes"
