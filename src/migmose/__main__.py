"""
contains CLI logic for migmose.
"""

from pathlib import Path

import click
from maus.edifact import EdifactFormat

from migmose.mig.nachrichtenstruktur import NachrichtenstrukturTabelle
from migmose.mig.nestednachrichtenstruktur import NestedNachrichtenstruktur
from migmose.parsing import find_file_to_type, parse_raw_nachrichtenstrukturzeile, preliminary_output_as_json


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
    "--message_type",
    type=click.Choice(list(map(lambda x: x.name, EdifactFormat)), case_sensitive=False),
    # Taken from https://github.com/pallets/click/issues/605#issuecomment-889462570
    prompt="Please specify which message type to be parsed.",
    help="Defines the set of message types to be parsed.",
    multiple=True,
)
@click.option(
    "-o",
    "--output_dir",
    type=click.Path(exists=False, dir_okay=True, file_okay=False, path_type=Path),
    prompt="Please enter the path to the directory which should contain the output files.",
    help="Set path to directory which contains the output files. If the directory does not exist, it will be created.",
)
def main(input_dir: Path, output_dir, message_type: list[EdifactFormat]) -> None:
    """
    Main function. Uses CLI input.
    """
    dict_files = find_file_to_type(message_type, input_dir)
    for m_type, file in dict_files.items():
        raw_lines = parse_raw_nachrichtenstrukturzeile(file)
        nachrichtenstrukturtabelle = NachrichtenstrukturTabelle.init_raw_table(raw_lines)
        nested_nachrichtenstruktur, _ = NestedNachrichtenstruktur.structure_table(nachrichtenstrukturtabelle)
        # preliminary_output_as_json(nested_nachrichtenstruktur, m_type, output_dir)
        NestedNachrichtenstruktur.output_as_json(nested_nachrichtenstruktur, m_type, output_dir)


if __name__ == "__main__":
    main()  # pylint:disable=no-value-for-parameter
