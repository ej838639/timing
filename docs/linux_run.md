# Summary
Here is how to run the project after the [Linux VM Setup](linux_setup.md).


Update version in pyproject.toml
```sh
[project]
name = "ptplab"
version = "0.1.2"
```

Reinstall the editable package.
```sh
uv pip install -e .
uv pip show ptplab # show new version is being used
```

# Build a new wheel for the package (if needed)
Build a new wheel
```sh
uv build

dist/
└── ptplab-0.1.3-py3-none-any.whl
```

# Copy build from local conputer to Linux VM 2
Move the following wheel: `ptplab-0.1.3-py3-none-any.whl`
From: `~/timing/build`
To: `~/linux_share2`

# Start VM2 and deploy ptplab
```sh
ls /mnt/linux_share2
```
If no files shown, then unmount and mount folder again.
```sh
sudo umount /mnt/linux_share2
sudo mount -t 9p -o trans=virtio,version=9p2000.L,rw,access=any share /mnt/linux_share2
```
Move the file and install it.
```sh
mv /mnt/linux_share2/ptplab-0.1.3-py3-none-any.whl ~/wheels

cd ~/timing
uv pip install ~/wheels/ptplab-0.1.3-py3-none-any.whl
uv pip show ptplab

# Output: verify it shows current version
Name: ptplab
Version: 0.1.2

uv run ptplab --help # verify it package is available to run
```

# Start ptp4l on VM1 as Grand Master (GM)
```sh
sudo ptp4l -i enp0s1 -m -S -f /etc/linuxptp/ptp4l.conf

# Expected output
ptp4l[2182.893]: port 1: INITIALIZING to LISTENING on INIT_COMPLETE
ptp4l[2182.893]: port 0: INITIALIZING to LISTENING on INIT_COMPLETE
ptp4l[2189.172]: port 1: LISTENING to MASTER on ANNOUNCE_RECEIPT_TIMEOUT_EXPIRES
ptp4l[2189.172]: selected local clock 12270c.fffe.c59c31 as best master
ptp4l[2189.172]: port 1: assuming the grand master role
```

# Start ptp4l on VM2
```sh
cd ~/timing
```
If the first time running, then run these commands.
```sh
# Confirm slave (i.e. " foreign master")
sudo ptp4l -i enp0s1 -m -S -f /etc/linuxptp/ptp4l.conf

# Expected output
ptp4l[64956.960]: port 1: INITIALIZING to LISTENING on INIT_COMPLETE
ptp4l[64956.960]: port 0: INITIALIZING to LISTENING on INIT_COMPLETE
ptp4l[64958.887]: port 1: new foreign master 12270c.fffe.c59c31-1
ptp4l[64962.892]: selected best master clock 12270c.fffe.c59c31
ptp4l[64962.892]: foreign master not using PTP timescale
ptp4l[64962.892]: port 1: LISTENING to UNCALIBRATED on RS_SLAVE
ptp4l[64965.022]: master offset -105589383 s0 freq +1500000 path delay    579968
ptp4l[64966.022]: master offset -105654118 s0 freq +1500000 path delay    677985
ptp4l[64967.025]: master offset -104997390 s0 freq +1500000 path delay    677985

# Ctrl-C to stop

# Analyze ouptput with ptplab. Start ptp4l in background.
mkdir -f logs
```

```sh
sudo -v
sudo ptp4l -i enp0s1 -m -S -f /etc/linuxptp/ptp4l.conf \
> ~/timing/logs/ptp4l_5.log 2>&1 &
```
`-m` prints to stdout; also tee to a file for parsing
`-S` forces software timestamping
`-f` config file to use
`> [filename]` send output to this file
`2>&1` redirect stderr into the same file
`&` run in the background

```sh
# Confirm the process is running
ps aux | grep ptp4l

# Confirm ptp4l is logging
tail -f ~/timing/logs/ptp4l_4.log
```
# Output the state, warnings, and alarms
```sh
# Process the logs with the python package we built: ptplab
uv run ptplab --log logs/ptp4l_short.log --from-start

uv run ptplab --log logs/ptp4l_5.log --event-log logs/ptp_events_3.jsonl

# Output
2025-12-29 11:23:27 [WARN] offset_warn: Offset 1.999 ms >= 1.0 ms
2025-12-29 11:23:27 [INFO] servo_state: Servo state s2
2025-12-29 11:23:28 [WARN] offset_warn: Offset 1.885 ms >= 1.0 ms
2025-12-29 11:23:28 [INFO] servo_state: Servo state s2
2025-12-29 11:23:29 [WARN] offset_warn: Offset 1.866 ms >= 1.0 ms
2025-12-29 11:23:29 [INFO] servo_state: Servo state s2
[...]
```
Collect about 20 min of logs (~1k lines). 
Transfer to local computer into the timing/logs folder. 
Then possible to run ptplab on local computer to analyze this file.

Stop ptplab with Ctrl-C

# If running for the local computer, process the log from the beginning
```sh
ptplab --log ~/timing/logs/ptp4l.log --from-start
ptplab --log logs/ptp4l_enp0s1.log --plot-every-s 1.0 --from-start
uv run ptplab --log logs/ptp4l_short.log --plot-every-s 1.0 --from-start
ptplab --log logs/ptp4l_short.log --plot-every-s 0.0 --from-start
python -m ptplab.app --log logs/ptp4l_enp0s1.log --plot-every-s 1.0 --from-start
```

# Stop ptp4l on VM2
Stop ptp4l that is running in the background
```sh
ps -o pid,ppid,stat,cmd -C ptp4l || echo "ptp4l stopped"
```
`-C ptp4l` Only show processes whose command name is ptp4l
`-o pid,ppid,stat,cmd` 
  pid: Process ID -> what to kill
  ppid: Parent process ID -> whether it’s wrapped by sudo or systemd
  stat: Process state -> healthy (S), stopped (T), zombie (Z)
  cmd: Full command line -> confirm interface, flags, config file
  
  Example:
  ```sh
  PID   PPID STAT CMD
  52946  52944 S    ptp4l -i enp0s1 -m -S -f /etc/linuxptp/ptp4l.conf
  ```

```sh
sudo kill [PID]

ps -o pid,ppid,stat,cmd -C ptp4l || echo "ptp4l stopped"
```
# Stop ptp4l on VM1
Ctrl-C to stop.

# Transfer file to local computer
Copy to shared folder.
```sh
cp logs/ptp_events_3.jsonl /mnt/linux_share2/
```

# Shut down Linux VMs
```sh
sudo poweroff
```

# Plot the offset vs time
Transfer the event log back to the local computer to plot and analyze.
```sh
uv run ptpanalyze --log logs/ptp_events_3.jsonl --title "PTP Offset Analysis" --block

```
