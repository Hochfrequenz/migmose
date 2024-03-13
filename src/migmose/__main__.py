"""
contains CLI logic for migmose.
"""

from pathlib import Path

import click
from maus.edifact import EdifactFormat

from migmose.mig.nachrichtenstrukturtabelle import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.parsing import find_file_to_format, parse_raw_nachrichtenstrukturzeile


# add CLI logic
@click.command()
@click.option(
    "-i",
    "--input_dir",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, path_type=Path),
    prompt="Please enter the path to the directory containing the .docx files",
    help="Set path to directory which contains the .docx files for the migs",
)
@click.option(
    "-mt",
    "--message_format",
    type=click.Choice(list(map(lambda x: x.name, EdifactFormat)), case_sensitive=False),
    # Taken from https://github.com/pallets/click/issues/605#issuecomment-889462570
    prompt="Please specify which message format to be parsed.",
    help="Defines the set of message formats to be parsed.",
    multiple=True,
)
@click.option(
    "-o",
    "--output_dir",
    type=click.Path(exists=False, dir_okay=True, file_okay=False, path_type=Path),
    prompt="Please enter the path to the directory which should contain the output files.",
    help="Set path to directory which contains the output files. If the directory does not exist, it will be created.",
)
def main(input_dir: Path, output_dir, message_format: list[EdifactFormat]) -> None:
    """
    Main function. Uses CLI input.
    """
    dict_files = find_file_to_format(message_format, input_dir)
    for m_format, file in dict_files.items():
        raw_lines = parse_raw_nachrichtenstrukturzeile(file)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.create_nachrichtenstruktur_tabelle(raw_lines)
        nachrichtenstrukturtabelle.to_csv(m_format, output_dir)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.create_nested_nachrichtenstruktur(
            nachrichtenstrukturtabelle
        )
        nested_nachrichtenstruktur.to_json(m_format, output_dir)


if __name__ == "__main__":
    main()  # pylint:disable=no-value-for-parameter
