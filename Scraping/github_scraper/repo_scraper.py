"""
Repository scraper — fetches metadata for **all** public repositories.

For each repository it collects:
  - Full metadata (name, description, topics, language, stars, forks, …)
  - Detailed language breakdown (bytes per language)
  - Commit count
  - Contributor count
  - README content (raw markdown)
  - Last 10 commits (author, date, message, SHA)
"""

import base64
import logging
import re
from typing import Any, Dict, List, Optional

from github_scraper.client import GitHubClient

logger = logging.getLogger("github_scraper.repo")


def scrape_repositories(
    client: GitHubClient,
    username: str,
    include_forks: bool = False,
) -> List[Dict[str, Any]]:
    """
    Fetch and enrich metadata for every public repository of a user.

    Parameters
    ----------
    client : GitHubClient
        Authenticated API client.
    username : str
        GitHub username.
    include_forks : bool
        If *False* (default), forked repos are skipped.

    Returns
    -------
    list[dict]
        List of enriched repository dictionaries.
    """
    logger.info("Fetching all repositories for %s (include_forks=%s)", username, include_forks)

    raw_repos = client.get_paginated(f"/users/{username}/repos", params={"sort": "updated"})
    logger.info("Found %d total repositories for %s.", len(raw_repos), username)

    enriched_repos: List[Dict[str, Any]] = []

    for idx, repo in enumerate(raw_repos, start=1):
        repo_name = repo.get("name", "unknown")

        if repo.get("fork") and not include_forks:
            logger.info("[%d/%d] Skipping forked repo: %s", idx, len(raw_repos), repo_name)
            continue

        logger.info("[%d/%d] Processing repo: %s", idx, len(raw_repos), repo_name)

        enriched = _extract_repo_metadata(repo)

        # ── Language breakdown ──────────────────────────────────────────
        enriched["languages"] = _fetch_languages(client, username, repo_name)

        # ── Commit count ────────────────────────────────────────────────
        enriched["commit_count"] = _fetch_commit_count(client, username, repo_name)

        # ── Contributor count ───────────────────────────────────────────
        enriched["contributor_count"] = _fetch_contributor_count(client, username, repo_name)

        # ── README ──────────────────────────────────────────────────────
        enriched["readme_content"] = _fetch_readme(client, username, repo_name)

        # ── Recent commits ──────────────────────────────────────────────
        enriched["recent_commits"] = _fetch_recent_commits(client, username, repo_name)

        enriched_repos.append(enriched)
        logger.debug("Finished enriching repo: %s", repo_name)

    logger.info("Finished processing %d repositories for %s.", len(enriched_repos), username)
    return enriched_repos


# ═══════════════════════════════════════════════════════════════════════════
#  Private helpers
# ═══════════════════════════════════════════════════════════════════════════


def _extract_repo_metadata(repo: Dict) -> Dict[str, Any]:
    """Extract the core metadata fields from the raw repo JSON."""
    license_info = repo.get("license")
    return {
        "name": repo.get("name"),
        "full_name": repo.get("full_name"),
        "html_url": repo.get("html_url"),
        "description": repo.get("description"),
        "topics": repo.get("topics", []),
        "primary_language": repo.get("language"),
        "stars": repo.get("stargazers_count"),
        "forks": repo.get("forks_count"),
        "watchers": repo.get("watchers_count"),
        "open_issues": repo.get("open_issues_count"),
        "size_kb": repo.get("size"),
        "license": license_info.get("name") if license_info else None,
        "is_fork": repo.get("fork", False),
        "is_archived": repo.get("archived", False),
        "is_template": repo.get("is_template", False),
        "default_branch": repo.get("default_branch"),
        "has_wiki": repo.get("has_wiki"),
        "has_pages": repo.get("has_pages"),
        "homepage": repo.get("homepage"),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
    }


def _fetch_languages(client: GitHubClient, owner: str, repo: str) -> Dict[str, int]:
    """Fetch the per-language byte counts for a repo."""
    data = client.get(f"/repos/{owner}/{repo}/languages")
    if data is None:
        logger.warning("Could not fetch languages for %s/%s.", owner, repo)
        return {}
    logger.debug("Languages for %s: %s", repo, data)
    return data


def _fetch_commit_count(client: GitHubClient, owner: str, repo: str) -> Optional[int]:
    """Estimate total commit count using pagination headers."""
    response = client.get(
        f"/repos/{owner}/{repo}/commits",
        params={"per_page": 1},
        raw=True,
    )
    if response.status_code != 200:
        logger.warning("Could not fetch commit count for %s/%s (status %s).", owner, repo, response.status_code)
        return None

    link_header = response.headers.get("Link", "")
    if 'rel="last"' in link_header:
        match = re.search(r'page=(\d+)>; rel="last"', link_header)
        count = int(match.group(1)) if match else None
    else:
        count = len(response.json())

    logger.debug("Commit count for %s: %s", repo, count)
    return count


def _fetch_contributor_count(client: GitHubClient, owner: str, repo: str) -> Optional[int]:
    """Estimate contributor count using pagination headers."""
    response = client.get(
        f"/repos/{owner}/{repo}/contributors",
        params={"per_page": 1, "anon": "true"},
        raw=True,
    )
    if response.status_code != 200:
        logger.warning("Could not fetch contributors for %s/%s (status %s).", owner, repo, response.status_code)
        return None

    link_header = response.headers.get("Link", "")
    if 'rel="last"' in link_header:
        match = re.search(r'page=(\d+)>; rel="last"', link_header)
        count = int(match.group(1)) if match else None
    else:
        count = len(response.json())

    logger.debug("Contributor count for %s: %s", repo, count)
    return count


def _fetch_readme(client: GitHubClient, owner: str, repo: str) -> Optional[str]:
    """Fetch the repo's README as raw markdown text."""
    data = client.get(f"/repos/{owner}/{repo}/readme")
    if data is None:
        logger.info("No README found for %s/%s.", owner, repo)
        return None

    content = data.get("content")
    encoding = data.get("encoding")
    if content and encoding == "base64":
        try:
            decoded = base64.b64decode(content).decode("utf-8", errors="replace")
            logger.debug("README for %s: %d chars.", repo, len(decoded))
            return decoded
        except Exception as exc:
            logger.error("Failed to decode README for %s/%s: %s", owner, repo, exc)
            return None

    logger.warning("README for %s/%s has unexpected encoding: %s", owner, repo, encoding)
    return None


def _fetch_recent_commits(
    client: GitHubClient, owner: str, repo: str, count: int = 10
) -> List[Dict[str, Any]]:
    """Fetch the most recent commits (default 10)."""
    data = client.get(f"/repos/{owner}/{repo}/commits", params={"per_page": count})
    if not data:
        logger.info("No commits found for %s/%s.", owner, repo)
        return []

    commits = []
    for c in data:
        commit_info = c.get("commit", {})
        author_info = commit_info.get("author", {})
        commits.append({
            "sha": c.get("sha"),
            "message": commit_info.get("message"),
            "author_name": author_info.get("name"),
            "author_email": author_info.get("email"),
            "date": author_info.get("date"),
            "html_url": c.get("html_url"),
        })

    logger.debug("Fetched %d recent commits for %s.", len(commits), repo)
    return commits
