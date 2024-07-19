import pytest
from unittest.mock import patch, ANY
import sys
from pathlib import Path

file_path = Path(__file__).resolve()
parent_dir = file_path.parent.parent
sys.path.insert(0, str(parent_dir))

from dl_gh import main as main_function


@pytest.mark.asyncio
@patch("dl_gh.get_latest_release")
@patch("dl_gh.get_package_urls")
@patch("dl_gh.download_package")
@patch("builtins.input", return_value="1")
async def test_file_download(mock_input, mock_download, mock_get_urls, mock_get_latest):
    # Mock the necessary functions
    mock_get_latest.return_value = "v3.4.0"
    mock_get_urls.return_value = [
        "https://github.com/MusicDin/kubitect/releases/download/v3.4.0/kubitect-v3.4.0-darwin-arm64.tar.gz"
    ]
    mock_download.return_value = None

    # Simulate command-line arguments
    test_args = ["-u", "MusicDin", "-r", "kubitect", "-t", "tar.gz"]

    # Call the main function with our test arguments
    await main_function(test_args)

    # Assert that the download function was called with the correct arguments
    expected_file_name = "kubitect-v3.4.0-darwin-arm64.tar.gz"
    expected_path = Path.cwd() / expected_file_name
    mock_download.assert_called_once_with(
        "https://github.com/MusicDin/kubitect/releases/download/v3.4.0/kubitect-v3.4.0-darwin-arm64.tar.gz",
        str(expected_path),
        ANY,  # This is for the session argument, which we don't need to check
    )
