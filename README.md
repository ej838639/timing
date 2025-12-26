# Summary
Linux-based PTP timing lab for radar systems using ptp4l and phc2sys, with Python monitoring to measure offset stability, detect lost synchronization, and enforce timing budgets across single- and multi-site GNSS-disciplined deployments.

⸻

PTP Timing Lab for Radar Systems

This project is a hands-on learning lab for Precision Time Protocol (PTP) as used in radar and distributed sensor systems, with a focus on:
	•	Linux ptp4l and phc2sys
	•	measuring timing accuracy and stability
	•	detecting and alerting on synchronization loss
	•	scaling from a single radar site to multi-site GNSS-disciplined deployments

The lab mirrors a realistic radar architecture:
	•	Each site has a local PTP Grandmaster disciplined by GNSS
	•	A PTP-aware switch (Boundary Clock preferred)
	•	Radar compute nodes with PTP-capable NICs and OCXO
	•	ptp4l used to synchronize NIC PHC to the site GM
	•	phc2sys used to discipline the system clock from the NIC PHC
	•	Application-level monitoring to ensure offsets stay within cueing budgets

The project is designed to be useful even without PTP hardware timestamping, while clearly showing what additional insight you gain once hardware is available.

⸻

Goals
	•	Learn how linuxptp behaves in practice, not just on paper
	•	Understand offset, frequency correction, and path delay
	•	Build tooling to:
	•	parse real ptp4l logs
	•	plot offset vs time
	•	flag degraded or lost synchronization
	•	Practice engineering tradeoffs needed to stay below 10 ms timing error
	•	Create an interview-ready demonstration of timing system understanding for radar

⸻
# What This Project Is (and Is Not)

✅ This project is:
	•	A realistic PTP learning environment for radar systems
	•	Focused on operational behavior, not just theory
	•	Portable: Linux does timing, macOS can do analysis
	•	Honest about hardware constraints

❌ This project is not:
	•	A replacement for a real GNSS-disciplined PTP lab
	•	A claim of sub-microsecond accuracy without hardware timestamping
	•	A WAN-scale PTP solution (sites are independent timing islands)

⸻
# Documentation
- [System Architecture](docs/system_architecture.md)
- [Interfaces](docs/interfaces.md)
- [Requirements](docs/requirements.md)

⸻
# Project Layout

timing/
  README.md
  pyproject.toml
  configs/
    site_single.yaml
    site_multisite.yaml
  docs/
    interfaces.md
    requirements.md
    system_architecture.md
  examples/
    example_ptp41.log
  scripts/
    ptp4l_slave.sh           # Run ptp4l as a slave
    phc2sys.sh               # Discipline system clock from NIC PHC
    check_ts_capabilities.sh # Check NIC timestamping support
    simulate_ptp_log.sh      # Generate fake ptp4l logs for development
  src/ptplab/
    common/
      models.py              # Data models
    ptplab/
      config.py                # Thresholds and configuration
      log_tail.py              # Tail-like log follower
      parse_ptp.py             # ptp4l log parsing
      events.py                # Warn / alarm / lost-sync detection
      plot.py                  # Offset vs time plotting
      monitor.py               # Main monitoring application
    app.py

⸻
# Supported Platforms

Linux (Timing Nodes)
	•	Recommended OS: Ubuntu Server 22.04 LTS
	•	Kernel: ≥ 5.15 (6.x supported)
	•	Why: full support for PHC, hardware timestamping, and linuxptp

macOS (Development / Analysis)
	•	Used for:
	•	Python development
	•	log parsing and plotting
	•	macOS does not support Linux PHC or ptp4l equivalently
	•	Real timing work must run on Linux

⸻
# Running Without PTP Hardware (Software Timestamping)

Even without a PTP-capable NIC, you can learn:
	•	ptp4l state transitions (LISTENING → UNCALIBRATED → SLAVE)
	•	offset and frequency correction behavior
	•	how network load affects timing
	•	how to detect degraded sync or failures

Run ptp4l using software timestamping:

./scripts/ptp4l_slave.sh eth0 0

Simulate logs for development:

./scripts/simulate_ptp_log.sh ./logs/ptp4l_sim.log
python -m ptplab.monitor --log ./logs/ptp4l_sim.log

⸻
# Running With PTP Hardware (Future / Optional)

With a NIC that supports hardware timestamping:
	•	/dev/ptp0 will appear
	•	ptp4l can use hardware timestamps
	•	phc2sys can discipline system time from the NIC PHC
	•	Offset jitter drops significantly
	•	Holdover and GNSS loss behavior can be evaluated

Example:

./scripts/ptp4l_slave.sh eth0 0
./scripts/phc2sys.sh /dev/ptp0


⸻
# Monitoring & Alerting

The Python monitor provides:
	•	Offset vs time plotting
	•	Threshold-based alerts
	•	Warn: ≥ 1 ms
	•	Alarm: ≥ 5 ms
	•	Lost-sync detection
	•	No valid servo updates for N seconds

Run:

python -m ptplab.monitor \
  --log ./logs/ptp4l_eth0_d0.log \
  --warn-ms 1 \
  --alarm-ms 5 \
  --lost-sync-s 3

These thresholds can be tuned to match radar cueing budgets.

⸻
# Engineering Challenges Explored

This lab is intentionally designed to surface real-world issues:
	•	CPU contention and scheduling jitter
	•	Network congestion and packet delay variation
	•	PTP state churn and BMCA changes
	•	Log gaps and process failures
	•	Differences between software and hardware timestamping

The goal is not “perfect sync”, but knowing when sync is no longer trustworthy.

⸻
# Why This Matters for Radar Systems

Radar systems depend on time alignment for:
	•	coherent processing
	•	multi-sensor fusion
	•	track correlation
	•	cueing and handoff logic

In practice, detecting degraded timing is often more important than achieving absolute best-case accuracy.

This project demonstrates how to:
	•	build timing confidence,
	•	enforce timing budgets,
	•	and surface timing health to higher-level systems.

⸻
# Future Extensions
	•	systemd units for ptp4l / phc2sys
	•	SLO reports (% time < 1 ms / 5 ms / 10 ms)
	•	Multi-site dashboard
	•	GNSS loss / holdover experiments
	•	NIC and switch comparisons (BC vs non-BC)
