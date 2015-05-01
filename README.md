# POSIX Parameter Expansion

This is an experiment to create a Python library to enable
[POSIX parameter expansion][1] from a string.

## Obvious Test Cases

```python
    >>> foo = 'abc/123-def.ghi'
    >>> # Bland Expansion
    >>> pe('abc $foo abc')
    'abc abc/123-def.ghi abc'
    >>> pe('abc${foo}abc')
    'abcabc/123-def.ghiabc'
    >>>
    >>> # Default Value Expansion
    >>> pe('-${foo:-bar}-')
    '-abc/123-def.ghi-'
    >>> pe('-${bar:-bar}-')
    '-bar-'
```

### Default Value Expansion

```python
    >>> foo = 'abc/123-def.ghi'
    >>> pe('abc $foo abc')
    'abc abc/123-def.ghi abc'
    >>> pe('abc${foo}abc')
    'abcabc/123-def.ghiabc'
```


[1]: http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html#tag_02_06_02
