"""
Profile scraper — fetches comprehensive GitHub user profile data.

Collects:
  - All public user fields (name, bio, company, location, email, …)
  - Account statistics (repos, gists, followers, following)
  - Profile README content (from {username}/{username} repo, if it exists)
"""

import base64
import logging
from typing import Any, Dict, Optional

from github_scraper.client import GitHubClient

logger = logging.getLogger("github_scraper.profile")


def scrape_profile(client: GitHubClient, username: str) -> Optional[Dict[str, Any]]:
    """
    Fetch the full public profile for a GitHub user.

    Parameters
    ----------
    client : GitHubClient
        Authenticated API client.
    username : str
        GitHub username to look up.

    Returns
    -------
    dict or None
        Profile data dictionary, or *None* if the user was not found.
    """
    logger.info("Fetching profile for user: %s", username)

    user_data = client.get(f"/users/{username}")
    if user_data is None:
        logger.error("User '%s' not found (404).", username)
        return None

    profile = {
        # ── Identity ────────────────────────────────────────────────────
        "username": user_data.get("login"),
        "name": user_data.get("name"),
        "bio": user_data.get("bio"),
        "company": user_data.get("company"),
        "location": user_data.get("location"),
        "email": user_data.get("email"),
        "blog": user_data.get("blog"),
        "twitter_username": user_data.get("twitter_username"),
        "avatar_url": user_data.get("avatar_url"),
        "html_url": user_data.get("html_url"),
        "hireable": user_data.get("hireable"),
        "type": user_data.get("type"),  # "User" or "Organization"

        # ── Statistics ──────────────────────────────────────────────────
        "public_repos": user_data.get("public_repos"),
        "public_gists": user_data.get("public_gists"),
        "followers": user_data.get("followers"),
        "following": user_data.get("following"),

        # ── Dates ───────────────────────────────────────────────────────
        "created_at": user_data.get("created_at"),
        "updated_at": user_data.get("updated_at"),

        # ── Profile README (populated below) ────────────────────────────
        "profile_readme": None,
    }

    logger.info(
        "Profile fetched — %s (%s) | %d repos, %d followers",
        profile["name"] or profile["username"],
        profile["location"] or "no location",
        profile["public_repos"] or 0,
        profile["followers"] or 0,
    )

    # ── Fetch profile README ────────────────────────────────────────────
    profile["profile_readme"] = _fetch_profile_readme(client, username)

    return profile


def _fetch_profile_readme(client: GitHubClient, username: str) -> Optional[str]:
    """
    Attempt to fetch the special profile README from the `{username}/{username}` repo.

    Returns the raw markdown string or *None* if it doesn't exist.
    """
    logger.debug("Looking for profile README in repo %s/%s", username, username)

    readme_data = client.get(f"/repos/{username}/{username}/readme")
    if readme_data is None:
        logger.info("No profile README found for %s.", username)
        return None

    content = readme_data.get("content")
    encoding = readme_data.get("encoding")

    if content and encoding == "base64":
        try:
            decoded = base64.b64decode(content).decode("utf-8", errors="replace")
            logger.info("Profile README fetched (%d chars).", len(decoded))
            return decoded
        except Exception as exc:
            logger.error("Failed to decode profile README: %s", exc)
            return None

    logger.warning("Profile README found but has unexpected encoding: %s", encoding)
    return None
