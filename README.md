# Fedora Care CLI

Fedora Linux için terminal tabanlı bakım ve sistem izleme aracı.

## Kurulum

```bash
pip install -e .
```

## Komutlar

| Komut | Açıklama |
|-------|----------|
| `fedcare health` | CPU, RAM, SWAP, disk, uptime ve boot süresi özeti |
| `fedcare services` | Kritik systemd servislerinin durumu |
| `fedcare network` | Ağ arayüzleri, DNS ve ping testi |
| `fedcare logs` | Son hata/uyarı sayısı (journalctl) |
| `fedcare updates` | Bekleyen DNF güncellemeleri |
| `fedcare clean` | Cache/log temizliği (varsayılan dry-run) |
| `fedcare backup` | Önemli config dosyalarını yedekler |
| `fedcare startup` | Açılışta en yavaş servisler |
| `fedcare report` | Health + Logs + Clean özet raporu |

Her komut `--json` flagı ile JSON çıktısı destekler.

## Kullanım

```bash
fedcare health
fedcare services --json
fedcare backup --dest ~/yedek
fedcare startup --top 15
fedcare clean --apply
```

## Gereksinimler

- Fedora Linux
- Python 3.10+
