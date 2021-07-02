#!/usr/bin/env python

"""
Given a string, expand that string using POSIX [parameter expansion][1].

Also support some minimal Bash extensions to expansion [3]:
- pattern substitution with `${foo/bar/baz}` (but only plain strings and not patterns)
- substring expansion with `${foo:4:2}


## Limitations

(Pull requests to remove limitations are welcome.)

- Only simple nested expansions of the forms $variable and ${variable} are
supported and not complex expansions such as in `${foo:-${bar:-$baz}}`
- Only ASCII alphanumeric characters and underscores are supported in parameter
names. (Per POSIX, parameter names may not begin with a numeral.)
- Assignment expansions do not mutate the real environment.
- For simplicity's sake, this implementation uses fnmatch instead of
completely reimplementing [POSIX pattern matching][2]
- Comments in strings are unsupported.

[1]: http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html#tag_02_06_02
[2]: http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html#tag_02_13
[3]: https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
"""

import os
from fnmatch import fnmatchcase
from itertools import takewhile
from shlex import shlex


def expand(s, env=None):
    """Expand the string using POSIX parameter expansion rules.
    Uses the provided environment dict or the actual environment."""
    if env is None:
        env = dict(os.environ)
    s = expand_simple(s, env)
    return "".join(expand_tokens(s, env))


class ParameterExpansionNullError(LookupError):
    pass


class ParameterExpansionParseError(Exception):
    pass


def expand_tokens(s, env):
    shl = shlex(s, posix=True)
    shl.commenters = ""
    while True:
        try:
            yield "".join(takewhile(lambda t: t != "$", shl))
            yield follow_sigil(shl, env)
        except StopIteration:
            return


def follow_sigil(shl, env):
    param = next(shl)
    if param == "{":
        consume = iter(list(takewhile(lambda t: t != "}", shl)))
        return follow_brace(consume, env)
    return env.get(param, "")


def expand_simple(s, env):
    """Expand a string containing shell variable substitutions.
    This expands the forms $variable and ${variable} only.
    Non-existent variables are left unchanged.
    Uses the provided environment dict.
    Similar to ``os.path.expandvars``.
    """
    for name, value in env.items():
        s = s.replace(f"${name}", value)
        name = "{" + name + "}"
        s = s.replace(f"${name}", value)
    return s


def remove_affix(subst, shl, suffix=True):
    """
    http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html#tag_02_13
    """
    max = False
    pat = "".join(shl)
    if pat[0] == ("%" if suffix else "#"):
        max = True
        pat = pat[1:]
    size = len(subst)
    indices = range(0, size)
    if max != suffix:
        indices = reversed(indices)
    if suffix:
        for i in indices:
            if fnmatchcase(subst[i:], pat):
                return subst[:i]
        return subst
    else:
        for i in indices:
            if fnmatchcase(subst[:i], pat):
                return subst[i:]
        return subst


def remove_suffix(subst, shl):
    return remove_affix(subst, shl, True)


def remove_prefix(subst, shl):
    return remove_affix(subst, shl, False)


def follow_brace(shl, env):
    param = next(shl)
    if param == "#":
        word = next(shl)
        subst = env.get(word, "")
        return str(len(subst))
    subst = env.get(param, "")
    param_set_and_not_null = bool(subst and (param in env))
    param_unset = param not in env
    try:
        modifier = next(shl)
        if modifier == "%":
            return remove_suffix(subst, shl)
        elif modifier == "#":
            return remove_prefix(subst, shl)
        elif modifier == ":":
            modifier = next(shl)
            if modifier == "-":
                word = next(shl)
                if param_set_and_not_null:
                    return subst
                return word
            elif modifier == "=":
                word = next(shl)
                if param_set_and_not_null:
                    return subst
                env[param] = word
                return env[param]
            elif modifier == "?":
                if param_set_and_not_null:
                    return subst
                raise ParameterExpansionNullError(shl)
            elif modifier == "+":
                if param_set_and_not_null:
                    return next(shl)
                return subst  # ""
            elif modifier.isdigit():
                # this is a Substring Expansion as in ${foo:4:2}
                # This is a bash'ism, and not POSIX.
                # see https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
                try:
                    start = int(modifier)
                except ValueError as e:
                    raise ParameterExpansionParseError("Not a bash slice", shl) from e
                if param_set_and_not_null:
                    subst = subst[start:]
                # if this fails, we will StopIteration and we have a plain ${foo:4}
                # and subst above will be returned
                modifier = next(shl)
                if modifier != ":":
                    raise ParameterExpansionParseError("Illegal slice argument", shl)
                end = int(next(shl))
                if param_set_and_not_null:
                    return subst[:end]
                return subst
            else:
                raise ParameterExpansionParseError()
        elif modifier == "/":
            # this is a string replacement
            arg1 = next(shl)
            replace_all = False
            if arg1 == "/":
                # with // replace all occurences
                replace_all = True
                arg1 = next(shl)

            # the repl of a replacement may not exist at all with no trailing
            # slash or it may be empty
            sep = next(shl, "/")
            if sep != "/":
                raise ParameterExpansionParseError("Illegal replacement syntax")

            # the repl of a replacement may be empty
            try:
                arg2 = next(shl)
            except StopIteration:
                arg2 = ""

            if param_set_and_not_null:
                if replace_all:
                    return subst.replace(arg1, arg2)
                else:
                    return subst.replace(arg1, arg2, 1)

            return subst
        else:
            if modifier == "-":
                word = next(shl)
                if param_unset:
                    return word
                return subst  # may be ""
            elif modifier == "=":
                word = next(shl)
                if param_unset:
                    env[param] = word
                    return env[param]
                return subst  # may be ""
            elif modifier == "?":
                if param_unset:
                    msg = "".join(shl) or "parameter '$parameter' not found"
                    raise ParameterExpansionNullError(msg)
                return subst  # may be ""
            elif modifier == "+":
                word = next(shl)
                if param_unset:
                    return subst  # ""
                return word
            raise ParameterExpansionParseError()
    except StopIteration:
        return subst
