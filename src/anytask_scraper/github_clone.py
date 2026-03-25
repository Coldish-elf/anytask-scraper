from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_NON_REPO_ACTIONS = frozenset(
    {"pull", "pulls", "commit", "issues", "releases", "actions", "settings", "wiki"}
)


@dataclass
class GitHubRepoInfo:
    owner: str
    repo: str
    branch: str | None = None
    url: str = ""


@dataclass
class CloneResult:
    success: bool
    path: Path
    reason: str = ""


def parse_github_url(url: str) -> GitHubRepoInfo | None:
    parsed = urlparse(url)
    if parsed.netloc.lower() not in ("github.com", "www.github.com"):
        return None

    segments = [s for s in parsed.path.strip("/").split("/") if s]
    if len(segments) < 2:
        return None

    owner = segments[0]
    repo = segments[1].removesuffix(".git")
    if repo in _NON_REPO_ACTIONS:
        return None

    branch: str | None = None
    if len(segments) >= 3:
        action = segments[2]
        if action in _NON_REPO_ACTIONS:
            return None
        if action == "tree" and len(segments) >= 4:
            branch = "/".join(segments[3:])
        elif action == "blob" and len(segments) >= 4:
            branch = segments[3]

    return GitHubRepoInfo(owner=owner, repo=repo, branch=branch, url=url)


def extract_github_links(links: list[str]) -> list[GitHubRepoInfo]:
    seen: set[tuple[str, str, str | None]] = set()
    results: list[GitHubRepoInfo] = []

    for link in links:
        info = parse_github_url(link)
        if info is None:
            continue
        key = (info.owner, info.repo, info.branch)
        if key not in seen:
            seen.add(key)
            results.append(info)

    return results


def clone_github_repo(
    info: GitHubRepoInfo,
    dest_dir: Path,
    timeout: int = 120,
) -> CloneResult:
    clone_url = f"https://github.com/{info.owner}/{info.repo}.git"
    target = dest_dir / info.repo

    if target.exists():
        if (target / ".git").is_dir():
            logger.debug("Repo already cloned at %s", target)
            return CloneResult(success=True, path=target, reason="already_cloned")
        logger.warning("Target dir exists but is not a git repo: %s", target)
        return CloneResult(success=False, path=target, reason="dir_exists_not_git")

    try:
        logger.info("Cloning %s → %s", clone_url, target)
        subprocess.run(
            ["git", "clone", clone_url, str(target)],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True,
        )
        if info.branch is not None:
            logger.info("Checking out branch %s in %s", info.branch, target)
            subprocess.run(
                ["git", "checkout", info.branch],
                cwd=str(target),
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
        return CloneResult(success=True, path=target)
    except FileNotFoundError:
        logger.error("git executable not found")
        return CloneResult(success=False, path=target, reason="git_not_found")
    except subprocess.TimeoutExpired:
        logger.error("git clone timed out for %s", clone_url)
        return CloneResult(success=False, path=target, reason="timeout")
    except subprocess.CalledProcessError as e:
        reason = e.stderr.strip() if e.stderr else str(e)
        logger.error("git command failed for %s: %s", clone_url, reason)
        return CloneResult(success=False, path=target, reason=reason)
