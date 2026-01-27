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

## Example Output

### `fedcare health`
```
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field     ┃ Value                                             ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ CPU Usage │ 4.9%                                              │
│ Load Avg  │ 0.42 / 0.77 / 0.96                                │
│ RAM       │ 52.6%  (7.31 / 14.95 GB)                          │
│ SWAP      │ 0.0% (0.0 / 8.0 GB)                               │
│ Disk /    │ 15.86 / 474.35 GB  (Free: 457.47 GB)              │
│ Uptime    │ 11h 17m                                           │
│ Boot Time │ Startup finished in 19.446s                       │
└───────────┴───────────────────────────────────────────────────┘
```

### `fedcare services`
```
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Service        ┃ Status   ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ NetworkManager │ active   │
│ firewalld      │ active   │
│ sshd           │ inactive │
│ crond          │ active   │
│ bluetooth      │ active   │
│ docker         │ inactive │
└────────────────┴──────────┘
```

### `fedcare network`
```
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Field           ┃ Value        ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Interface: lo   │ 127.0.0.1    │
│ Interface: wlo1 │ 192.168.1.21 │
│ DNS             │ 127.0.0.53   │
│ Ping 8.8.8.8    │ OK           │
│ Ping google.com │ OK           │
└─────────────────┴──────────────┘
```

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
