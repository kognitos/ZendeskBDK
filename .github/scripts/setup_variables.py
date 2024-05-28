import os
import re
import sys
import toml


def interpolate_values(data: dict) -> dict:
    """
    Loops through the dictionary and stores (in a separate dict) all items whose values have no reference
    to another variable (meaning, no unresolved { ... }s in their value). For each item whose value still
    contains an unresolved reference, it tries to resolve it from the items that have already been fully
    resolved. If after an iteration the amount of (non-zero) unresolved items does not decrease, it means
    there is at least one cyclic dependency.

    Example of propper functioning:
        {
            'VARIABLE_SUFFIX': "DIRECTION",
            'REGION_DIRECTION': "WEST",
            'REGION': "US-{ REGION_{ VARIABLE_SUFFIX } }-2"
        }
        would result in:
        {
            'VARIABLE_SUFFIX': "DIRECTION",
            'REGION_DIRECTION': "WEST",
            'REGION': "US-WEST-2"
        }

    Example of cyclic dependency (this would fail):
        {
            'VAR1': "{ VAR2 }",
            'VAR2': "{ VAR3 }",
            'VAR3': "{ VAR1 }"
        }
    """

    var_name_pattern = r"[-_A-Za-z][-_A-Za-z0-9]*"
    pattern = re.compile(r"({\s*" + var_name_pattern + r"\s*})")

    total_var_count = len(data)
    fully_processed_vars = {}
    while len(fully_processed_vars) < total_var_count:
        remainder_count = len(data)
        _data = data.copy()
        for k, v in _data.items():
            if not re.search("^" + var_name_pattern + "$", k):
                raise KeyError(f"The following key does not comply with naming restrictions: {k}")

            matches = list(pattern.finditer(v))
            for match in matches:
                var_name = match.group()[1:-1].strip()
                if var_name in fully_processed_vars:
                    data[k] = v[:match.start()] + fully_processed_vars[var_name] + v[match.end():]
            if len(list(pattern.finditer(data[k]))) == 0:
                fully_processed_vars[k] = data[k]
                del data[k]

        if len(data) == 0:
            print("All variables processed!")
            break
        elif remainder_count == len(data):
            raise ValueError(f"There is at least one cyclic dependency among the following variables: {data}")

    return fully_processed_vars

def read_file(path: str) -> dict:
    try:
        with open(path, 'r') as file:
            config = {}
            data = toml.load(file)
            for k, v in data['tool']['poetry'].items():
                config[k] = str(v)
            config.update(data['cloud'])
            config.update(data['environment'])
            return config
    except FileNotFoundError:
        print(f"File not found: {path}")


def output(data: dict):
    output_file = os.getenv('GITHUB_OUTPUT')
    with open(output_file, "a") as out:
        for k, v in data.items():
            if not isinstance(k, str):
                raise ValueError("Keys must be strings")
            variable = f"{k}={v}"
            out.write(f"{variable}\n")


output(interpolate_values(read_file(sys.argv[1])))
