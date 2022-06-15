from pathlib import Path
import pytest


@pytest.fixture
def rootdir() -> Path:
    path = Path(__file__)
    return path.parent

@pytest.fixture
def datadir(rootdir) -> Path:
    return rootdir / "data"
