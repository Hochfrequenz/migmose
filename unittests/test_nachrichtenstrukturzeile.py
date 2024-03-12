import pytest

from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class TestNachrichtenstrukturZeile:
    """
    A class with pytest unit tests for NachrichtenstrukturZeile.
    """

    def test_init_nachrichtenstrukturzeile(self):
        nachrichtenstruktur_zeile = NachrichtenstrukturZeile.init_raw_lines(
            "\t0590\t527\tRFF\tC\tD\t9\t9\t3\tReferenz auf die ID einer Messlokation"
        )
        assert nachrichtenstruktur_zeile.zaehler == "0590"
        nachrichtenstruktur_zeile = NachrichtenstrukturZeile.init_raw_lines(
            "\t0590\tRFF\tC\tD\t9\t9\t3\tReferenz auf die ID einer Messlokation"
        )
        assert nachrichtenstruktur_zeile.nr is None

    def test_failed_init_nachrichtenstrukturzeile(self):
        with pytest.raises(ValueError) as excinfo:
            _ = NachrichtenstrukturZeile.init_raw_lines("\tRFF\tC\tD\t9\t9\t3\tReferenz auf die ID einer Messlokation")
        assert "Expected 8 or 9 fields, got" in str(excinfo.value)
