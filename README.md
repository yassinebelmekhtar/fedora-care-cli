# Fedora Care CLI

A terminal-based maintenance and system monitoring tool for Fedora Linux.

## Installation

```bash
pip install -e .
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
