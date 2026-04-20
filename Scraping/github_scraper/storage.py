"""
Storage module — saves scraped data to an organized folder structure.

Output layout::

    {output_dir}/{username}/
    ├── profile.json              # Full profile info
    ├── repositories_summary.json # All repos metadata
    └── repos/
        ├── repo-name-1/
        │   ├── metadata.json     # Repo metadata + languages + commits
        │   ├── README.md         # Repo README (if it exists)
        │   └── source/           # Mirror of repo file tree
        │       ├── src/
        │       │   └── main.py
        │       └── requirements.txt
        └── ...
"""

import json
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger("github_scraper.storage")


def save_user_data(
    username: str,
    profile: Dict[str, Any],
    repos: List[Dict[str, Any]],
    repo_files: Dict[str, List[Dict[str, Any]]],
    output_dir: str = "github_data",
) -> str:
    """
    Save all scraped data to disk in an organized folder structure.

    Parameters
    ----------
    username : str
        GitHub username (used as the top-level folder name).
    profile : dict
        Profile data from ``scrape_profile``.
    repos : list[dict]
        Repository data from ``scrape_repositories``.
    repo_files : dict[str, list[dict]]
        Mapping of repo name → list of file dicts from ``download_repo_files``.
    output_dir : str
        Root output directory (default ``github_data``).

    Returns
    -------
    str
        Path to the created user directory.
    """
    user_dir = os.path.join(output_dir, username)
    repos_dir = os.path.join(user_dir, "repos")
    os.makedirs(repos_dir, exist_ok=True)
    logger.info("Saving data to: %s", os.path.abspath(user_dir))

    # ── 1. Save profile ─────────────────────────────────────────────────
    _save_json(os.path.join(user_dir, "profile.json"), profile)
    logger.info("Saved profile.json")

    # ── 2. Build and save aggregate language breakdown ───────────────────
    language_totals: Dict[str, int] = {}
    for repo in repos:
        for lang, byte_count in repo.get("languages", {}).items():
            language_totals[lang] = language_totals.get(lang, 0) + byte_count

    # Attach to profile file as well
    profile_with_langs = {**profile, "language_breakdown": language_totals}
    _save_json(os.path.join(user_dir, "profile.json"), profile_with_langs)

    # ── 3. Save repositories summary ────────────────────────────────────
    # Strip large fields (readme, recent_commits) for the summary file
    summary_repos = []
    for repo in repos:
        summary = {k: v for k, v in repo.items() if k not in ("readme_content", "recent_commits")}
        summary_repos.append(summary)
    _save_json(os.path.join(user_dir, "repositories_summary.json"), summary_repos)
    logger.info("Saved repositories_summary.json (%d repos)", len(summary_repos))

    # ── 4. Save per-repo data ───────────────────────────────────────────
    for repo in repos:
        repo_name = repo.get("name", "unknown")
        repo_dir = os.path.join(repos_dir, repo_name)
        os.makedirs(repo_dir, exist_ok=True)

        # metadata.json (everything except raw code)
        _save_json(os.path.join(repo_dir, "metadata.json"), repo)
        logger.debug("Saved metadata.json for %s", repo_name)

        # README.md
        readme_content = repo.get("readme_content")
        if readme_content:
            readme_path = os.path.join(repo_dir, "README.md")
            _save_text(readme_path, readme_content)
            logger.debug("Saved README.md for %s", repo_name)
        else:
            logger.debug("No README to save for %s", repo_name)

        # Source files
        files = repo_files.get(repo_name, [])
        if files:
            source_dir = os.path.join(repo_dir, "source")
            _save_source_files(source_dir, files)
            logger.info("Saved %d source files for %s", len(files), repo_name)
        else:
            logger.debug("No source files to save for %s", repo_name)

    logger.info(
        "All data saved successfully to %s (%d repos, %d total files).",
        os.path.abspath(user_dir),
        len(repos),
        sum(len(f) for f in repo_files.values()),
    )
    return os.path.abspath(user_dir)


# ═══════════════════════════════════════════════════════════════════════════
#  Private helpers
# ═══════════════════════════════════════════════════════════════════════════


def _save_json(path: str, data: Any) -> None:
    """Write data as pretty-printed JSON."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    except Exception as exc:
        logger.error("Failed to write JSON to %s: %s", path, exc)


def _save_text(path: str, text: str) -> None:
    """Write plain text to a file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as exc:
        logger.error("Failed to write text to %s: %s", path, exc)


def _save_source_files(source_dir: str, files: List[Dict[str, Any]]) -> None:
    """
    Save downloaded source files, preserving directory structure.

    Each file dict has keys: ``path``, ``size``, ``content``.
    """
    for file_info in files:
        rel_path = file_info["path"]
        content = file_info["content"]
        full_path = os.path.join(source_dir, rel_path)

        # Create parent directories
        parent = os.path.dirname(full_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as exc:
            logger.error("Failed to save source file %s: %s", rel_path, exc)
