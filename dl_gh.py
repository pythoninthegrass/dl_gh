#!/usr/bin/env python

try:
    import aiohttp
    import asyncio
except ImportError as e:
    lib = str(e).split()[-1].strip("'")
    print(f"Error: '{lib}' module not found. Please install via 'python -m pip install {lib}'")
    exit(1)

import argparse
import os
import platform
import re
from typing import List


async def fetch(url: str, session: aiohttp.ClientSession) -> str:
    async with session.get(url) as response:
        return await response.text()


async def get_latest_release(base_url: str, session: aiohttp.ClientSession) -> str:
    releases_page = await fetch(f"{base_url}/releases", session)
    match = re.search(r'/releases/tag/([^"]+)', releases_page)
    return match.group(1) if match else None


async def get_package_urls(
    user_name: str,
    repo_name: str,
    pkg_type: str,
    latest: str,
    session: aiohttp.ClientSession,
) -> List[str]:
    api_url = f"https://api.github.com/repos/{user_name}/{repo_name}/releases/latest"
    async with session.get(api_url) as response:
        data = await response.json()

    urls = [asset["browser_download_url"] for asset in data.get("assets", [])]
    return [url for url in urls if pkg_type in url and latest in url]


def filter_packages(pkg_urls: List[str], distro: str, arch: str) -> List[str]:
    exclusions = ["md5"]
    filtered_urls = [
        url for url in pkg_urls if not any(exc in url for exc in exclusions)
    ]

    distro_arch_pattern = f"{distro}.*{arch}"
    matching_urls = [
        url
        for url in filtered_urls
        if re.search(distro_arch_pattern, url, re.IGNORECASE)
    ]

    return matching_urls if matching_urls else filtered_urls


async def download_package(
    url: str, output_path: str, session: aiohttp.ClientSession
) -> None:
    async with session.get(url) as response:
        with open(output_path, "wb") as f:
            while True:
                chunk = await response.content.read(8192)
                if not chunk:
                    break
                f.write(chunk)


async def main(argv=None):
    parser = argparse.ArgumentParser(description="Download GitHub release packages")
    parser.add_argument("-u", "--user", required=True, help="GitHub user name")
    parser.add_argument("-r", "--repo", required=True, help="GitHub repo name")
    parser.add_argument(
        "-t", "--type", required=True, help="Package type (e.g., tar.gz)"
    )
    args = parser.parse_args(argv)

    base_url = f"https://github.com/{args.user}/{args.repo}"
    pkg_path = os.getcwd()
    distro = "darwin" if platform.system() == "Darwin" else "linux"
    arch = platform.machine().lower()

    if arch == "x86_64":
        arch = "amd64"
    elif arch == "aarch64":
        arch = "arm64"

    async with aiohttp.ClientSession() as session:
        latest = await get_latest_release(base_url, session)
        if not latest:
            print("Failed to get latest release version")
            return

        pkg_urls = await get_package_urls(
            args.user, args.repo, args.type, latest, session
        )
        if not pkg_urls:
            print(f"No packages found for {args.type}")
            return

        filtered_urls = filter_packages(pkg_urls, distro, arch)

        if len(filtered_urls) > 1:
            print("Available packages:")
            for i, url in enumerate(filtered_urls, 1):
                print(f"{i}: {url}")
            pkg_num = int(input("Enter package number: ")) - 1
            pkg_url = filtered_urls[pkg_num]
        elif filtered_urls:
            pkg_url = filtered_urls[0]
        else:
            print(f"No packages found for {distro}/{arch}")
            return

        pkg_name = pkg_url.split("/")[-1]
        output = os.path.join(pkg_path, pkg_name)
        await download_package(pkg_url, output, session)
        print(f"{pkg_name} downloaded to {pkg_path}")


# TODO: fix two sigints needed to exit
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDownload cancelled. Exiting...")
        exit(0)
