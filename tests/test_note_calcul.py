import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sections.helpers.note_calcul import (
    repartition_energie_finale_partie_renovee_somme,
    estimation_ecs_annuel,
    estimation_part_chauffage_periode_sur_annuel,
    
    )


def test_repartition_energie_finale_partie_renovee_somme():
    assert repartition_energie_finale_partie_renovee_somme(70, 30) == 100
    assert repartition_energie_finale_partie_renovee_somme(50, 50) == 100
    assert repartition_energie_finale_partie_renovee_somme(0, 0) == 0

