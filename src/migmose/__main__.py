"""
contains CLI logic for migmose.
"""

from pathlib import Path

import click
from loguru import logger
from maus.edifact import EdifactFormat

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.parsing import find_file_to_format, parse_raw_nachrichtenstrukturzeile


# add CLI logic
@click.command()
@click.option(
    "-i",
    "--input-dir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
    prompt="Please enter the path to the directory containing the .docx files",
    help="Set path to directory which contains the .docx files for the migs",
)
@click.option(
    "-mf",
    "--message-format",
    type=click.Choice(list(map(lambda x: x.name, EdifactFormat)), case_sensitive=False),
    # Taken from https://github.com/pallets/click/issues/605#issuecomment-889462570
    default=list(map(lambda x: x.name, EdifactFormat)),
    help="Defines the set of message formats to be parsed.",
    multiple=True,
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
    type=click.Choice(["csv", "nested_json"], case_sensitive=False),
    default=["csv"],
    prompt="Please specify how the output should be formatted.",
    help="Defines the output format. Choose between csv and nested_json. Default is csv.",
    multiple=True,
)
def main(input_dir: Path, output_dir, message_format: list[EdifactFormat], file_type: list[str]) -> None:
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

    dict_files = find_file_to_format(message_format, input_dir)
    for m_format, file in dict_files.items():
        raw_lines = parse_raw_nachrichtenstrukturzeile(file)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        if "csv" in file_type:
            logger.info("💾 Saving flat Nachrichtenstruktur table for {} as csv to {}.", m_format, output_dir)
            nachrichtenstrukturtabelle.to_csv(m_format, output_dir)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
            nachrichtenstrukturtabelle
        )
        if "nested_json" in file_type:
            logger.info("💾 Saving nested Nachrichtenstruktur for {} as json to {}.", m_format, output_dir)
            nested_nachrichtenstruktur.to_json(m_format, output_dir)


if __name__ == "__main__":
    main()  # pylint:disable=no-value-for-parameter
