import subprocess


def run_cmd(cmd):
    subprocess.run(cmd, shell=True, check=True)

def run_tests():
    # generate coverage report
    run_cmd("poetry run pytest -vv --junit-xml=test-results.xml")

def run_record():
    # generate coverage report
    run_cmd("poetry run pytest --record-mode=rewrite")

def run_format():
    # format all files in-place
    run_cmd("poetry run black src tests")
    # organize imports
    run_cmd("poetry run isort src tests")

def run_lint():
    # lint source and test files
    run_cmd("poetry run pylint --output-format=colorized src tests")

def run_type_check():
    # type check source
    run_cmd("poetry run pyright")
