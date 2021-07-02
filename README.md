# POSIX Parameter Expansion

![GitHub](https://img.shields.io/github/license/kojiromike/parameter-expansion)
![PyPI](https://img.shields.io/pypi/v/parameter-expansion)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/parameter-expansion)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/parameter-expansion)
![PyPI - Downloads](https://img.shields.io/pypi/dm/parameter-expansion)

[![Tests](https://github.com/kojiromike/parameter-expansion/actions/workflows/test.yml/badge.svg)](https://github.com/kojiromike/parameter-expansion/actions/workflows/test.yml)
[![CodeQL](https://github.com/kojiromike/parameter-expansion/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/kojiromike/parameter-expansion/actions/workflows/codeql-analysis.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)


This is an experimental Python library to enable
[POSIX parameter expansion][1] in a string.
It supports also a subset of [Bash parameter expansion][2].

## Why not spawning a shell directly for this?
One reason is that it may be security risk. Another reason is to
support lightweight analysis or evaluation of shell parameters with
few system dependencies and outside of a running shell.

For instance this use in [scancode-toolkit][3] as part of a lightweight
shell script parser to extract and expand parameters found in some
build scripts.

## Which expansions are supported?
All the standard shell expansions are supported, including some level
of nested expansion, as long as this is not too complex or ambiguous.
In addition, we support Bash substrings and string replacement.
There is an extensive test suite listing [all supported substitions][4]


## How does this work?
The `expand()` function accepts a string and a dictionary of variables
(otherwise it uses the current environmnent variables). The string is
parsed with a custom parser and interpreted to perform the various
expansion procedures using these variables.

### Obvious Test Cases

```python
    >>> from parameter_expansion import expand
    >>> foo = 'abc/123-def.ghi'
    >>> # Bland Expansion
    >>> expand('abc $foo abc')
    'abc abc/123-def.ghi abc'
    >>> expand('abc${foo}abc')
    'abcabc/123-def.ghiabc'
    >>>
    >>> # Default Value Expansion
    >>> expand('-${foo:-bar}-')
    '-abc/123-def.ghi-'
    >>> expand('-${bar:-bar}-')
    '-bar-'
```

### Default Value Expansion

```python
    >>> foo = 'abc/123-def.ghi'
    >>> expand('abc $foo abc')
    'abc abc/123-def.ghi abc'
    >>> expand('abc${foo}abc')
    'abcabc/123-def.ghiabc'
```

[posix-pe]: http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html#tag_02_06_02


## Is any other library doing a similar thing?

- [sayanarijit/expandvars](https://github.com/sayanarijit/expandvars) has similar features yet does not cover all the expansions that this library supports (such as %, # and nested variables).
- [sloria/environs](https://github.com/sloria/environs)


## Contributing

Contributions are welcome. If you would like to add some code, open a pull request. If you need help or are unsure about how to go about contributing, feel free to [open an issue](https://github.com/kojiromike/parameter-expansion/issues/new) or [a discussion](https://github.com/kojiromike/parameter-expansion/discussions/new).


### Pull Requests and Semantic Versioning

This project will try to stick to versions that are compatible with both [PEP 440](https://www.python.org/dev/peps/pep-0440/) and [Semantic Versioning 2.0.0](https://semver.org/) as much as possible. This means...

- ...a *major* version, as in 1.0.2 -> 2.0.0 indicates an incompatible/breaking API change.
- ...a *minor* version, as in 1.3.2 -> 1.4.0 indicates new functionality that maintains backwards compatibility for existing features.
- ...a *patch* version, as in 1.1.2 -> 1.1.3 indicates a bugfix or other improvement with no significant api changes or new features.

Deciding the semantics of a version bump are something best done by humans, and what better place to make that decision than in the pull request itself? Each pull request should have a new version of the project. When a PR is merged, that version information will be used to automatically create a build, release and deploy to pypi.


[1]: https://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html#tag_02_06_02
[2]: https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
[3]: https://github.com/nexB/scancode-toolkit/blob/develop/src/packagedcode/bashparse.py
[4]: https://github.com/kojiromike/parameter-expansion/blob/main/parameter_expansion/tests/test_pe.py
