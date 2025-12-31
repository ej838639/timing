# Summary
Linux-based PTP timing lab for radar systems using ptp4l, with Python monitoring to measure offset stability and detect lost synchronization.

⸻
# PTP Timing Lab for Radar Systems
This project is a hands-on learning lab for Precision Time Protocol (PTP) as used in radar and distributed sensor systems, with a focus on:
- Linux ptp4l
- Measuring timing accuracy and stability
- Detecting and alerting on synchronization loss
- Scaling from a single radar site to multi-site GNSS-disciplined deployments

The lab mirrors a realistic radar architecture:
- Each site has a local PTP Grandmaster disciplined by GNSS
- A PTP-aware switch (Boundary Clock preferred)
-	Radar compute nodes with PTP-capable NICs and OCXO
-	ptp4l used to synchronize NIC PHC to the site GM
-	phc2sys used to discipline the system clock from the NIC PHC
-	Application-level monitoring to ensure offsets stay within cueing budgets

The project is designed to be useful even without PTP hardware timestamping, while clearly showing what additional insight you gain once hardware is available.

⸻
# Goals
-	Learn how linuxptp behaves in practice, not just on paper
-	Understand offset, frequency correction, and path delay
-	Build tooling to:
-	parse real ptp4l logs
-	plot offset vs time
-	flag degraded or lost synchronization
-	Practice engineering tradeoffs needed to stay below 10 ms timing error
-	Create an interview-ready demonstration of timing system understanding for radar

⸻
# What This Project Is (and Is Not)

✅ This project is:
-	A realistic PTP learning environment for radar systems
-	Focused on operational behavior, not just theory
-	Portable: Linux does timing, macOS can do analysis
-	Honest about hardware constraints

❌ This project is not:
-	A replacement for a real GNSS-disciplined PTP lab
-	A claim of sub-microsecond accuracy without hardware timestamping
-	A WAN-scale PTP solution (sites are independent timing islands)

⸻
# Documentation
- [System Architecture](docs/system_architecture.md)
- [Interfaces](docs/interfaces.md)
- [Requirements](docs/requirements.md)

⸻
# Run Code
Here is how to run the code for the project

Setup two Linux VMs, capture logs for ptp4l from the slave VM, transfer the logs to the local computer in the timing/logs folder, and analyze the events log.
- [Linux Setup](docs/linux_setup.md)
- [Linux Run](docs/linux_run.md)
- [Local Analyze](docs/local_analyze.md)

⸻
# Project Layout
```txt
timing/
├── README.md
├── main.py
├── pyproject.toml
│
├── build/                         # Build artifacts
│
├── configs/
│   ├── site_single.yaml
│   └── site_multisite.yaml
│
├── docs/
│   ├── interfaces.md
│   ├── linux_run.md
│   ├── linux_setup.md
│   ├── local_analyze.md
│   ├── requirements.md
│   └── system_architecture.md
│
├── logs/                          # PTP logs from Linux VMs
│
├── scripts/
│   ├── check_ts_capabilities.sh  # Check NIC timestamping support
│   └── phc2sys.sh                # Discipline system clock from NIC PHC
│
└── src/
    ├── ptpanalyze/               # Analysis tools
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── analyzer.py
    │   ├── app.py
    │   └── plot.py
    │
    └── ptplab/                   # Main monitoring application
        ├── __init__.py
        ├── __main__.py
        ├── app.py
        ├── config.py             # Thresholds and configuration
        ├── event_logger.py
        ├── events.py             # Warn / alarm / lost-sync detection
        ├── log_tail.py           # Tail-like log follower
        ├── models.py             # Data models
        ├── monitor.py            # Main monitoring loop
        └── parse_ptp.py          # ptp4l log parsing
```
⸻
# Supported Platforms
Linux (Log Collection / Parsing)
- Generate ptp4l messages
- Parse ptp4l messages into events

macOS (Development / Analysis)
-	Python development
-	Event plotting

⸻
# Running Without PTP Hardware (Software Timestamping)
Even without a PTP-capable NIC:
-	ptp4l state transitions (LISTENING → UNCALIBRATED → SLAVE)
-	offset and frequency correction behavior
-	how network load affects timing
-	how to detect degraded sync or failures

⸻
# Running With PTP Hardware (Future)
With a NIC that supports hardware timestamping:
-	/dev/ptp0 will appear
-	ptp4l can use hardware timestamps
-	phc2sys can discipline system time from the NIC PHC
-	Offset jitter drops significantly
-	Holdover and GNSS loss behavior can be evaluated

⸻
# Monitoring & Alerting
The Python monitor provides:
-	Offset vs time plotting
-	Threshold-based alerts
-	Warn: ≥ 1 ms
-	Alarm: ≥ 5 ms
-	Lost-sync detection
-	No valid servo updates for N seconds

⸻
# Engineering Challenges Explored
This lab is intentionally designed to surface real-world issues:
-	CPU contention and scheduling jitter
-	Network congestion and packet delay variation
-	PTP state churn and BMCA changes
-	Log gaps and process failures

The goal is not “perfect sync”, but knowing when sync is no longer trustworthy.

⸻
# Why This Matters for Radar Systems
Radar systems depend on time alignment for:
-	coherent processing
-	multi-sensor fusion
-	track correlation
-	cueing and handoff logic

In practice, detecting degraded timing is often more important than achieving absolute best-case accuracy.

This project demonstrates how to:
-	build timing confidence,
-	enforce timing budgets,
-	and surface timing health to higher-level systems.

⸻
# Future Extensions
-	systemd units for ptp4l / phc2sys
-	SLO reports (% time < 1 ms / 5 ms / 10 ms)
-	Multi-site dashboard
-	GNSS loss / holdover experiments
-	NIC and switch comparisons (BC vs non-BC)
