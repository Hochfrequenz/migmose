from migmose.mig.nachrichtenstrukturzeile import NachrichtenstrukturZeile


class TestNachrichtenstrukturZeile:
    """
    A class with pytest unit tests.
    """

    def test_something(self):
        my_class = NachrichtenstrukturZeile(zaehler="1")
        assert my_class.zaehler == "1"
