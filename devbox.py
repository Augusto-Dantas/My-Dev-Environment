#!/usr/bin/env python3
"""Project scaffolding and Docker development-container launcher."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "my-dev-environment"
ROOT = Path(os.environ.get("DEVBOX_HOME", Path.home() / ".local/share/my-dev-environment"))
COMPOSE = ROOT / "source/docker-compose.yml"
ENV_FILE = ROOT / ".env"

GITIGNORES = {
    "Python": "__pycache__/\n*.py[cod]\n.venv/\nvenv/\n.env\n.pytest_cache/\n",
    "Rust": "/target/\nCargo.lock\n",
    "Node.js": "node_modules/\ndist/\nbuild/\n.env\n",
    "C/C++": "build/\ncmake-build-*/\n*.o\n*.a\n*.so\n",
    "Go": "/vendor/\n*.exe\n*.test\n",
    "Java": "target/\n*.class\n.gradle/\nbuild/\n",
    "General": ".DS_Store\nThumbs.db\n.env\n.vscode/\n.idea/\n",
}

MIT_LICENSE = """MIT License

Copyright (c) {year} {owner}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
"""

def key_for(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()

def ask(prompt: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    return input(f"{prompt} [{suffix}] ").strip().lower() in ({"y", "yes"} if not default else {"y", "yes", ""})

def choose(prompt: str, options: list[str], default: int = 0) -> str:
    print(prompt)
    for i, option in enumerate(options, 1):
        marker = " (default)" if i - 1 == default else ""
        print(f"  {i}. {option}{marker}")
    while True:
        raw = input(f"Select [1-{len(options)}] (default {default + 1}): ").strip()
        if not raw:
            return options[default]
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print("Invalid selection.")

def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

def registered_containers() -> list[dict]:
    result = []
    folder = CONFIG / "containers"
    if folder.exists():
        for file in sorted(folder.glob("*.json")):
            data = load_json(file)
            if data and data.get("name") and data.get("workspace_root"):
                result.append(data)
    return result

def project_config(directory: Path) -> dict | None:
    current = directory.resolve()
    for candidate in (current, *current.parents):
        config = load_json(CONFIG / "projects" / f"{key_for(str(candidate))}.json")
        if config:
            return config
    return None

def compose(profile: dict, workspace: Path, command: list[str]) -> int:
    if not COMPOSE.exists() or not ENV_FILE.exists():
        print("Devbox is not installed correctly. Run the installer again.", file=sys.stderr)
        return 1
    root = Path(profile["workspace_root"]).expanduser().resolve()
    try:
        relative = workspace.resolve().relative_to(root)
    except ValueError:
        print(f"Project directory must be inside the container workspace: {root}", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env.update({
        "DEVBOX_WORKSPACE": str(root),
        "DEVBOX_CONTAINER_NAME": profile["name"],
    })
    project_id = profile.get("compose_project") or ("devbox-" + key_for(str(root))[:10])
    args = ["docker", "compose", "--env-file", str(ENV_FILE), "-f", str(COMPOSE),
            "--project-directory", str(COMPOSE.parent), "-p", project_id]
    action = command[0] if command else "shell"
    if action == "up":
        return subprocess.call(args + ["up", "-d", "--build"], env=env)
    if action == "down":
        return subprocess.call(args + ["down"], env=env)
    if action == "restart":
        return subprocess.call(args + ["up", "-d", "--build", "--force-recreate"], env=env)
    if action in ("status", "ps"):
        return subprocess.call(args + ["ps"], env=env)
    if action == "logs":
        return subprocess.call(args + ["logs", "-f"], env=env)
    if action in ("shell", "sh"):
        code = subprocess.call(args + ["up", "-d", "--build"], env=env)
        if code:
            return code
        workdir = "/workspace" if str(relative) == "." else f"/workspace/{relative.as_posix()}"
        return subprocess.call(args + ["exec", "-w", workdir, "devenv", "zsh"], env=env)
    print(f"Unknown command: {action}", file=sys.stderr)
    return 2

def create_project() -> int:
    name = input("Project name: ").strip()
    if not name or name in (".", "..") or "/" in name or "\\" in name:
        print("Please enter a valid project directory name.", file=sys.stderr)
        return 2

    containers = registered_containers()
    options = [f"{item['name']} ({item['workspace_root']})" for item in containers]
    options.append("Create a new container")
    selected = choose("Which development container should host this project?", options, len(options) - 1)
    profile = None
    if selected == "Create a new container":
        parent = Path(input(f"Project parent directory [{Path.cwd()}]: ").strip() or Path.cwd()).expanduser().resolve()
        target = parent / name
        container_name = input(f"New container name [devbox-{key_for(str(target))[:8]}]: ").strip()
        if not container_name:
            container_name = "devbox-" + key_for(str(target))[:8]
        if any(item["name"] == container_name for item in containers):
            print("A container with that name is already registered.", file=sys.stderr)
            return 2
        profile = {
            "name": container_name,
            "workspace_root": str(target),
            "compose_project": "devbox-" + key_for(str(target))[:10],
        }
    else:
        index = options.index(selected)
        profile = containers[index]
        parent = Path(profile["workspace_root"]).expanduser().resolve()
        target = parent / name

    if target.exists():
        print(f"Target already exists: {target}", file=sys.stderr)
        return 2

    language = choose("Project type:", ["General", *GITIGNORES.keys()], 0)
    use_git = ask("Initialize a Git repository?", True)
    add_readme = ask("Create a README.md?", True)
    add_gitignore = ask("Create a .gitignore?", True)
    license_choice = choose("Add a license?", ["None", "MIT"], 1)
    publish = ask("Create a GitHub repository with GitHub CLI (gh)?", False)
    visibility = "private"
    if publish:
        visibility = choose("GitHub repository visibility:", ["Private", "Public"], 0).lower()
        if not shutil.which("gh"):
            print("GitHub CLI (gh) is not installed. Skipping GitHub creation.")
            publish = False
        elif subprocess.call(["gh", "auth", "status"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            print("GitHub CLI is not authenticated. Run 'gh auth login' and try again.")
            publish = False

    target.mkdir(parents=True)
    if add_readme:
        (target / "README.md").write_text(f"# {name}\n\nProject description.\n", encoding="utf-8")
    if add_gitignore:
        content = GITIGNORES.get(language, GITIGNORES["General"])
        if language != "General":
            content += GITIGNORES["General"]
        (target / ".gitignore").write_text(content, encoding="utf-8")
    if license_choice == "MIT":
        owner = os.environ.get("GIT_AUTHOR_NAME") or os.environ.get("USER") or "Copyright holder"
        (target / "LICENSE").write_text(MIT_LICENSE.format(year=__import__("datetime").date.today().year, owner=owner), encoding="utf-8")

    if use_git:
        init = subprocess.run(["git", "init", "-b", "main", str(target)], capture_output=True, text=True)
        if init.returncode:
            subprocess.run(["git", "init", str(target)], check=True)
        subprocess.run(["git", "-C", str(target), "add", "."], check=True)
        subprocess.run(["git", "-C", str(target), "commit", "-m", "Initial project setup"], check=False)

    container_dir = CONFIG / "containers"
    container_dir.mkdir(parents=True, exist_ok=True)
    save_json(container_dir / f"{key_for(profile['name'])}.json", profile)
    save_json(CONFIG / "projects" / f"{key_for(str(target.resolve()))}.json", profile)

    if publish:
        command = ["gh", "repo", "create", name, f"--{visibility}", "--source", str(target), "--remote", "origin"]
        if use_git:
            command.append("--push")
        result = subprocess.run(command, cwd=target)
        if result.returncode:
            print("Project was created locally, but GitHub repository creation failed.", file=sys.stderr)

    print(f"\nProject created: {target}")
    print(f"Linked container: {profile['name']}")
    print(f"Enter the project and run 'devbox' to open its development environment.")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="devbox",
        description="Manage your Docker development environments and scaffold projects.",
        epilog="Run 'devbox new' to create a project with an interactive setup wizard.",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("new", help="Create a project using the interactive project wizard")
    sub.add_parser("shell", help="Start the linked container and open Zsh")
    sub.add_parser("up", help="Build and start the linked container in the background")
    sub.add_parser("down", help="Stop and remove the linked container")
    sub.add_parser("restart", help="Rebuild and restart the linked container")
    sub.add_parser("status", aliases=["ps"], help="Show the linked container status")
    sub.add_parser("logs", help="Follow linked container logs")
    args = parser.parse_args()

    if args.command == "new":
        return create_project()
    if args.command is None:
        args.command = "shell"
    cwd = Path.cwd().resolve()
    profile = project_config(cwd)
    if profile is None:
        # Backward-compatible behavior for directories not created with 'devbox new'.
        profile = {
            "name": "devbox-" + key_for(str(cwd))[:10],
            "workspace_root": str(cwd),
            "compose_project": "devbox-" + key_for(str(cwd))[:10],
        }
    command = ["status" if args.command == "ps" else args.command]
    return compose(profile, cwd, command)

if __name__ == "__main__":
    raise SystemExit(main())
