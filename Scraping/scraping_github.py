"""
scraping_github.py — Entry point for the comprehensive GitHub scraper.

Usage:
    python scraping_github.py                    # scrape default user
    python scraping_github.py <username>         # scrape a specific user
    python scraping_github.py <username> --include-forks --no-code

Environment:
    GITHUB_TOKEN    Personal access token (via .env or shell export)
"""

import argparse
import os
import sys
import time

from dotenv import load_dotenv

load_dotenv()

from github_scraper import (
    GitHubClient,
    download_repo_files,
    save_user_data,
    scrape_profile,
    scrape_repositories,
    setup_logger,
)


def main() -> None:
    # ── CLI arguments ───────────────────────────────────────────────────
    parser = argparse.ArgumentParser(
        description="Scrape a GitHub user's profile, repositories, and source code."
    )
    parser.add_argument(
        "username",
        nargs="?",
        default="khaledhany28",
        help="GitHub username to scrape (default: khaledhany28)",
    )
    parser.add_argument(
        "--include-forks",
        action="store_true",
        help="Include forked repositories (skipped by default)",
    )
    parser.add_argument(
        "--no-code",
        action="store_true",
        help="Skip downloading source code files",
    )
    parser.add_argument(
        "--output-dir",
        default="github_data",
        help="Root output directory (default: github_data)",
    )
    parser.add_argument(
        "--max-file-size",
        type=int,
        default=500,
        help="Max file size to download in KB (default: 500)",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=200,
        help="Max files to download per repo (default: 200)",
    )
    args = parser.parse_args()

    # ── Setup ───────────────────────────────────────────────────────────
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info("GitHub Scraper starting for user: %s", args.username)
    logger.info("=" * 60)

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.warning("No GITHUB_TOKEN found in environment. Using unauthenticated requests.")
    client = GitHubClient(token=token)

    start_time = time.time()

    # ── 1. Scrape profile ───────────────────────────────────────────────
    profile = scrape_profile(client, args.username)
    if profile is None:
        logger.error("Could not fetch profile. Exiting.")
        sys.exit(1)

    # ── 2. Scrape repositories ──────────────────────────────────────────
    repos = scrape_repositories(client, args.username, include_forks=args.include_forks)
    if not repos:
        logger.warning("No repositories found for %s.", args.username)

    # ── 3. Download source code ─────────────────────────────────────────
    repo_files = {}
    if not args.no_code:
        for idx, repo in enumerate(repos, start=1):
            repo_name = repo["name"]
            branch = repo.get("default_branch", "main")
            logger.info(
                "[%d/%d] Downloading code for: %s (branch: %s)",
                idx, len(repos), repo_name, branch,
            )
            files = download_repo_files(
                client,
                args.username,
                repo_name,
                default_branch=branch,
                max_file_size=args.max_file_size * 1024,
                max_files=args.max_files,
            )
            repo_files[repo_name] = files
    else:
        logger.info("Skipping code download (--no-code flag).")

    # ── 4. Save everything to disk ──────────────────────────────────────
    output_path = save_user_data(
        username=args.username,
        profile=profile,
        repos=repos,
        repo_files=repo_files,
        output_dir=args.output_dir,
    )

    # ── Summary ─────────────────────────────────────────────────────────
    elapsed = time.time() - start_time
    total_files = sum(len(f) for f in repo_files.values())
    logger.info("=" * 60)
    logger.info("SCRAPING COMPLETE")
    logger.info("  User:          %s", args.username)
    logger.info("  Repos scraped: %d", len(repos))
    logger.info("  Files saved:   %d", total_files)
    logger.info("  API requests:  %d", client.requests_made)
    logger.info("  Time elapsed:  %.1f seconds", elapsed)
    logger.info("  Output:        %s", output_path)
    logger.info("  Log file:      github_scraper.log")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()