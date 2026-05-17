# 🏠 My Homelab – Private Cloud with Docker

## 📌 Overview

A self-hosted homelab built with Docker Compose, managed by a Python [Invoke](https://www.pyinvoke.org/) task runner. Designed to replace traditional cloud services like Google Drive and Dropbox while keeping full control over personal data.

**Goals:**
- Full control over personal data with improved privacy
- Access services from any device, anywhere via Tailscale VPN
- Custom DNS with Pi-hole for clean local hostnames
- Hands-on experience with infrastructure, networking, and DevOps

---

## 🧱 Architecture

```
Remote Device (Tailscale)        Local Device (LAN / Tailscale)
         │                                    │
         │ WireGuard tunnel                   │
         ▼                                    ▼
   Tailscale Network ──────────────▶ Your Server (192.168.0.x)
   (subnet routing)                           │
                                              │
                              ┌───────────────┼────────────────────┐
                              ▼               ▼                    ▼
                       🌐 NPM (80/443)   🛡️ Pi-hole (53)   📊 Dashboard (8888)
                       Reverse proxy     DNS + ad block     Health monitor
                              │
              ┌───────────────┼───────────────┐
              ▼                               ▼
       ☁️ Nextcloud (8080)           📚 Calibre-Web (8083)
       Private cloud storage         eBook library
              │
       ┌──────┴──────┐
       ▼             ▼
  🗄️ MariaDB     ⚡ Redis
  (database)    (cache)
```

All containers communicate over a shared Docker network (`homelab_network`). Pi-hole resolves custom hostnames (e.g. `nextcloud.momos`) to the server's LAN IP. Tailscale subnet routing makes the whole LAN reachable remotely.

---

## ⚙️ Tech Stack

| Tool | Purpose |
|---|---|
| Docker & Docker Compose | Container orchestration |
| Nextcloud | Private cloud storage platform |
| MariaDB | Relational database for Nextcloud |
| Redis | Caching layer for Nextcloud |
| Calibre-Web Automated | eBook library management |
| Nginx Proxy Manager | Reverse proxy and SSL management |
| Pi-hole | Network-wide DNS ad blocker and custom DNS |
| FastAPI + uvicorn | Service health dashboard |
| Tailscale | Zero-config VPN for secure remote access |
| Invoke (Python) | Task automation (`tasks.py`) |
| uv | Python package and environment management |

---

## 📦 Services

### ☁️ Nextcloud
Private cloud storage with file sync, user management, and a web interface.

| | |
|---|---|
| Access | `http://nextcloud.momos` |
| Direct access | `http://localhost:8080` |
| Backend | MariaDB + Redis |

---

### 📚 Calibre-Web Automated
eBook library management with automatic book ingestion from a watched folder.

| | |
|---|---|
| Access | `http://calibreweb.momos` or `http://localhost:8083` |
| Book ingest | `/Volumes/Elements/homelab/calibre-web/import` |
| Library | `/Volumes/Elements/homelab/calibre-web/library` |

---

### 🌐 Nginx Proxy Manager
Reverse proxy that routes traffic by hostname, handles SSL termination, and serves as the public entry point for all services.

| | |
|---|---|
| Admin UI | `http://localhost:81` |
| Default login | `admin@example.com` / `changeme` (change on first login) |
| HTTP / HTTPS | ports 80 / 443 |

---

### 🛡️ Pi-hole
Network-wide DNS server and ad blocker. Provides custom DNS entries so services are accessible by hostname instead of IP.

| | |
|---|---|
| Admin UI | `http://localhost:8081` |
| DNS port | 53 (TCP + UDP) |
| Custom DNS | Managed via Admin UI → Local DNS → DNS Records |

**Custom hostnames configured:**

| Hostname | Resolves to |
|---|---|
| `nextcloud.momos` | `192.168.0.19` |
| `calibreweb.momos` | `192.168.0.19` |
| `immich.momos` | `192.168.0.19` |
| `gitea.momos` | `192.168.0.19` |
| `uptime-kuma.momos` | `192.168.0.19` |
| `portainer.momos` | `192.168.0.19` |
| `pihole.momos` | `192.168.0.19` |
| `npm.momos` | `192.168.0.19` |

---

### 📷 Immich
Self-hosted photo and video library with automatic mobile backup, face recognition, and timeline view.

| | |
|---|---|
| Access | `http://immich.momos` or `http://localhost:2283` |
| Backend | PostgreSQL (pgvecto-rs) + Redis + ML container |
| Library | `/Volumes/Elements/homelab/immich/library` |

---

### 📊 Uptime Kuma
Service monitoring dashboard with uptime tracking, response time graphs, and alerts (email, Telegram, Slack, etc.).

| | |
|---|---|
| Access | `http://uptime-kuma.momos` or `http://localhost:3001` |

---

### 🐳 Portainer
Docker container management UI. Start, stop, inspect, and manage all containers and volumes from a browser — no terminal required.

| | |
|---|---|
| Access | `http://portainer.momos` or `http://localhost:9000` |
| Note | Admin-only — do not share this link with other users |

---

### 🐙 Gitea
Self-hosted Git service with repositories, issues, pull requests, and CI/CD via Gitea Actions.

| | |
|---|---|
| Web UI | `http://gitea.momos` or `http://localhost:3000` |
| SSH clone | `git clone ssh://git@localhost:2222/user/repo.git` |
| Database | SQLite (built-in) |

---

## 🔒 Remote Access via Tailscale

Services are not exposed to the public internet. Remote access is handled by [Tailscale](https://tailscale.com) using subnet routing — all devices on your Tailnet can reach the entire home network (`192.168.0.0/24`) through an encrypted WireGuard tunnel.

### Setup (run once on the server)

```bash
# Advertise local subnet to Tailscale
sudo tailscale up --advertise-routes=192.168.0.0/24 --accept-routes
```

Then in the **Tailscale admin console**:
1. **Machines** → your machine → **Edit route settings** → approve `192.168.0.0/24`
2. **DNS** → **Add nameserver** → `192.168.0.19` → enable **Override local DNS**

After this, all Tailscale-connected devices automatically use Pi-hole for DNS and can reach all services by hostname from anywhere.

---

## 🗂️ Project Structure

```
services/
├── nextcloud/          # Nextcloud + MariaDB + Redis
├── calibre-web/        # Calibre-Web Automated
├── npm/                # Nginx Proxy Manager
├── pi_hole/            # Pi-hole DNS server
├── immich/             # Immich photo & video library
├── gitea/              # Self-hosted Git service
├── uptime-kuma/        # Uptime monitoring
├── portainer/          # Docker container management UI
└── dashboard/          # Home screen + health dashboard (FastAPI)

tasks.py                # Invoke task runner
pyproject.toml          # Python project config (uv)
.env.template           # Environment variable template
.env                    # Local secrets (not committed)
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <repo-url>
cd homelab
```

### 2. Setup environment

```bash
uv run inv setup
```

Copy `.env.template` to `.env` and fill in the required variables:

```bash
MYSQL_ROOT_PASSWORD=
MYSQL_PASSWORD=
MYSQL_DATABASE=nextcloud
MYSQL_USER=nextcloud
HARDCOVER_TOKEN=
```

### 3. Start all services

```bash
uv run inv up --all
```

Or start specific services:

```bash
uv run inv up --nextcloud
uv run inv up --calibre
uv run inv up --npm
uv run inv up --pi-hole
uv run inv up --dashboard
```

### 4. Stop services

```bash
uv run inv down --all
```

### 5. Check status

```bash
uv run inv status
```

### 6. View logs

```bash
uv run inv logs --service nextcloud
```

### 7. Sync Nextcloud files

```bash
uv run inv scan
```

---

## 💾 Data Persistence

| Service | Data Location |
|---|---|
| Nextcloud files | `./services/nextcloud/data/nextcloud_data` |
| Nextcloud DB | `./services/nextcloud/nextcloud_db` |
| Nextcloud ext. | `/Volumes/Elements/homelab/nextcloud/` |
| Calibre-Web config | `./services/calibre-web/data/config` |
| Calibre library | `/Volumes/Elements/homelab/calibre-web/library` |
| Calibre ingest | `/Volumes/Elements/homelab/calibre-web/import` |
| NPM data | `./services/npm/data/` |
| Pi-hole config | `./services/pi_hole/data/pihole/` |

---

## 🔐 Security Notes

- Services are behind NAT — not directly reachable from the internet
- Remote access uses Tailscale (WireGuard encryption, no open inbound ports)
- Anyone on the local WiFi can reach all services directly
- Do **not** port-forward ports 53, 8080, 8081, 8083, or 8888 on your router

---

## ⚠️ Known Limitations

- No HTTPS inside the local network (traffic between browser and services is unencrypted on LAN)
- No automated backup strategy
- External USB volume path (`/Volumes/Elements/`) is macOS-specific — update paths when migrating to Linux
