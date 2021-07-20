from collections import namedtuple

import pytest  # type: ignore

import parameter_expansion as pex
import parameter_expansion.pe

#
# This tuple describes a test case where we test the expansion of a
# "tested_shell" strings with the "env" mapping of environment variables and
# ensure that expanded results are equal to the "expected_str" string.
Case = namedtuple("Case", ["tested_shell", "expected_str", "env"])

#
# tests POSIX expansion
subst_test_cases = [
    Case(
        tested_shell="-$parameter-",
        expected_str="-set-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
    ),
    Case(
        tested_shell="-$parameter-",
        expected_str="--",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
    ),
    Case(
        tested_shell="-$parameter-",
        expected_str="-$parameter-",
        env={
            "word": "word",
        },  # unset
    ),
    Case(
        tested_shell="-${parameter}-",
        expected_str="-set-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
    ),
    Case(
        tested_shell="-${parameter}-",
        expected_str="--",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
    ),
    Case(
        tested_shell="-${parameter}-",
        expected_str="--",
        env={
            "word": "word",
        },  # unset
    ),
    Case(
        tested_shell="-${parameter:-word}-",
        expected_str="-set-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
    ),
    Case(
        tested_shell="-${parameter:-word}-",
        expected_str="-word-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
    ),
    Case(
        tested_shell="-${parameter:-word}-",
        expected_str="-word-",
        env={
            "word": "word",
        },  # unset
    ),
    Case(
        tested_shell="-${parameter-word}-",
        expected_str="-set-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
    ),
    Case(
        tested_shell="-${parameter-word}-",
        expected_str="--",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
    ),
    Case(
        tested_shell="-${parameter-word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="-word-",
    ),
    Case(
        tested_shell="-${parameter:=word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-set-",
    ),
    Case(
        tested_shell="-${parameter:=word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="-word-",
    ),
    Case(
        tested_shell="-${parameter:=word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="-word-",
    ),
    Case(
        tested_shell="-${parameter=word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-set-",
    ),
    Case(
        tested_shell="-${parameter=word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="--",
    ),
    Case(
        tested_shell="-${parameter=word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="-word-",
    ),
    Case(
        tested_shell="-${parameter:?word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-set-",
    ),
    Case(
        tested_shell="-${parameter:?word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="error",
    ),
    Case(
        tested_shell="-${parameter:?word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="error",
    ),
    Case(
        tested_shell="-${parameter?word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-set-",
    ),
    Case(
        tested_shell="-${parameter?word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="--",
    ),
    Case(
        tested_shell="-${parameter?word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="error",
    ),
    Case(
        tested_shell="-${parameter:+word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-word-",
    ),
    Case(
        tested_shell="-${parameter:+word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="--",
    ),
    Case(
        tested_shell="-${parameter:+word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="--",
    ),
    Case(
        tested_shell="- ${parameter:+word} -",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="- word -",
    ),
    Case(
        tested_shell="- ${parameter:+word} -",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="-  -",
    ),
    Case(
        tested_shell="- ${parameter:+word} -",
        env={
            "word": "word",
        },  # unset
        expected_str="-  -",
    ),
    Case(
        tested_shell="-${parameter+word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-word-",
    ),
    Case(
        tested_shell="-${parameter+word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="-word-",
    ),
    Case(
        tested_shell="-${parameter+word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="--",
    ),
    Case(
        tested_shell="-${#parameter}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-3-",
    ),
    Case(
        tested_shell="-${#parameter}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="-0-",
    ),
    Case(
        tested_shell="-${#parameter}-",
        env={
            "word": "word",
        },  # unset
        expected_str="-0-",
    ),
]

affix_test_cases = [
    Case(
        tested_shell="-${parameter%/*}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-aa/bb-",
    ),
    Case(
        tested_shell="-${parameter%%/*}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-aa-",
    ),
    Case(
        tested_shell="-${parameter#*/}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-bb/cc-",
    ),
    Case(
        tested_shell="-${parameter##*/}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-cc-",
    ),
]

# test Bash substrings
substring_test_cases = [
    Case(
        tested_shell="-${parameter:0:2}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-aa-",
    ),
    Case(
        tested_shell="-${parameter:3:2}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-bb-",
    ),
    Case(
        tested_shell="- ${parameter:3:2} -",
        env={"parameter": "aa/bb/cc"},
        expected_str="- bb -",
    ),
    Case(
        tested_shell="-${parameter:6}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-cc-",
    ),
]

# test Bash string replacement
replace_test_cases = [
    Case(
        tested_shell="-${parameter/aa/bb}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-bb/bb/cc-",
    ),
    Case(
        tested_shell="-${parameter/aa}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-/bb/cc-",
    ),
    Case(
        tested_shell="-${parameter/ aa / - zz }-",
        env={"parameter": "bb/ aa /cc"},
        expected_str="-bb/ - zz /cc-",
    ),
    Case(
        tested_shell="-${parameter/aa/}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-/bb/cc-",
    ),
    Case(
        tested_shell="-${parameter/aa/zz}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="-zz/bb/aa-",
    ),
    Case(
        tested_shell="- ${parameter/aa/zz} -",
        env={"parameter": "aa/bb/aa"},
        expected_str="- zz/bb/aa -",
    ),
    Case(
        tested_shell="-${parameter//aa/zz}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="-zz/bb/zz-",
    ),
    Case(
        tested_shell="-${parameter//aa}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="-/bb/-",
    ),
    Case(
        tested_shell="-${parameter//aa/ zz}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="- zz/bb/ zz-",
    ),
    Case(
        tested_shell="-${parameter/aa}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="-/bb/aa-",
    ),
    Case(
        tested_shell="-${parameter//aa}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="-/bb/-",
    ),
]

# test expansion of nested plain parameters without expressions
simple_test_cases = [
    Case(
        tested_shell="-${parameter/$aa/$bb}-",
        env=dict(
            parameter="FOO/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="-BAR/bb/cc-",
    ),
    Case(
        tested_shell="- ${parameter/$aa/$bb} -",
        env=dict(
            parameter="FOO/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="- BAR/bb/cc -",
    ),
    Case(
        tested_shell="-$parameter/$aa/$bb-",
        env=dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="-aa/bb/cc/FOO/BAR-",
    ),
    Case(
        tested_shell="-${parameter/${aa}/${bb}}-",
        env=dict(
            parameter="FOO/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="-BAR/bb/cc-",
    ),
    Case(
        tested_shell="-$parameter/$aa/${bb}-",
        expected_str="-aa/bb/cc/FOO/BAR-",
        env=dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
    ),
    Case(
        tested_shell="- $parameter/$aa/${bb} -",
        env=dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="- aa/bb/cc/FOO/BAR -",
    ),
]

# test expansion of plain parameters without expressions
simple_simple_test_cases = [
    Case(
        tested_shell="-$parameter/$aa/$bb-",
        env=dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="-aa/bb/cc/FOO/BAR-",
    ),
    Case(
        tested_shell="-$parameter/$aa/${bb}-",
        env=dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="-aa/bb/cc/FOO/BAR-",
    ),
    Case(
        tested_shell="- $parameter/$aa/${bb} -",
        expected_str="- aa/bb/cc/FOO/BAR -",
        env=dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
    ),
]


@pytest.mark.parametrize("test", subst_test_cases)
def test_expand(test):
    try:
        result = pex.expand(test.tested_shell, env=test.env)
        assert result == test.expected_str
    except pex.ParameterExpansionNullError:
        assert test.expected_str == "error"


@pytest.mark.parametrize("test", affix_test_cases)
def test_affix(test):
    assert pex.expand(test.tested_shell, env=test.env) == test.expected_str


@pytest.mark.parametrize("test", substring_test_cases)
def test_substring(test):
    assert pex.expand(test.tested_shell, env=test.env) == test.expected_str


@pytest.mark.parametrize("test", replace_test_cases)
def test_replace(test):
    assert pex.expand(test.tested_shell, env=test.env) == test.expected_str


@pytest.mark.parametrize("test", simple_test_cases)
def test_simple(test):
    assert pex.expand(test.tested_shell, env=test.env) == test.expected_str


@pytest.mark.parametrize("test", simple_simple_test_cases)
def test_expand_simple(test):
    assert pex.expand(test.tested_shell, env=test.env) == test.expected_str


def test_expand_strict_raises_Exception():
    string = "- $parameter/$aa/${bb}"
    env = dict(foo="bar", bar="baz")
    try:
        pex.expand(string, env, strict=True)
        raise AssertionError("ParameterExpansionNullError should be raised")
    except pex.ParameterExpansionNullError:
        pass


def test_expand_can_handle_substring_with_no_start():
    env = dict(_rpi_bt="1234567890ABCDEF")
    var = "${_rpi_bt::8}"
    expanded_var = pex.expand(var, env=env, strict=True)
    assert expanded_var == "12345678"


def test_expand_can_handle_substring_with_no_length():
    env = dict(pyname="123456ABCD")
    var = "${pyname:6}"
    expanded_var = pex.expand(var, env=env, strict=True)
    assert expanded_var == "ABCD"


def test_expand_can_handle_nested_pound_expand():
    env = dict(_pyname="cssselect2")
    var = "${_pyname%${_pyname#?}}"
    expanded_var = pex.expand(var, env=env, strict=True)
    assert expanded_var == "c"


def test_expand_can_handle_nested_substitution_and_pattern_expand():
    env = dict(pkgver="0.8.0_alpha19")
    var = "${pkgver/${pkgver%alpha*}/}"
    expanded_var = pex.expand(var, env=env, strict=True)
    assert expanded_var == "alpha19"


def test_expand_simple_expands_longest_param_name_first():
    env = dict(pkg="foo", pkgver="bar")
    var = "$pkgver"
    expanded_var = pex.expand(var, env=env, strict=True)
    assert expanded_var == "bar"


def test_tokenize_preserves_spaces():
    s = " - $parameter/$aa/${bb}   - \t- \n ${parameter/ aa /   - zz }- "
    tokens = list(parameter_expansion.pe.tokenize(s))
    expected = [
        " ",
        "-",
        " ",
        "$",
        "parameter",
        "/",
        "$",
        "aa",
        "/",
        "$",
        "{",
        "bb",
        "}",
        "   ",
        "-",
        " \t",
        "-",
        " \n ",
        "$",
        "{",
        "parameter",
        "/",
        " ",
        "aa",
        " ",
        "/",
        "   ",
        "-",
        " ",
        "zz",
        " ",
        "}",
        "-",
        " ",
    ]
    assert tokens == expected
