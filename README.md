# Fedora Care CLI

A terminal-based maintenance and system monitoring tool for Fedora Linux. Check system health, monitor systemd services, test network connectivity, list pending DNF updates, backup config files, and analyze boot performance — all with `fedcare`.

**Features:** CPU/RAM/disk monitoring, systemd service status, network diagnostics, journalctl log analysis, DNF update checker, config file backup, boot time analysis, full system report. All commands support `--json` output for scripting and automation.

## Installation

### Via DNF (Recommended)

```bash
sudo dnf copr enable selinbtw/fedcare
sudo dnf install fedora-care-cli
```

### Via pip

```bash
pip install .
```

## Quick Start

After installing, run `fedcare` to see all available commands:

```bash
fedcare              # Show all commands
fedcare health       # System health summary
fedcare services     # Systemd service status
fedcare network      # Network diagnostics
fedcare logs         # Recent errors/warnings
fedcare updates      # Pending DNF updates
fedcare clean        # Cleanup plan (dry-run)
fedcare clean --apply  # Execute cleanup
fedcare backup       # Backup config files
fedcare startup      # Slowest boot services
fedcare report       # Full system report
```

Add `--json` to any command for JSON output:

```bash
fedcare health --json
```

## Commands

| Command | Description |
|---------|-------------|
| `fedcare health` | System health summary (CPU, RAM, SWAP, disk, uptime, boot time) |
| `fedcare services` | Status of critical systemd services |
| `fedcare network` | Network interfaces, DNS, and connectivity test |
| `fedcare logs` | Recent error/warning counts from journalctl |
| `fedcare updates` | List pending DNF updates |
| `fedcare clean` | Cache/log cleanup (default: dry-run) |
| `fedcare backup` | Backup important config files |
| `fedcare startup` | Slowest services at boot |
| `fedcare report` | Combined Health + Logs + Clean report |

Every command supports the `--json` flag for JSON output.

## Screenshots

### `fedcare health`
![health](screenshots/health.png)

### `fedcare services` & `fedcare startup`
![services-startup](screenshots/services-startup.png)

### `fedcare network` & `fedcare logs`
![network-logs](screenshots/network-logs.png)

### `fedcare updates`
![updates](screenshots/updates.png)

### `fedcare clean` & `fedcare clean --apply`
![clean](screenshots/clean.png)

### `fedcare report`
![report](screenshots/report.png)

## Usage

```bash
fedcare health
fedcare services --json
fedcare backup --dest ~/my-backup
fedcare startup --top 15
fedcare clean --apply
```

## Requirements

- Fedora Linux
- Python 3.10+
