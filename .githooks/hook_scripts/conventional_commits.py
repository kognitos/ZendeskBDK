import re
import sys
import pdb


BRANCHES_TO_CHECK = ['refs/heads/master', 'refs/heads/main']

ERROR_MESSAGE = "The commit message format must be a conventional commit (https://www.conventionalcommits.org/en/v1.0.0/)"

ALLOWED_TYPES = r"(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)"
SCOPE = r"(\([\w\-\.]+\))?"
BREAKING = r"(!)?"
SUBJECT = r"((?:[\w ])+)"
BODY = r"(?:\n+((?:[^#\n]+\n*?)+))??"
COMMENTS = r"(?:\n+((?:#.*\n*?)+))?"

PATTERN = r"^" + ALLOWED_TYPES + SCOPE + BREAKING + ": " + SUBJECT + BODY + COMMENTS + "\n*$"


def parseBreakingChanges(exclamation_mark, commit_subject, commit_body):
        breaking_changes = []
        if exclamation_mark:
            breaking_changes.append(commit_subject)
        if commit_body:
            breaking_changes += re.findall(r"BREAKING CHANGE: (.+)", commit_body)
        return breaking_changes if breaking_changes else None

def stripLineBreaks(content):
    pass

def parseBodyAndFooters(raw_body):
    """
    This is due to a limitation within python's regex engine
    """
    if not raw_body:
        return None, None

    body, footers = None, None
    raw_body = "\n" + raw_body  # Hack to make the regex match when there is no body

    BODY = r"([\s\S]*?\n*)??"

    FOOTER_TITLE = r"[A-Z][a-z]+(?:-[a-z]+)*"
    FOOTER_NAME = r"(?:[A-Za-z]+ )+"
    FOOTER_EMAIL = r"<[\w\-\.]+@(?:[\w\-]+\.)+[\w\-]{2,4}>"
    FOOTER = \
        r"(" + \
            r"(?:\n+?" + \
                FOOTER_TITLE + \
                r": " + \
                FOOTER_NAME + \
                FOOTER_EMAIL + \
            r")*" + \
        r")"
    
    PATTERN = r"^" + BODY + FOOTER + r"$"

    if _match := re.match(PATTERN, raw_body):
        if _match.groups()[0] and _match.groups()[0].strip():
            body = _match.groups()[0].strip()
        
        if _match.groups()[1] and _match.groups()[1].strip():
            footers = []
            _footers = _match.groups()[1].strip().split('\n')
            for _footer in _footers:
                if _footer.strip():
                    footers.append(_footer.strip())
    
    return body, footers

def enforce_conventional_commits(message=None, force_check=False):
    with open("./.git/HEAD") as f:
        branch = f.read().removeprefix("ref: ").strip()

    if not message:
        with open("./.git/COMMIT_EDITMSG") as f:
            message = f.read()

    if branch in BRANCHES_TO_CHECK or force_check:
        if not (_match := re.match(PATTERN, message)):
            raise ValueError(ERROR_MESSAGE)
    else:
        return

    body, footers = parseBodyAndFooters(_match.groups()[4])
    breaking_changes = parseBreakingChanges(_match.groups()[2], _match.groups()[3], body)
    commit_info = {
        "type": _match.groups()[0],
        "scope": _match.groups()[1][1:-1] if _match.groups()[1] else None,
        "isBreaking": bool(breaking_changes),
        "breakingChanges": breaking_changes,
        "subject": _match.groups()[3],
        "body": body,
        "footers": footers,
        "comments": _match.groups()[5]
    }

    return commit_info

if __name__ == "__main__":
    if len(sys.argv) == 2:
        # Manual test: "python conventional_commits.py '<your commit message>'" (MUST USE SINGLE QUOTES)
        try:
            print(enforce_conventional_commits(message=sys.argv[1], force_check=True))
        except ValueError:
            print("INVALID")

def test_conventional_commits():
    import pytest
    assert enforce_conventional_commits(
        message="fix: fixed",
        force_check=True
    ) == {
        'type': 'fix',
        'subject': 'fixed',
        'body': None,
        'breakingChanges': None,
        'comments': None,
        'footers': None,
        'isBreaking': False,
        'scope': None,
    }

    assert enforce_conventional_commits(
        message="feat(KOG-123)!: added an awesome feature",
        force_check=True
    ) == {
        'type': 'feat',
        'subject': 'added an awesome feature',
        'body': None,
        'breakingChanges': ['added an awesome feature'],
        'comments': None,
        'footers': None,
        'isBreaking': True,
        'scope': 'KOG-123',
    }

    assert enforce_conventional_commits(
        message="""ci(KOG-123): added an awesome pipeline


my crazyy commit bodyy
    with random indentations
and more data


Coauthored-by: Bob Dylan <bob@ross.com>


Painted-by: Bob Ross <bob@ross.com>


# Random comment
# Comment 2

""",
        force_check=True
    ) == {
        'type': 'ci',
        'subject': 'added an awesome pipeline',
        'body': 'my crazyy commit bodyy\n    with random indentations\nand more data',
        'breakingChanges': None,
        'comments': '# Random comment\n# Comment 2',
        'footers': ['Coauthored-by: Bob Dylan <bob@ross.com>', 'Painted-by: Bob Ross <bob@ross.com>'],
        'isBreaking': False,
        'scope': 'KOG-123',
    }

    assert enforce_conventional_commits(
        message="""ci(KOG-123): added an awesome pipeline
message body

Coauthored-by: Bob Dylan <bob@ross.com>

Painted-UpperCase: Bob Ross <bob@ross.com>

# Random comment
# Comment 2

""",
        force_check=True
    ) == {
        'type': 'ci',
        'subject': 'added an awesome pipeline',
        'body': 'message body\n\nCoauthored-by: Bob Dylan <bob@ross.com>\n\nPainted-UpperCase: Bob Ross <bob@ross.com>',
        'breakingChanges': None,
        'comments': '# Random comment\n# Comment 2',
        'footers': None,  # Footers must be the last thing before comments
        'isBreaking': False,
        'scope': 'KOG-123',
    }

    assert enforce_conventional_commits(
        message="""ci(KOG-123): added an awesome pipeline
Coauthored-by: Bob Dylan <bob@ross.com>

Painted-UpperCase: Bob Ross <bob@ross.com>
Tested: Mati <matias@kognitos.com>
# Random comment
# Comment 2

""",
        force_check=True
    ) == {
        'type': 'ci',
        'subject': 'added an awesome pipeline',
        'body': 'Coauthored-by: Bob Dylan <bob@ross.com>\n\nPainted-UpperCase: Bob Ross <bob@ross.com>',
        'breakingChanges': None,
        'comments': '# Random comment\n# Comment 2',
        'footers': ['Tested: Mati <matias@kognitos.com>'],
        'isBreaking': False,
        'scope': 'KOG-123',
    }

    assert enforce_conventional_commits(
        message="""ci(KOG-123): added an awesome pipeline
Tested: Mati <matias@kognitos.com>


# Random comment
# Comment 2

""",
        force_check=True
    ) == {
        'type': 'ci',
        'subject': 'added an awesome pipeline',
        'body': None,
        'breakingChanges': None,
        'comments': '# Random comment\n# Comment 2',
        'footers': ['Tested: Mati <matias@kognitos.com>'],
        'isBreaking': False,
        'scope': 'KOG-123',
    }

    assert enforce_conventional_commits(
        message="""ci(KOG-123): added an awesome pipeline

Trailing-space: Mati <matias@kognitos.com> 

# Random comment
# Comment 2

""",
        force_check=True
    ) == {
        'type': 'ci',
        'subject': 'added an awesome pipeline',
        'body': 'Trailing-space: Mati <matias@kognitos.com>',  # It gets stripped but not detected as propper footer
        'breakingChanges': None,
        'comments': '# Random comment\n# Comment 2',
        'footers': None,
        'isBreaking': False,
        'scope': 'KOG-123',
    }

    assert enforce_conventional_commits(
        message="""ci(KOG-123): added an awesome pipeline


        
        
# Random comment
# Comment 2

""",
        force_check=True
    ) == {
        'type': 'ci',
        'subject': 'added an awesome pipeline',
        'body': None,
        'breakingChanges': None,
        'comments': '# Random comment\n# Comment 2',
        'footers': None,
        'isBreaking': False,
        'scope': 'KOG-123',
    }

    assert enforce_conventional_commits(
        message="""ci(KOG-123): added an awesome pipeline
Invalid-email: Mati <matias@kognitos>


""",
        force_check=True
    ) == {
        'type': 'ci',
        'subject': 'added an awesome pipeline',
        'body': 'Invalid-email: Mati <matias@kognitos>',  # Gets detected as body
        'breakingChanges': None,
        'comments': None,
        'footers': None,
        'isBreaking': False,
        'scope': 'KOG-123',
    }

    assert enforce_conventional_commits(
        message="""ci(KOG-123): added an awesome pipeline
invalid-footer: Mati <matias@kognitos.com>
# Random comment
# Comment 2

""",
        force_check=True
    ) == {
        'type': 'ci',
        'subject': 'added an awesome pipeline',
        'body': 'invalid-footer: Mati <matias@kognitos.com>',  # Gets detected as body
        'breakingChanges': None,
        'comments': '# Random comment\n# Comment 2',
        'footers': None,
        'isBreaking': False,
        'scope': 'KOG-123',
    }

    with pytest.raises(ValueError):
        # Comments must be the last thing or there must be no comments at all
        enforce_conventional_commits(
            message="""ci(KOG-123): added an awesome pipeline

my body

# Random comment
# Comment 2

Footer: Mati <mati@mati.com>

""",
            force_check=True
        )

    with pytest.raises(ValueError):
        enforce_conventional_commits(message="fix:must leave a space", force_check=True)

    with pytest.raises(ValueError):
        enforce_conventional_commits(message="FIX: must be lowercase", force_check=True)

    with pytest.raises(ValueError):
        enforce_conventional_commits(message="fix: cant use symbols like '-=:[](){}'", force_check=True)
