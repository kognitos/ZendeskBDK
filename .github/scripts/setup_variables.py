import os
import sys
import toml


def interpolate_values(data):
    """
    This will only work properly if templates are defined in order
    ie: VAR1 = "{VAR3}"
        VAR2 = "Hello"
        VAR3 = "{VAR2}"
    will produce
        VAR1 -> "{VAR3}"
        VAR2 -> "Hello"
        VAR3 -> "Hello"
    as VAR1 tried to be initialized before VAR3
    """
    for k, v in data.items():
        data[k] = v.format(**data)
    return data


def read_file(path):
    try:
        with open(path, 'r') as file:
            config = {}
            data = toml.load(file)
            for k, v in data['tool']['poetry'].items():
                if isinstance(v, int) or isinstance(v, str) or isinstance(v, float):
                    config[k] = v
            config.update(data['environment'])
            config.update(data['deployment'])
            return config
    except FileNotFoundError:
        print(f"File not found: {path}")


def output(data):
    output_file = os.getenv('GITHUB_OUTPUT')
    with open(output_file, "a") as out:
        for k, v in data.items():
            if not isinstance(k, str):
                raise ValueError("Keys must be strings")
            variable = f"{k}={v}"
            out.write(f"{variable}\n")


output(interpolate_values(read_file(sys.argv[1])))
