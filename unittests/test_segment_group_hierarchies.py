import json

import pytest
from efoli import EdifactFormat, EdifactFormatVersion
from maus.models.message_implementation_guide import SegmentGroupHierarchy as MausSGH
from maus.models.message_implementation_guide import SegmentGroupHierarchySchema

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.mig.reducednestednachrichtenstruktur import ReducedNestedNachrichtenstruktur
from migmose.mig.segmentgrouphierarchies import SegmentGroupHierarchy
from migmose.parsing import find_file_to_format, parse_raw_nachrichtenstrukturzeile
from unittests import path_to_test_edi_energy_mirror_repo


class TestSegmentGroupHierarchy:
    """test class for create_reduced_nested_nachrichtenstruktur"""

    @pytest.mark.parametrize(
        "message_format",
        [
            pytest.param(EdifactFormat.ORDCHG, id="ORDCHG"),
            pytest.param(EdifactFormat.UTILMDS, id="UTILMDS"),
            pytest.param(EdifactFormat.IFTSTA, id="IFTSTA"),
        ],
    )
    def test_create_create_segmentgroup_hierarchy(self, message_format: EdifactFormat, tmp_path, snapshot):
        """test if the reduced nested nachrichtenstruktur is created correctly"""
        file_path_dict = find_file_to_format(
            [message_format], path_to_test_edi_energy_mirror_repo, EdifactFormatVersion.FV2310
        )
        file_path = file_path_dict[message_format]
        (raw_lines, _) = parse_raw_nachrichtenstrukturzeile(file_path)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
            nachrichtenstrukturtabelle
        )
        reduced_nested_nachrichtenstruktur = ReducedNestedNachrichtenstruktur.create_reduced_nested_nachrichtenstruktur(
            nested_nachrichtenstruktur
        )
        sgh = SegmentGroupHierarchy.create_segmentgroup_hierarchy(reduced_nested_nachrichtenstruktur)
        sgh.to_json(message_format, tmp_path)
        with open(tmp_path / f"{message_format}.sgh.json", "r", encoding="utf-8") as file1:
            actual_sgh_json = json.load(file1)
            assert actual_sgh_json == snapshot
        with open(tmp_path / f"{message_format}.sgh.json", "r", encoding="utf-8") as sgh_file:
            sgh = SegmentGroupHierarchySchema().loads(sgh_file.read())
            assert isinstance(sgh, MausSGH)
