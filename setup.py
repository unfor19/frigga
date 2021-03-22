from os import getcwd, path, environ
from setuptools import setup
import subprocess


# Change accordingly ----------------------------
PACKAGE_DIR_NAME = "frigga"
GITHUB_OWNER = "unfor19"
GITHUB_REPOSITORY = "frigga"
# -----------------------------------------------


# Keep the same structure, should NOT be changed
def get_short_commit():
    """Assumes git is installed"""
    return subprocess.check_output(
        ['git', 'rev-parse', '--short', 'HEAD']
    ).decode().strip()


# Keep the same structure, should NOT be changed
with open("version", "r") as fh:
    version = fh.read()

with open(path.join(getcwd(), 'src', PACKAGE_DIR_NAME, '__init__.py'), "w") as fh:  # noqa: E501
    short_commit = ""
    try:
        short_commit = get_short_commit()
    except Exception:
        try:
            if "GITHUB_SHA" in environ and environ["GITHUB_SHA"]:
                short_commit = environ["GITHUB_SHA"]
        except Exception:
            short_commit = "abcd123"
    finally:
        short_commit = short_commit[0:7]

    fh.write(
        f"__version__ = '{version}'\n__short_commit__ = '{short_commit}'"
    )

setup(
    version=version,
    download_url=f'https://github.com/{GITHUB_OWNER}/{GITHUB_REPOSITORY}/archive/{version}.tar.gz',  # noqa: E501
)
# -----------------------------------------------
