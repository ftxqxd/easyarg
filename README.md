# easyarg

A simple, easy-to-use argument parsing library for Python based on function annotations.

## Example

```python
from easyarg import Command

@Command
def main(filename, /, *, out: str, uppercase: bool = False):
    """
    Write the input file to the output file, optionally uppercasing it.
    """
    with open(filename) as input_file:
        input_text = input_file.read()
        if uppercase:
            input_text = input_text.upper()
    with open(out, 'w') as output_file:
        output_file.write(input_text)

main.run()
```

This could be invoked as follows:

```sh
$ python3 main.py -- input_file -u --out=output_file
```

## Philosophy

`easyarg` is meant to be simple enough that, 90% of the time, you won't have to read the documentation to use it.
The use case is primarily simple, single-file scripts that you want to throw together as quickly as possible.
