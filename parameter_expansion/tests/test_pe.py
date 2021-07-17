from collections import namedtuple

import pytest

import parameter_expansion as pex
import parameter_expansion.pe

Test = namedtuple("Test", ["tested_shell", "expected_str", "env"])

subst_test_cases = [
    # string,        (set_and_not_null, set_but_null, unset)
    Test(
        tested_shell="-$parameter-",
        expected_str="-set-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
    ),
    Test(
        tested_shell="-$parameter-",
        expected_str="--",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
    ),
    Test(
        tested_shell="-$parameter-",
        expected_str="-$parameter-",
        env={
            "word": "word",
        },  # unset
    ),
    Test(
        tested_shell="-${parameter}-",
        expected_str="-set-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
    ),
    Test(
        tested_shell="-${parameter}-",
        expected_str="--",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
    ),
    Test(
        tested_shell="-${parameter}-",
        expected_str="--",
        env={
            "word": "word",
        },  # unset
    ),
    Test(
        tested_shell="-${parameter:-word}-",
        expected_str="-set-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
    ),
    Test(
        tested_shell="-${parameter:-word}-",
        expected_str="-word-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
    ),
    Test(
        tested_shell="-${parameter:-word}-",
        expected_str="-word-",
        env={
            "word": "word",
        },  # unset
    ),
    Test(
        tested_shell="-${parameter-word}-",
        expected_str="-set-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
    ),
    Test(
        tested_shell="-${parameter-word}-",
        expected_str="--",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
    ),
    Test(
        tested_shell="-${parameter-word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="-word-",
    ),
    Test(
        tested_shell="-${parameter:=word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-set-",
    ),
    Test(
        tested_shell="-${parameter:=word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="-word-",
    ),
    Test(
        tested_shell="-${parameter:=word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="-word-",
    ),
    Test(
        tested_shell="-${parameter=word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-set-",
    ),
    Test(
        tested_shell="-${parameter=word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="--",
    ),
    Test(
        tested_shell="-${parameter=word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="-word-",
    ),
    Test(
        tested_shell="-${parameter:?word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-set-",
    ),
    Test(
        tested_shell="-${parameter:?word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="error",
    ),
    Test(
        tested_shell="-${parameter:?word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="error",
    ),
    Test(
        tested_shell="-${parameter?word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-set-",
    ),
    Test(
        tested_shell="-${parameter?word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="--",
    ),
    Test(
        tested_shell="-${parameter?word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="error",
    ),
    Test(
        tested_shell="-${parameter:+word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-word-",
    ),
    Test(
        tested_shell="-${parameter:+word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="--",
    ),
    Test(
        tested_shell="-${parameter:+word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="--",
    ),
    Test(
        tested_shell="- ${parameter:+word} -",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="- word -",
    ),
    Test(
        tested_shell="- ${parameter:+word} -",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="-  -",
    ),
    Test(
        tested_shell="- ${parameter:+word} -",
        env={
            "word": "word",
        },  # unset
        expected_str="-  -",
    ),
    Test(
        tested_shell="-${parameter+word}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-word-",
    ),
    Test(
        tested_shell="-${parameter+word}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="-word-",
    ),
    Test(
        tested_shell="-${parameter+word}-",
        env={
            "word": "word",
        },  # unset
        expected_str="--",
    ),
    Test(
        tested_shell="-${#parameter}-",
        env={
            "parameter": "set",
            "word": "word",
        },  # set and not null
        expected_str="-3-",
    ),
    Test(
        tested_shell="-${#parameter}-",
        env={
            "parameter": "",
            "word": "word",
        },  # set but null
        expected_str="-0-",
    ),
    Test(
        tested_shell="-${#parameter}-",
        env={
            "word": "word",
        },  # unset
        expected_str="-0-",
    ),
]

affix_test_cases = [
    # tested shell string, (parameter, expected result)
    Test(
        tested_shell="-${parameter%/*}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-aa/bb-",
    ),
    Test(
        tested_shell="-${parameter%%/*}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-aa-",
    ),
    Test(
        tested_shell="-${parameter#*/}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-bb/cc-",
    ),
    Test(
        tested_shell="-${parameter##*/}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-cc-",
    ),
]

substring_test_cases = [
    # tested shell string, (parameter, expected result)
    Test(
        tested_shell="-${parameter:0:2}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-aa-",
    ),
    Test(
        tested_shell="-${parameter:3:2}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-bb-",
    ),
    Test(
        tested_shell="- ${parameter:3:2} -",
        env={"parameter": "aa/bb/cc"},
        expected_str="- bb -",
    ),
    Test(
        tested_shell="-${parameter:6}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-cc-",
    ),
]

replace_test_cases = [
    # tested shell string,  (parameter, expected_str)
    Test(
        tested_shell="-${parameter/aa/bb}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-bb/bb/cc-",
    ),
    Test(
        tested_shell="-${parameter/aa}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-/bb/cc-",
    ),
    Test(
        tested_shell="-${parameter/ aa / - zz }-",
        env={"parameter": "bb/ aa /cc"},
        expected_str="-bb/ - zz /cc-",
    ),
    Test(
        tested_shell="-${parameter/aa/}-",
        env={"parameter": "aa/bb/cc"},
        expected_str="-/bb/cc-",
    ),
    Test(
        tested_shell="-${parameter/aa/zz}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="-zz/bb/aa-",
    ),
    Test(
        tested_shell="- ${parameter/aa/zz} -",
        env={"parameter": "aa/bb/aa"},
        expected_str="- zz/bb/aa -",
    ),
    Test(
        tested_shell="-${parameter//aa/zz}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="-zz/bb/zz-",
    ),
    Test(
        tested_shell="-${parameter//aa}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="-/bb/-",
    ),
    Test(
        tested_shell="-${parameter//aa/ zz}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="- zz/bb/ zz-",
    ),
    Test(
        tested_shell="-${parameter/aa}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="-/bb/aa-",
    ),
    Test(
        tested_shell="-${parameter//aa}-",
        env={"parameter": "aa/bb/aa"},
        expected_str="-/bb/-",
    ),
]

simple_test_cases = [
    # tested shell string,    (env, expected result)
    Test(
        tested_shell="-${parameter/$aa/$bb}-",
        env=dict(
            parameter="FOO/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="-BAR/bb/cc-",
    ),
    Test(
        tested_shell="- ${parameter/$aa/$bb} -",
        env=dict(
            parameter="FOO/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="- BAR/bb/cc -",
    ),
    Test(
        tested_shell="-$parameter/$aa/$bb-",
        env=dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="-aa/bb/cc/FOO/BAR-",
    ),
    Test(
        tested_shell="-${parameter/${aa}/${bb}}-",
        env=dict(
            parameter="FOO/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="-BAR/bb/cc-",
    ),
    Test(
        tested_shell="-$parameter/$aa/${bb}-",
        expected_str="-aa/bb/cc/FOO/BAR-",
        env=dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
    ),
    Test(
        tested_shell="- $parameter/$aa/${bb} -",
        env=dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="- aa/bb/cc/FOO/BAR -",
    ),
]

simple_simple_test_cases = [
    # string,               env, result
    Test(
        tested_shell="-$parameter/$aa/$bb-",
        env=dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="-aa/bb/cc/FOO/BAR-",
    ),
    Test(
        tested_shell="-$parameter/$aa/${bb}-",
        env=dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        expected_str="-aa/bb/cc/FOO/BAR-",
    ),
    Test(
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
        raise Exception("ParameterExpansionNullError should be raised")
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
