import pytest

from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class TestNachrichtenstrukturZeile:
    """
    A class with pytest unit tests.
    """

    def test_init_nachrichtenstrukturzeile(self):
        my_class2 = NachrichtenstrukturZeile.init_raw_lines(
            "0590	527	RFF	C	D	9	9	3	Referenz auf die ID einer Messlokation"
        )
        assert my_class2.zaehler == "0590"
        my_class3 = NachrichtenstrukturZeile.init_raw_lines("0590	RFF	C	D	9	9	3	Referenz auf die ID einer Messlokation")
        assert my_class3.nr is None

    def test_failed_init_nachrichtenstrukturzeile(self):
        with pytest.raises(ValueError) as excinfo:
            _ = NachrichtenstrukturZeile.init_raw_lines("RFF	C	D	9	9	3	Referenz auf die ID einer Messlokation")
        assert "Expected 8 or 9 fields, got" in str(excinfo.value)
