"""
GitHubClient — Thin HTTP wrapper around the GitHub REST API.

Handles:
  - Authentication via personal access token
  - Automatic rate-limit detection, logging, and sleep-until-reset
  - Retries with exponential back-off on transient errors (5xx, timeouts)
  - Full request/response DEBUG logging
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("github_scraper.client")

API_BASE = "https://api.github.com"

# Rate-limit safety margin: warn when fewer than this many requests remain
RATE_LIMIT_WARN_THRESHOLD = 100


class GitHubClient:
    """
    Authenticated GitHub API client with built-in rate-limit awareness.

    Parameters
    ----------
    token : str or None
        GitHub personal access token.  If *None*, requests are
        unauthenticated (60 requests / hour).
    """

    def __init__(self, token: Optional[str] = None):
        self.session = requests.Session()

        # ── Auth header ─────────────────────────────────────────────────
        if token:
            self.session.headers.update({
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            })
            logger.info("GitHubClient created with authenticated token")
        else:
            self.session.headers.update({
                "Accept": "application/vnd.github.v3+json",
            })
            logger.warning(
                "GitHubClient created WITHOUT token — limited to 60 requests/hour"
            )

        # ── Retry strategy for transient errors ─────────────────────────
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self._requests_made = 0

    # ── Core request method ─────────────────────────────────────────────
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        raw: bool = False,
    ) -> Union[Dict, List, requests.Response]:
        """
        Make a GET request to the GitHub API.

        Parameters
        ----------
        endpoint : str
            API path (e.g. ``/users/octocat``) or full URL.
        params : dict, optional
            Query parameters.
        raw : bool
            If *True*, return the raw ``requests.Response`` instead of JSON.

        Returns
        -------
        dict / list / Response
            Parsed JSON or raw response.
        """
        url = endpoint if endpoint.startswith("http") else f"{API_BASE}{endpoint}"
        logger.debug("GET %s  params=%s", url, params)

        response = self.session.get(url, params=params, timeout=30)
        self._requests_made += 1

        # ── Rate-limit handling ─────────────────────────────────────────
        self._check_rate_limit(response)

        logger.debug(
            "Response %s  %s  (%d bytes)",
            response.status_code,
            url,
            len(response.content),
        )

        if raw:
            return response

        if response.status_code == 404:
            logger.warning("404 Not Found: %s", url)
            return None

        if response.status_code != 200:
            logger.error(
                "Unexpected status %s for %s: %s",
                response.status_code,
                url,
                response.text[:300],
            )
            response.raise_for_status()

        return response.json()

    # ── Pagination helper ───────────────────────────────────────────────
    def get_paginated(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        per_page: int = 100,
    ) -> List[Dict]:
        """
        Fetch all pages for a paginated GitHub endpoint.

        Returns
        -------
        list[dict]
            Concatenated results from every page.
        """
        params = dict(params or {})
        params["per_page"] = per_page
        page = 1
        all_items: List[Dict] = []

        while True:
            params["page"] = page
            logger.debug("Paginated request page=%d for %s", page, endpoint)
            response = self.get(endpoint, params=params, raw=True)

            if response.status_code != 200:
                logger.error(
                    "Pagination stopped — status %s at page %d for %s",
                    response.status_code,
                    page,
                    endpoint,
                )
                break

            data = response.json()
            if not data:
                break

            all_items.extend(data)
            logger.debug("Page %d returned %d items (total so far: %d)", page, len(data), len(all_items))

            # Check if there is a next page
            if "next" not in response.links:
                break
            page += 1

        logger.info("Paginated fetch complete: %s → %d items", endpoint, len(all_items))
        return all_items

    # ── Rate-limit internals ────────────────────────────────────────────
    def _check_rate_limit(self, response: requests.Response) -> None:
        """Inspect rate-limit headers and sleep if necessary."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        limit = response.headers.get("X-RateLimit-Limit")
        reset_ts = response.headers.get("X-RateLimit-Reset")

        if remaining is None:
            return

        remaining = int(remaining)
        limit = int(limit) if limit else "?"
        reset_ts = int(reset_ts) if reset_ts else None

        logger.debug("Rate limit: %d / %s remaining", remaining, limit)

        if remaining <= 0 and reset_ts:
            wait = max(reset_ts - int(time.time()), 1)
            logger.warning(
                "Rate limit EXHAUSTED. Sleeping %d seconds until reset…", wait
            )
            time.sleep(wait + 1)

        elif remaining < RATE_LIMIT_WARN_THRESHOLD:
            logger.warning(
                "Rate limit running low: %d / %s remaining", remaining, limit
            )

    @property
    def requests_made(self) -> int:
        """Total number of API requests issued by this client."""
        return self._requests_made
