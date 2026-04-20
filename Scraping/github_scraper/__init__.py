"""
github_scraper — Comprehensive GitHub profile and repository scraper.

Usage:
    from github_scraper import GitHubClient, scrape_profile, scrape_repositories, download_repo_files, save_user_data, setup_logger

    setup_logger()
    client = GitHubClient(token="your_token")
    profile = scrape_profile(client, "username")
    repos = scrape_repositories(client, "username")
    ...
"""

from github_scraper.logger import setup_logger
from github_scraper.client import GitHubClient
from github_scraper.profile_scraper import scrape_profile
from github_scraper.repo_scraper import scrape_repositories
from github_scraper.file_downloader import download_repo_files
from github_scraper.storage import save_user_data

__all__ = [
    "setup_logger",
    "GitHubClient",
    "scrape_profile",
    "scrape_repositories",
    "download_repo_files",
    "save_user_data",
]
