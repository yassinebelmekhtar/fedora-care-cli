import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import click
import psutil
from rich import print
from rich.table import Table


def gb(n: int) -> float:
    return round(n / (1024**3), 2)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return (r.stdout or r.stderr or "").strip()


def run_root(cmd):
    r = subprocess.run(["sudo"] + cmd, capture_output=True, text=True, check=False)
    return (r.stdout or r.stderr or "").strip()


@click.group(help="Fedora bakım & hız kontrol aracı")
def cli():
    pass


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Çıktıyı JSON formatında ver.")
def health(as_json):
    """Sistem sağlığı özetini gösterir."""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    load1, load5, load15 = psutil.getloadavg()

    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    du = shutil.disk_usage("/")

    boot = datetime.fromtimestamp(psutil.boot_time())
    uptime_sec = int((datetime.now() - boot).total_seconds())
    uptime_h = uptime_sec // 3600
    uptime_m = (uptime_sec % 3600) // 60

    systemd_analyze = run(["systemd-analyze"]) or "systemd-analyze okunamadı"

    data = {
        "cpu_percent": cpu_percent,
        "load_avg": {"1m": round(load1, 2), "5m": round(load5, 2), "15m": round(load15, 2)},
        "ram": {"percent": vm.percent, "used_gb": gb(vm.used), "total_gb": gb(vm.total)},
        "swap": {"percent": swap.percent, "used_gb": gb(swap.used), "total_gb": gb(swap.total)},
        "disk_root": {"used_gb": gb(du.used), "total_gb": gb(du.total), "free_gb": gb(du.free)},
        "uptime": {"hours": uptime_h, "minutes": uptime_m},
        "boot_summary": systemd_analyze,
    }

    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    t = Table(title="Fedora Care • Health", show_lines=True)
    t.add_column("Alan", style="bold")
    t.add_column("Değer")

    t.add_row("CPU Kullanımı", f"%{cpu_percent}")
    t.add_row("Load Avg", f"{load1:.2f} / {load5:.2f} / {load15:.2f}")
    t.add_row("RAM", f"%{vm.percent}  ({gb(vm.used)} / {gb(vm.total)} GB)")
    t.add_row("SWAP", f"%{swap.percent} ({gb(swap.used)} / {gb(swap.total)} GB)")
    t.add_row("Disk /", f"{gb(du.used)} / {gb(du.total)} GB  (Boş: {gb(du.free)} GB)")
    t.add_row("Uptime", f"{uptime_h} saat {uptime_m} dk")
    t.add_row("Boot Süresi", systemd_analyze)

    print(t)


@cli.command()
@click.option("--since", default="10m", show_default=True, help="Zaman aralığı (örn: 10m, 1h, 1d)")
@click.option("--json", "as_json", is_flag=True, help="Çıktıyı JSON formatında ver.")
def logs(since, as_json):
    """Son hata/uyarı sayısını gösterir."""
    err = run(["journalctl", "--since", since, "-p", "err", "--no-pager"])
    warn = run(["journalctl", "--since", since, "-p", "warning", "--no-pager"])

    err_count = len([l for l in (err.splitlines() if err else []) if l.strip()])
    warn_count = len([l for l in (warn.splitlines() if warn else []) if l.strip()])

    data = {"since": since, "errors": err_count, "warnings": warn_count}

    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    t = Table(title=f"Logs • Son {since}", show_lines=True)
    t.add_column("Seviye", style="bold")
    t.add_column("Adet")
    t.add_row("ERROR", str(err_count))
    t.add_row("WARNING", str(warn_count))
    print(t)

    if err_count == 0 and warn_count == 0:
        print("[bold green]Temiz görünüyor ✅[/bold green]")
    else:
        print("[bold yellow]Detay görmek için:[/bold yellow]")
        print(f"  journalctl --since {since} -p err")
        print(f"  journalctl --since {since} -p warning")


@cli.command()
@click.option("--apply", is_flag=True, help="Gerçekten uygula (sudo ister).")
@click.option("--json", "as_json", is_flag=True, help="Çıktıyı JSON formatında ver.")
def clean(apply, as_json):
    """Cache/log temizliği (varsayılan: dry-run)."""
    actions = [
        {"name": "DNF cache temizliği", "command": ["dnf", "clean", "all"]},
        {"name": "Eski journal loglarını küçült (1 hafta)", "command": ["journalctl", "--vacuum-time=7d"]},
    ]

    if as_json:
        payload = {
            "mode": "apply" if apply else "dry-run",
            "actions": [{"name": a["name"], "command": " ".join(a["command"])} for a in actions],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if apply:
            # JSON modunda da uygulasın istiyorsan uygular; istemiyorsan apply kullanmazsın zaten.
            for a in actions:
                run_root(a["command"])
        return

    t = Table(title="Clean • Plan", show_lines=True)
    t.add_column("İşlem", style="bold")
    t.add_column("Komut")
    t.add_column("Mod")

    for a in actions:
        t.add_row(a["name"], " ".join(a["command"]), "APPLY" if apply else "DRY-RUN")

    print(t)

    if not apply:
        print("\n[bold yellow]Dry-run:[/bold yellow] Hiçbir şey silinmedi.")
        print("Uygulamak istersen: [bold]fedcare clean --apply[/bold]")
        return

    print("\n[bold]Uygulanıyor (sudo isteyebilir)...[/bold]")
    for a in actions:
        print(f"\n[bold]{a['name']}[/bold]")
        out = run_root(a["command"])
        print(out if out else "OK")

    print("\n[bold green]Temizlik tamam ✅[/bold green]")


@cli.command()
@click.option("--since", default="10m", show_default=True, help="Log zaman aralığı")
@click.option("--json", "as_json", is_flag=True, help="Çıktıyı JSON formatında ver.")
def report(since, as_json):
    """Health + Logs + Clean planını tek seferde gösterir."""
    # --- health ---
    cpu_percent = psutil.cpu_percent(interval=0.5)
    load1, load5, load15 = psutil.getloadavg()
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    du = shutil.disk_usage("/")
    boot = datetime.fromtimestamp(psutil.boot_time())
    uptime_sec = int((datetime.now() - boot).total_seconds())
    uptime_h = uptime_sec // 3600
    uptime_m = (uptime_sec % 3600) // 60
    systemd_analyze = run(["systemd-analyze"]) or "?"

    # --- logs ---
    err = run(["journalctl", "--since", since, "-p", "err", "--no-pager"])
    warn = run(["journalctl", "--since", since, "-p", "warning", "--no-pager"])
    err_count = len([l for l in (err.splitlines() if err else []) if l.strip()])
    warn_count = len([l for l in (warn.splitlines() if warn else []) if l.strip()])

    # --- clean plan ---
    clean_actions = [
        {"name": "DNF cache temizliği", "command": "dnf clean all"},
        {"name": "Eski journal loglarını küçült (1 hafta)", "command": "journalctl --vacuum-time=7d"},
    ]

    if as_json:
        data = {
            "health": {
                "cpu_percent": cpu_percent,
                "load_avg": {"1m": round(load1, 2), "5m": round(load5, 2), "15m": round(load15, 2)},
                "ram": {"percent": vm.percent, "used_gb": gb(vm.used), "total_gb": gb(vm.total)},
                "swap": {"percent": swap.percent, "used_gb": gb(swap.used), "total_gb": gb(swap.total)},
                "disk_root": {"used_gb": gb(du.used), "total_gb": gb(du.total), "free_gb": gb(du.free)},
                "uptime": {"hours": uptime_h, "minutes": uptime_m},
                "boot_summary": systemd_analyze,
            },
            "logs": {"since": since, "errors": err_count, "warnings": warn_count},
            "clean": {"mode": "dry-run", "actions": clean_actions},
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    t = Table(title="Fedora Care • Full Report", show_lines=True)
    t.add_column("Kategori", style="bold")
    t.add_column("Alan", style="bold")
    t.add_column("Değer")

    t.add_row("Health", "CPU", f"%{cpu_percent}")
    t.add_row("Health", "Load Avg", f"{load1:.2f} / {load5:.2f} / {load15:.2f}")
    t.add_row("Health", "RAM", f"%{vm.percent}  ({gb(vm.used)} / {gb(vm.total)} GB)")
    t.add_row("Health", "SWAP", f"%{swap.percent} ({gb(swap.used)} / {gb(swap.total)} GB)")
    t.add_row("Health", "Disk /", f"{gb(du.used)} / {gb(du.total)} GB  (Boş: {gb(du.free)} GB)")
    t.add_row("Health", "Uptime", f"{uptime_h} saat {uptime_m} dk")
    t.add_row("Health", "Boot", systemd_analyze)
    t.add_row("Logs", f"Errors (son {since})", str(err_count))
    t.add_row("Logs", f"Warnings (son {since})", str(warn_count))
    for a in clean_actions:
        t.add_row("Clean", a["name"], f"[dim]{a['command']}[/dim]  (dry-run)")

    print(t)


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Çıktıyı JSON formatında ver.")
def services(as_json):
    """Kritik systemd servislerinin durumunu gösterir."""
    svc_list = ["NetworkManager", "firewalld", "sshd", "crond", "bluetooth", "docker"]
    results = []
    for svc in svc_list:
        status = run(["systemctl", "is-active", svc])
        if status not in ("active", "inactive"):
            status = "not-found"
        results.append({"name": svc, "status": status})

    if as_json:
        print(json.dumps({"services": results}, ensure_ascii=False, indent=2))
        return

    t = Table(title="Fedora Care • Services", show_lines=True)
    t.add_column("Servis", style="bold")
    t.add_column("Durum")
    for s in results:
        color = "green" if s["status"] == "active" else "red" if s["status"] == "inactive" else "dim"
        t.add_row(s["name"], f"[{color}]{s['status']}[/{color}]")
    print(t)


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Çıktıyı JSON formatında ver.")
def network(as_json):
    """Ağ bilgisi ve bağlantı testi."""
    # Interfaces
    ifaces = {}
    for iface, addrs in psutil.net_if_addrs().items():
        ips = [a.address for a in addrs if a.family.name == "AF_INET"]
        if ips:
            ifaces[iface] = ips

    # DNS
    dns_servers = []
    try:
        with open("/etc/resolv.conf") as f:
            for line in f:
                line = line.strip()
                if line.startswith("nameserver"):
                    dns_servers.append(line.split()[1])
    except FileNotFoundError:
        pass

    # Ping tests
    ping_ip = run(["ping", "-c1", "-W2", "8.8.8.8"])
    ping_dns = run(["ping", "-c1", "-W2", "google.com"])
    ping_ip_ok = "1 received" in ping_ip or "1 packets received" in ping_ip or ", 0% packet loss" in ping_ip
    ping_dns_ok = "1 received" in ping_dns or "1 packets received" in ping_dns or ", 0% packet loss" in ping_dns

    data = {
        "interfaces": ifaces,
        "dns": dns_servers,
        "ping_ip": "OK" if ping_ip_ok else "FAIL",
        "ping_dns": "OK" if ping_dns_ok else "FAIL",
    }

    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    t = Table(title="Fedora Care • Network", show_lines=True)
    t.add_column("Alan", style="bold")
    t.add_column("Değer")
    for iface, ips in ifaces.items():
        t.add_row(f"Arayüz: {iface}", ", ".join(ips))
    t.add_row("DNS", ", ".join(dns_servers) if dns_servers else "Bulunamadı")
    t.add_row("Ping 8.8.8.8", "[green]OK[/green]" if ping_ip_ok else "[red]FAIL[/red]")
    t.add_row("Ping google.com", "[green]OK[/green]" if ping_dns_ok else "[red]FAIL[/red]")
    print(t)


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Çıktıyı JSON formatında ver.")
def updates(as_json):
    """Bekleyen DNF güncellemelerini listeler."""
    r = subprocess.run(
        ["dnf", "check-update", "--quiet"],
        capture_output=True, text=True, check=False,
    )
    output = (r.stdout or "").strip()
    packages = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 3 and "." in parts[0]:
            pkg_name = parts[0].rsplit(".", 1)[0]
            new_ver = parts[1]
            # Try to get current version
            cur = run(["rpm", "-q", "--qf", "%{VERSION}-%{RELEASE}", pkg_name])
            if "not installed" in cur:
                cur = "-"
            packages.append({"name": parts[0], "current": cur, "new": new_ver})

    if as_json:
        print(json.dumps({"count": len(packages), "packages": packages}, ensure_ascii=False, indent=2))
        return

    t = Table(title="Fedora Care • Updates", show_lines=True)
    t.add_column("Paket", style="bold")
    t.add_column("Mevcut Sürüm")
    t.add_column("Yeni Sürüm")
    for p in packages:
        t.add_row(p["name"], p["current"], p["new"])
    print(t)
    print(f"\nToplam [bold]{len(packages)}[/bold] güncelleme bekliyor.")


@cli.command()
@click.option("--dest", default=None, help="Yedek hedef dizini.")
@click.option("--json", "as_json", is_flag=True, help="Çıktıyı JSON formatında ver.")
def backup(dest, as_json):
    """Önemli config dosyalarını yedekler."""
    if dest is None:
        dest = os.path.join(
            Path.home(), "fedcare-backup", datetime.now().strftime("%Y%m%d-%H%M%S")
        )

    targets = [
        "/etc/fstab",
        "/etc/hosts",
        "/etc/dnf/dnf.conf",
        "/etc/ssh/sshd_config",
        "/etc/default/grub",
        "/etc/NetworkManager/",
    ]

    os.makedirs(dest, exist_ok=True)
    results = []
    for src in targets:
        try:
            if os.path.isdir(src):
                dst = os.path.join(dest, src.lstrip("/"))
                shutil.copytree(src, dst, dirs_exist_ok=True)
                results.append({"path": src, "status": "OK"})
            elif os.path.isfile(src):
                dst = os.path.join(dest, src.lstrip("/"))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                results.append({"path": src, "status": "OK"})
            else:
                results.append({"path": src, "status": "Bulunamadı"})
        except PermissionError:
            results.append({"path": src, "status": "İzin hatası"})
        except Exception as e:
            results.append({"path": src, "status": str(e)})

    if as_json:
        print(json.dumps({"dest": dest, "files": results}, ensure_ascii=False, indent=2))
        return

    t = Table(title=f"Fedora Care • Backup → {dest}", show_lines=True)
    t.add_column("Dosya", style="bold")
    t.add_column("Durum")
    for r in results:
        color = "green" if r["status"] == "OK" else "red"
        t.add_row(r["path"], f"[{color}]{r['status']}[/{color}]")
    print(t)


@cli.command()
@click.option("--top", "top_n", default=10, show_default=True, help="Gösterilecek servis sayısı.")
@click.option("--json", "as_json", is_flag=True, help="Çıktıyı JSON formatında ver.")
def startup(top_n, as_json):
    """Açılışta en yavaş servisleri gösterir."""
    output = run(["systemd-analyze", "blame", "--no-pager"])
    items = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            items.append({"time": parts[0], "service": parts[1]})
        if len(items) >= top_n:
            break

    if as_json:
        print(json.dumps({"items": items}, ensure_ascii=False, indent=2))
        return

    t = Table(title=f"Fedora Care • Startup (Top {top_n})", show_lines=True)
    t.add_column("Sıra", style="bold", justify="right")
    t.add_column("Servis")
    t.add_column("Süre")
    for i, item in enumerate(items, 1):
        t.add_row(str(i), item["service"], item["time"])
    print(t)


if __name__ == "__main__":
    cli()
