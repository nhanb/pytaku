#!/usr/bin/env python3
import shlex
import subprocess
from pathlib import Path
from sys import argv


def main():
    if len(argv) == 1:
        build_js()
        build_py()
        return

    if len(argv) == 2:
        # I prefer explicitly listing all possible commands here,
        # for both safety and readability.
        commands = {
            "js": build_js,
            "py": build_py,
            "deploy": deploy,
        }
        commands[argv[1]]()


def build_js():
    run(
        "esbuild",
        "src/pytaku/js-src/main.js",
        "--bundle",
        "--sourcemap",
        "--minify",
        "--outfile=src/pytaku/static/js/main.min.js",
    )


def build_py():
    run("uv", "build")


def deploy():
    hostname = "pytaku-1"

    # Ensure necessary dirs
    run("ssh", hostname, "mkdir", "-p", "/opt/pytaku/workdir", "/opt/pytaku/venv")

    # Upload and install latest source distribution
    sdist = list(path for path in Path("dist").glob("*.tar.gz"))[0]
    run("scp", str(sdist), f"{hostname}:/tmp/pytaku.tar.gz")
    run(
        "ssh",
        hostname,
        "/opt/pytaku/venv/bin/pip",
        "install",
        "--force-reinstall",
        "/tmp/pytaku.tar.gz",
    )
    run(
        "ssh",
        hostname,
        "/opt/pytaku/venv/bin/pytaku-collect-static",
        "/opt/pytaku/workdir",
    )

    # Install & restart systemd services
    services = ("pytaku", "pytaku-scheduler")
    for service in services:
        run(
            "scp",
            f"contrib/systemd/{service}.service",
            f"{hostname}:/etc/systemd/system/",
        )
    run("ssh", hostname, "systemctl", "daemon-reload")
    run("ssh", hostname, "systemctl", "restart", *services)


def run(*cmd):
    print("RUN:", " ".join(shlex.quote(arg) for arg in cmd))
    return subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
