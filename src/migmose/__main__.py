"""
contains CLI logic for migmose.
"""

from pathlib import Path

import click
from efoli import EdifactFormat, EdifactFormatVersion
from loguru import logger

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.mig.reducednestednachrichtenstruktur import ReducedNestedNachrichtenstruktur
from migmose.mig.segmentgrouphierarchies import SegmentGroupHierarchy
from migmose.parsing import _extract_document_version, find_file_to_format, parse_raw_nachrichtenstrukturzeile


def check_message_format(ctx, param, value) -> list[EdifactFormat]:  # type: ignore[no-untyped-def] # pylint: disable=unused-argument
    """
    Check if the message format is valid.
    """
    if len(value) == 0:
        value = map(lambda x: x, EdifactFormat)
    return list(value)


# add CLI logic
@click.command()
@click.option(
    "-eemp",
    "--edi-energy-mirror-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True, path_type=Path),
    prompt="Please enter the path to your local edi energy mirror repository.",
    help="The root path to the edi_energy_mirror repository.",
    required=True,
)
@click.option(
    "-mf",
    "--message-format",
    type=click.Choice(list(map(lambda x: x, EdifactFormat)), case_sensitive=False),
    # Taken from https://github.com/pallets/click/issues/605#issuecomment-889462570
    help="Defines the set of message formats to be parsed. If no format is specified, all formats are parsed.",
    multiple=True,
    callback=check_message_format,
)
@click.option(
    "-fv",
    "--format-version",
    multiple=False,
    type=click.Choice([e.value for e in EdifactFormatVersion], case_sensitive=False),
    default=EdifactFormatVersion.FV2404,
    required=True,
    help="Format version of the MIG documents, e.g. FV2310",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(exists=False, dir_okay=True, file_okay=False, path_type=Path),
    prompt="Please enter the path to the directory which should contain the output files.",
    help="Set path to directory which contains the output files. If the directory does not exist, it will be created.",
)
@click.option(
    "-ft",
    "--file-type",
    type=click.Choice(["csv", "nested_json", "reduced_nested_json", "tree"], case_sensitive=False),
    default=["csv", "nested_json", "reduced_nested_json", "tree"],
    help="Defines the output format. Choose between csv and nested_json and reduced_nested_json. Default is csv.",
    multiple=True,
)
def main(
    edi_energy_mirror_path: Path,
    output_dir: Path,
    format_version: EdifactFormatVersion | str,
    message_format: list[EdifactFormat],
    file_type: tuple[str],
) -> None:
    """
    Main function. Uses CLI input.
    """
    if isinstance(format_version, str):
        format_version = EdifactFormatVersion(format_version)
    if int(str(format_version)[-4:]) >= 2310 and EdifactFormat.UTILMD in message_format:
        logger.warning(
            "💡 UTILMD is not available for format versions 2310 and above. Parse UTILMDS and UTILMDG instead."
        )
        message_format.remove(EdifactFormat.UTILMD)
        message_format.extend([EdifactFormat.UTILMDG, EdifactFormat.UTILMDS, EdifactFormat.UTILMDW])
    message_format = list(set(message_format))
    dict_files = find_file_to_format(message_format, edi_energy_mirror_path, format_version)
    for m_format, file in dict_files.items():
        output_dir_for_format = output_dir / format_version / m_format
        raw_lines = parse_raw_nachrichtenstrukturzeile(file)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
            nachrichtenstrukturtabelle
        )
        reduced_nested_nachrichtenstruktur = ReducedNestedNachrichtenstruktur.create_reduced_nested_nachrichtenstruktur(
            nested_nachrichtenstruktur
        )
        if "csv" in file_type:
            logger.info(
                "💾 Saving flat Nachrichtenstruktur table for {} and {} as csv to {}.",
                m_format,
                format_version,
                output_dir_for_format,
            )
            nachrichtenstrukturtabelle.to_csv(m_format, output_dir_for_format)
        if "nested_json" in file_type:
            # Save the nested Nachrichtenstruktur as json
            logger.info(
                "💾 Saving nested Nachrichtenstruktur for {} and {} as json to {}.",
                m_format,
                format_version,
                output_dir_for_format,
            )
            nested_nachrichtenstruktur.to_json(m_format, output_dir_for_format)

        if "reduced_nested_json" in file_type:
            # Save the reduced nested Nachrichtenstruktur as json
            logger.info(
                "💾 Saving reduced nested Nachrichtenstruktur for {} and {} as json to {}.",
                m_format,
                format_version,
                output_dir_for_format,
            )
            reduced_nested_nachrichtenstruktur.to_json(m_format, output_dir_for_format)
        if "sgh_json" in file_type:
            sgh = SegmentGroupHierarchy.create_segmentgroup_hierarchy(reduced_nested_nachrichtenstruktur)
            # Save the reduced nested Nachrichtenstruktur as json
            logger.info(
                "💾 Saving reduced nested Nachrichtenstruktur for {} and {} as json to {}.",
                m_format,
                format_version,
                output_dir_for_format,
            )
            sgh.to_json(m_format, output_dir_for_format)
        if "tree" in file_type:
            # Save the reduced nested Nachrichtenstruktur as json
            logger.info(
                "💾 Saving tree for {} and {} as json to {}.",
                m_format,
                format_version,
                output_dir_for_format,
            )
            document_version, *_ = _extract_document_version(file)
            reduced_nested_nachrichtenstruktur.output_tree(m_format, output_dir_for_format, document_version)


if __name__ == "__main__":
    main()  # pylint:disable=no-value-for-parameter
