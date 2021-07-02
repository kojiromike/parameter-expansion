# POSIX Parameter Expansion

![GitHub](https://img.shields.io/github/license/kojiromike/parameter-expansion)
![PyPI](https://img.shields.io/pypi/v/parameter-expansion)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/parameter-expansion)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/parameter-expansion)
[![CodeQL](https://github.com/kojiromike/parameter-expansion/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/kojiromike/parameter-expansion/actions/workflows/codeql-analysis.yml)
[![Tests](https://github.com/kojiromike/parameter-expansion/actions/workflows/test.yml/badge.svg)](https://github.com/kojiromike/parameter-expansion/actions/workflows/test.yml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/parameter-expansion)


This is an experiment to create a Python library to enable
[POSIX parameter expansion][1] from a string.

## Obvious Test Cases

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


[1]: http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html#tag_02_06_02
