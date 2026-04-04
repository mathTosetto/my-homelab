# 🏠 My Homelab – Private Cloud with Docker

## 📌 Overview

This project is a self-hosted private cloud built using Docker, designed to replace traditional cloud services like Google Drive and Dropbox.

The main goal is to provide:
- Full control over personal data
- Improved privacy
- Reduced dependency on third-party cloud providers
- Hands-on experience with infrastructure, networking, and DevOps concepts

---

## 🎯 Objectives

- Store and manage personal files securely
- Host a personal eBook library
- Access services from any device (PC, phone, tablet)
- Build a scalable and maintainable homelab environment

---

## 🧱 Architecture

                📱 User (phone / PC)
                           │
                           │ HTTP / HTTPS
                           ▼
                🌐 Nginx Proxy Manager
                  (port 80 / 443 / 81)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ☁️ Nextcloud      📚 Calibre-Web     (outros serviços futuros)
   (porta 8080)      (porta 8083)
        │
        │
   ┌────┴───────────────┐
   ▼                    ▼
🗄️ MariaDB          ⚡ Redis
(banco de dados)   (cache/memória)

---

## ⚙️ Tech Stack

- **Docker & Docker Compose** – container orchestration
- **Nextcloud** – private cloud storage platform
- **MariaDB** – relational database
- **Redis** – caching layer
- **Calibre-Web** – eBook management system
- **Nginx Proxy Manager** – reverse proxy and access management
- **Invoke (Python)** – task automation

---

## 📦 Services

### ☁️ Nextcloud
- File storage and synchronization
- User management
- Web interface similar to Google Drive

Access:
    http://localhost:8080

---

### 📚 Calibre-Web
- eBook library management
- PDF reading and organization

Access:
    http://localhost:8083

---

### 🌐 Nginx Proxy Manager
- Reverse proxy for routing traffic
- SSL/TLS management (future)

Access:
    http://localhost:81

---

## 🗂️ Project Structure

    services/
    ├── nextcloud/
    ├── calibre-web/
    └── nginx/

    tasks.py
    .env.template
    pyproject.toml

---

## 🚀 Getting Started

### 1. Clone the repository

``bash
git clone <repo-url>
cd my-homelab

### 2. Setup environment

invoke setup

### 3. Start Services

invoke up

or specifics services:

    invoke up --nextcloud
    invoke up --calibre
    invoke up --nginx

### 4. Stop Services

invoke down

### 5. Check Status

invoke status

### 6. View Logs

invoke logs --service=nextcloud

---

## 💾 Data Persistence

All data is stored locally on the host machine using Docker volumes.

    | Service     | Data Location                       |
    | ----------- | ----------------------------------- |
    | Nextcloud   | ./services/nextcloud/nextcloud_data |
    | MariaDB     | ./services/nextcloud/nextcloud_db   |
    | Calibre-Web | ./services/calibre-web/calibre      |
    | Nginx       | ./services/nginx/nginx_data         |

---

## 🔐 Core Principles

- Privacy First
- Self-Hosting
- Modularity
- Simplicity
- Extensibility

---

## ⚠️ Current Limitations

- Credentials not externalized
- No backup strategy
- Reverse proxy not configured
- No secure external access

---