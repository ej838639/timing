# Summary
Here is how to setup a virtual machine with a Linux OS and Python 3.12.12 to use for this project.

# Linux Virtual Machine
Setup a VM with Linux OS. For a Mac it is recommended to use [UTM](https://mac.getutm.app/).
Remove USB drive since it it not needed for this project. (And it will cause a conflict if you add a second VM server attached to it.)

It is recommended to use [Ubuntu Server 22.04 LTS (Jammy)](https://cdimage.ubuntu.com/releases/jammy/release/) since it is a stable release.

No need for LVM. It adds complexity without benefit.

# Install Packages
```sh
sudo apt update
sudo apt install -y \
ethtool \
linuxptp \
iproute2
```
Set prompt to local time
```sh
timedatectl

# Output
Local time: Tue 2025-01-07 19:22:10 UTC
Universal time: Tue 2025-01-07 19:22:10 UTC
RTC time: Tue 2025-01-07 19:22:09
RTC in local TZ: no
Time zone: UTC (UTC, +0000)

timedatectl list-timezones

# Set to local time
sudo timedatectl set-timezone America/Los_Angeles

```

# Setup second VM
Setup a second VM the same way. 

# Setup Master and Slave
Find the IP address of both VMs.
```sh
ip link show enp0s1
ip addr show enp0s1
```

Ensure both VMs are on the same subnet. For example:
VM1: 192.168.64.3/24
VM2: 192.168.64.4/24

Ensure they can reach each other. 
From VM1:
```sh
ping 192.168.64.4
```

From VM2:
```sh
ping 192.168.64.3
```

Setup VM1 as the Grand Master (GM).
```sh
sudo nano /etc/linuxptp/ptp4l.conf
```
Confirm the following default settings:
priority1: 128
priority2: 128
domainNumber: 0

Setup VM2 as the Slave. 
```sh
sudo nano /etc/linuxptp/ptp4l.conf
```
Change to the following so the Best Master Clock Algorithm (BMCA) chooses VM1 (the lower priority):
priority1: 248
priority2: 248
domainNumber: 0

# Install Python 3.12.12
Install build depedencies
```sh
sudo apt update
sudo apt install -y build-essential curl git ca-certificates \
libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev uuid-dev
```
Install Python 3.12 (since this Linux OS has Python 3.10.12)
```sh
python3 --version

sudo apt install -y python3.12 python3.12-venv python3-pip
```
Run the venv with uv
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
sudo snap install astral-uv --classic

cd timing
uv venv
source .venv/bin/activate
uv pip install ptplab-0.1.0-py3-none-any.whl

ptplab --help
ptplab --log /var/log/ptp4l.log
```
