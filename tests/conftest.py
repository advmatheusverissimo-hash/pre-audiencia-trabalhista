import copy
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from engine.regras import carregar_regras  # noqa: E402


@pytest.fixture(scope="session")
def regras():
    return carregar_regras()


@pytest.fixture
def caso_bruto():
    with open(RAIZ / "tests" / "fixtures" / "caso_ficticio.json", encoding="utf-8") as f:
        return copy.deepcopy(json.load(f))
