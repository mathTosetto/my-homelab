import os

from textwrap import dedent
from pathlib import Path
from invoke import task

# ================ Configuration ================= #

SCRIPTS_DIR: str = "services"
SERVICES: dict[str, str] = {
    "nextcloud": f"{SCRIPTS_DIR}/nextcloud",
    "calibre": f"{SCRIPTS_DIR}/calibre-web",
    "npm": f"{SCRIPTS_DIR}/npm",
}

CALIBRE_DATA_DIR: str = "./services/calibre-web/calibre"
METADATA_URL: str = (
    "https://github.com/janeczku/calibre-web/raw/master/library/metadata.db"
)
NETWORK_NAME: str = "homelab_network"

# ================ Helper Functions ================= #


def format_print(message: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 15} {message} {'=' * 15}")


def ensure_file_exists(path: Path, default_content: str = ""):
    """Create a file if it does not exist."""
    if not path.exists():
        print(f"  - Creating missing file: {path}")
        path.write_text(default_content)
    else:
        print(f"  - File already exists: {path}")


def ensure_precommit_config():
    """Create a minimal .pre-commit-config.yaml if missing."""
    pre_commit_file: Path = Path(".pre-commit-config.yaml")

    default_config: str = dedent("""
    repos:
    - repo: https://github.com/pre-commit/pre-commit-hooks
      rev: v6.0.0
      hooks:
        - id: trailing-whitespace
          name: Trim trailing whitespace
        - id: check-yaml
          name: Validate YAML
        - id: check-json
          name: Validate JSON
        - id: check-toml
          name: Validate TOML
        - id: check-added-large-files
          name: Validate large files

    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.12.8
      hooks:
        - id: ruff
          name: Ruff Linter
          description: "Run 'ruff' for extremely fast Python linting"
          language: python
        - id: ruff-format
          name: Ruff Code Format
          description: "Run 'ruff format' for extremely fast Python formatting"
          language: python
    """)

    ensure_file_exists(pre_commit_file, default_config)


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
        print("Action: metadata.db missing. Fetching raw binary from GitHub...")
        c.run(f"curl -L {METADATA_URL} -o {db_path}")
        c.run(f"chmod 777 {db_path}")
        print(f"Success: Valid metadata.db placed in {db_path}")
    else:
        print("Status: metadata.db already exists. Skipping download.")


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


@task(
    help={
        "nextcloud": "Start the Nextcloud service",
        "calibre": "Start the Calibre-Web service",
        "npm": "Start the npm service",
        "all": "Start all services (default)",
    }
)
def up(c, nextcloud=False, calibre=False, npm=False, all=False):
    """Start Docker services and auto-prepare requirements."""
    format_print("Docker Up Task")

    ensure_network(c)

    selected = []
    if nextcloud:
        selected.append("nextcloud")
    if calibre:
        selected.append("calibre")
    if npm:
        selected.append("npm")

    if all or not selected:
        selected = list(SERVICES.keys())

    # if "calibre" in selected:
    #     ensure_metadata(c)

    for service in selected:
        run_compose(c, service, "up -d")

    if "calibre" in selected:
        print("\n[Access] Calibre-Web: http://localhost:8083 (DB Path: /books)")
    if "nextcloud" in selected:
        print("[Access] Nextcloud:   http://localhost:8080")
    if "npm" in selected:
        print("[Access] npm:   http://localhost:81")

    format_print("Docker Up Done")


@task(
    help={
        "nextcloud": "Stop the Nextcloud service",
        "calibre": "Stop the Calibre-Web service",
        "npm": "Stop the npm service",
        "all": "Stop all services (default)",
    }
)
def down(c, nextcloud=False, calibre=False, npm=False, all=False):
    """Stop Docker services modularly."""
    format_print("Docker Down Task")

    selected = []
    if nextcloud:
        selected.append("nextcloud")
    if calibre:
        selected.append("calibre")
    if npm:
        selected.append("npm")

    if all or not selected:
        selected = list(SERVICES.keys())

    for service in reversed(selected):
        run_compose(c, service, "down")

    format_print("Docker Down Done")


@task
def status(c):
    """Check the status of the homelab containers."""
    format_print("Stack Status")
    c.run("docker ps --filter 'name=nextcloud|calibre|npm'")


@task
def scan(c):
    """Force Nextcloud to scan for new files added by Calibre."""
    format_print("Syncing Nextcloud Filesystem")
    print("Action: Scanning 'Livros' folder for changes...")
    c.run("docker exec -u 33 nextcloud php occ files:scan user123")
    format_print("Sync Complete")


@task
def logs(c, service):
    """Follow logs for a specific service (nextcloud, npm, or calibre)."""
    folder = SERVICES.get(service)
    if folder:
        with c.cd(folder):
            c.run("docker compose logs -f")
    else:
        print(f"Error: Service {service} not found.")


@task
def setup(c):
    """Setup the project environment (git, .env, pre-commit)."""
    format_print("Setup Task")

    print("→ Checking Git repository...")
    if not Path(".git").exists():
        print("  - Initializing Git repository...")
        c.run("git init")
    else:
        print("  - Git already initialized.")

    print("→ Ensuring environment files...")

    ensure_file_exists(Path(".env.template"), default_content="# ENV template\n")

    env_file: Path = Path(".env")
    env_template: Path = Path(".env.template")

    if not env_file.exists():
        print("  - Creating .env from .env.template")
        env_file.write_text(env_template.read_text())
    else:
        print("  - .env already exists.")

    print("→ Ensuring .pre-commit-config.yaml exists...")
    ensure_precommit_config()

    print("→ Installing pre-commit hooks...")
    c.run("pre-commit clean", warn=True)
    c.run("pre-commit autoupdate")
    c.run("pre-commit install")

    print("→ To activate your venv, run: eval $(poetry env activate)")

    format_print("Setup Task Done!")
    print("\n")
