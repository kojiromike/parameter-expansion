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

import logging
import os
import sys
from fnmatch import fnmatchcase
from itertools import groupby, takewhile
from shlex import shlex

# Tracing flags: set to True to enable debug trace
TRACE = False
logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


def logger_debug(*args):
    return logger.debug(" ".join(a if isinstance(a, str) else repr(a) for a in args))


def expand(s, env=None, strict=False):
    """Expand the string using POSIX parameter expansion rules.
    Uses the provided environment dict or the actual environment.
    If strict is True, raise a ParameterExpansionNullError on missing
    env variable."""
    if env is None:
        env = dict(os.environ)
    s = expand_simple(s, env)
    return "".join(expand_tokens(s, env, strict))


class ParameterExpansionNullError(LookupError):
    pass


class ParameterExpansionParseError(Exception):
    pass


def expand_tokens(s, env, strict=False):
    tokens = tokenize(s)
    while True:
        try:
            before_dollar = "".join(takewhile(lambda t: t != "$", tokens))
            logger_debug("expand_tokens: before_dollar:", repr(before_dollar))
            yield before_dollar
            sigil = follow_sigil(tokens, env, strict)
            logger_debug("expand_tokens: sigil:", repr(sigil))
            yield sigil
        except StopIteration:
            return


def tokenize(s):
    """Yield token strings lexed from the shell string s."""
    shl = shlex(s, posix=True)
    shl.commenters = ""
    shl.whitespace = ""
    for grouped, group in groupby(shl, key=is_whitespace):
        # we group contiguous whitespaces in one string
        if grouped:
            yield "".join(group)
        else:
            yield from group


def follow_sigil(shl, env, strict=False):
    param = next(shl)
    if param == "{":
        consume = list(takewhile(lambda t: t != "}", shl))
        logger_debug("follow_sigil: consume:", consume)
        consume = iter(consume)
        return follow_brace(consume, env, strict)
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


def is_whitespace(s):
    return all(c in " \t\n" for c in s)


def follow_brace(shl, env, strict=False):
    param = next(shl)
    logger_debug("follow_brace: param:", repr(param))
    if param == "#":
        word = next(shl)

        try:
            subst = env[word]
        except KeyError:
            if strict:
                raise ParameterExpansionNullError(word)
            else:
                subst = ""
        return str(len(subst))

    try:
        subst = env[param]
    except KeyError:
        if strict:
            raise ParameterExpansionNullError(param)
        else:
            subst = ""

    logger_debug("follow_brace: subst:", repr(subst))
    param_unset = param not in env
    param_set_and_not_null = bool(subst and (param in env))
    try:
        modifier = next(shl)
        logger_debug("follow_brace: modifier:", repr(modifier))
        if is_whitespace(modifier):
            pass
        elif modifier == "%":
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
                return word
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
            # this is a string replacement as in replace foo by bar using / as sep
            arg1 = next(shl)
            logger_debug("follow_brace: subst/1: arg1.1:", repr(arg1))
            replace_all = False
            if arg1 == "/":
                # with // replace all occurences
                replace_all = True
                arg1 = next(shl)

            has_sep = False

            # join anything in between the start / and middle /
            for na in shl:
                logger_debug("follow_brace: subst/1: shl/na:", repr(na))
                if na == "/":
                    has_sep = True
                    break
                arg1 += na

            logger_debug(
                "follow_brace: subst/1: arg1.2:", repr(arg1), "has_sep:", has_sep
            )

            arg2 = ""
            if has_sep:
                # Join anything in between the after the middle / until the end.
                # Note: the arg2 replacement value of a replacement may be empty
                for na in shl:
                    arg2 += na

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
                    return word
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
