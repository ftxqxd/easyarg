#!/usr/bin/env python3
from easyarg import Command

@Command
def main(file: str, *, out: list[str], uppercase: bool = False) -> None:
    """
    Write the contents of FILE to the file(s) OUT, optionally uppercasing them.
    """
    with open(file) as input_file:
        input_text = input_file.read()
        if uppercase:
            input_text = input_text.upper()

    for output_path in out:
        with open(output_path, 'w') as output_file:
            output_file.write(input_text)

main.run()