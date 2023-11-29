from translation_god.main import get_abspath_from_relative
import os

def test_get_abspath_from_relative():
    project_abs_path = get_abspath_from_relative("../")
    pardir = os.path.pardir

    assert project_abs_path == pardir
