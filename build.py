#!/usr/bin/env python3
import shlex
import subprocess
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


def run(*cmd):
    print("RUN:", " ".join(shlex.quote(arg) for arg in cmd))
    return subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
