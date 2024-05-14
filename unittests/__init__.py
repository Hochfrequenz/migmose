"""
This file is here, because this allows for best de-coupling of tests and application/library logic.
Further reading: https://docs.pytest.org/en/6.2.x/goodpractices.html#tests-outside-application-code
"""

from pathlib import Path

path_to_test_edi_energy_mirror_repo = Path(__file__).parent / "test_edi_energy_mirror_repo"
path_to_test_FV2310 = path_to_test_edi_energy_mirror_repo / "edi_energy_de" / "FV2310"
expected_output_dir = Path(__file__).parent / "test_expected_data"
