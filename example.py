#!/usr/bin/env python3
from easyarg import Command

@Command
def main(filename: str, *, out: list[str], uppercase: bool = False) -> None:
    """
    Write the input file to the output file, optionally uppercasing it.
    """
    with open(filename) as input_file:
        input_text = input_file.read()
        if uppercase:
            input_text = input_text.upper()

    for output_path in out:
        with open(output_path, 'w') as output_file:
            output_file.write(input_text)

main.run()
