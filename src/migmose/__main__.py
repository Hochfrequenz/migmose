"""
contains CLI logic for migmose.
"""

from pathlib import Path

import click
from loguru import logger
from maus.edifact import EdifactFormat, EdifactFormatVersion

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.mig.reducednestednachrichtenstruktur import ReducedNestedNachrichtenstruktur
from migmose.parsing import find_file_to_format, parse_raw_nachrichtenstrukturzeile


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
    type=click.Choice(list(map(lambda x: x.name, EdifactFormat)), case_sensitive=False),
    # Taken from https://github.com/pallets/click/issues/605#issuecomment-889462570
    default=list(map(lambda x: x.name, EdifactFormat)),
    help="Defines the set of message formats to be parsed. If no format is specified, all formats are parsed.",
    multiple=True,
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
    type=click.Choice(["csv", "nested_json", "reduced_nested_json"], case_sensitive=False),
    default=["csv", "nested_json", "reduced_nested_json"],
    help="Defines the output format. Choose between csv and nested_json and reduced_nested_json. Default is csv.",
    multiple=True,
)
def main(
    edi_energy_mirror_path: Path,
    output_dir,
    format_version: EdifactFormatVersion | str,
    message_format: list[EdifactFormat],
    file_type: list[str],
) -> None:
    """
    Main function. Uses CLI input.
    """
    if message_format is None:
        message = "❌ No message format specified. Please specify the message format."
        click.secho(message, fg="yellow")
        logger.error(message)
        raise click.Abort()
    if file_type is None:
        message = "❌ No output format specified. Please specify the output format."
        click.secho(message, fg="yellow")
        logger.error(message)
        raise click.Abort()
    if isinstance(format_version, str):
        format_version = EdifactFormatVersion(format_version)

    dict_files = find_file_to_format(message_format, edi_energy_mirror_path, format_version)
    for m_format, file in dict_files.items():
        output_dir_for_format = output_dir / format_version / m_format
        raw_lines = parse_raw_nachrichtenstrukturzeile(file)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        if "csv" in file_type:
            logger.info(
                "💾 Saving flat Nachrichtenstruktur table for {} and {} as csv to {}.",
                m_format,
                format_version,
                output_dir_for_format,
            )
            nachrichtenstrukturtabelle.to_csv(m_format, output_dir_for_format)
        if "nested_json" in file_type:
            nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
                nachrichtenstrukturtabelle
            )
            # Save the nested Nachrichtenstruktur as json
            logger.info(
                "💾 Saving nested Nachrichtenstruktur for {} and {} as json to {}.",
                m_format,
                format_version,
                output_dir_for_format,
            )
            nested_nachrichtenstruktur.to_json(m_format, output_dir_for_format)

        if "reduced_nested_json" in file_type:
            nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
                nachrichtenstrukturtabelle
            )
            reduced_nested_nachrichtenstruktur = (
                ReducedNestedNachrichtenstruktur.create_reduced_nested_nachrichtenstruktur(nested_nachrichtenstruktur)
            )
            # Save the reduced nested Nachrichtenstruktur as json
            logger.info(
                "💾 Saving reduced nested Nachrichtenstruktur for {} and {} as json to {}.",
                m_format,
                format_version,
                output_dir_for_format,
            )
            reduced_nested_nachrichtenstruktur.to_json(m_format, output_dir_for_format)


if __name__ == "__main__":
    main()  # pylint:disable=no-value-for-parameter
