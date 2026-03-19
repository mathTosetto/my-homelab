import os
from invoke import task

# ================ Configuration ================= #

# Root relative paths to service orchestration folders
SCRIPTS_DIR: str = "services"
SERVICES: dict[str, str] = {
    "nextcloud": f"{SCRIPTS_DIR}/nextcloud",
    "calibre": f"{SCRIPTS_DIR}/calibre-web",
    "nginx": f"{SCRIPTS_DIR}/nginx",
}

# Data folders and external resources
CALIBRE_DATA_DIR: str = "./services/calibre-web/calibre"
METADATA_URL: str = "https://github.com/janeczku/calibre-web/raw/master/library/metadata.db"
NETWORK_NAME: str = "homelab_network"

# ================ Helper Functions ================= #

def format_header(message: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 15} {message} {'=' * 15}")

def ensure_network(c):
    """Ensure the external docker network exists."""
    networks = c.run("docker network ls", hide=True).stdout
    if NETWORK_NAME not in networks:
        print(f"Action: Creating external network '{NETWORK_NAME}'...")
        c.run(f"docker network create {NETWORK_NAME}")
    else:
        print(f"Status: Network '{NETWORK_NAME}' already exists.")

def ensure_metadata(c):
    """Downloads a fresh metadata.db if it is missing from the data folder."""
    db_path = os.path.join(CALIBRE_DATA_DIR, "metadata.db")
    
    if not os.path.exists(CALIBRE_DATA_DIR):
        print(f"Action: Creating directory {CALIBRE_DATA_DIR}")
        os.makedirs(CALIBRE_DATA_DIR)

    if not os.path.exists(db_path):
        print(f"Action: metadata.db missing. Fetching raw binary from GitHub...")
        # -L follows redirects, -o defines output path
        c.run(f"curl -L {METADATA_URL} -o {db_path}")
        c.run(f"chmod 777 {db_path}")
        print(f"Success: Valid metadata.db placed in {db_path}")
    else:
        print(f"Status: metadata.db already exists. Skipping download.")

def run_compose(c, service_alias: str, action: str):
    """Execute docker compose command in the service directory."""
    folder = SERVICES.get(service_alias)
    
    if not folder or not os.path.exists(folder):
        print(f"Error: Directory '{folder}' not found. Check your file structure.")
        return

    print(f"Step: Running {action.upper()} on {service_alias} (Folder: {folder})")
    with c.cd(folder):
        c.run(f"docker compose {action}")

# ================ Tasks ================= #

@task(help={
    "nextcloud": "Start the Nextcloud service",
    "calibre": "Start the Calibre-Web service",
    "nginx": "Start the Nginx service",
    "all": "Start all services (default)"
})
def up(c, nextcloud=False, calibre=False, nginx=False, all=False):
    """Start Docker services and auto-prepare requirements."""
    format_header("Docker Up Task")
    
    ensure_network(c)

    # Determine which services to start
    selected = []
    if nextcloud: selected.append("nextcloud")
    if calibre: selected.append("calibre")
    if nginx: selected.append("nginx")

    # Default to all if no specific flags are provided
    if all or not selected:
        selected = list(SERVICES.keys())

    # Pre-flight check: Calibre needs the database file to mount correctly
    if "calibre" in selected:
        ensure_metadata(c)

    for service in selected:
        run_compose(c, service, "up -d")

    # Feedback for the user
    if "calibre" in selected:
        print("\n[Access] Calibre-Web: http://localhost:8083 (DB Path: /books)")
    if "nextcloud" in selected:
        print("[Access] Nextcloud:   http://localhost:8080")
    if "nginx" in selected:
        print("[Access] Nginx:   http://localhost:81")

    format_header("Docker Up Done")

@task(help={
    "nextcloud": "Stop the Nextcloud service",
    "calibre": "Stop the Calibre-Web service",
    "nginx": "Stop the Nginx service",
    "all": "Stop all services (default)"
})
def down(c, nextcloud=False, calibre=False, nginx=False, all=False):
    """Stop Docker services modularly."""
    format_header("Docker Down Task")

    selected = []
    if nextcloud: selected.append("nextcloud")
    if calibre: selected.append("calibre")
    if nginx: selected.append("nginx")

    if all or not selected:
        selected = list(SERVICES.keys())

    # Reverse order: Stop Apps (NC/Calibre) before Database
    for service in reversed(selected):
        run_compose(c, service, "down")

    format_header("Docker Down Done")

@task
def status(c):
    """Check the status of the homelab containers."""
    format_header("Stack Status")
    c.run("docker ps --filter 'name=nextcloud|calibre|nginx'")

@task
def scan(c):
    """Force Nextcloud to scan for new files added by Calibre."""
    format_header("Syncing Nextcloud Filesystem")
    print("Action: Scanning 'Livros' folder for changes...")
    # This assumes your container is named 'nextcloud' as per your YAML
    c.run("docker exec -u 33 nextcloud php occ files:scan user123")
    format_header("Sync Complete")

@task
def logs(c, service):
    """Follow logs for a specific service (nextcloud, nginx, or calibre)."""
    folder = SERVICES.get(service)
    if folder:
        with c.cd(folder):
            c.run("docker compose logs -f")
    else:
        print(f"Error: Service {service} not found.")