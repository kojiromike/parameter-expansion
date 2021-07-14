import parameter_expansion as pex
import parameter_expansion.pe

subst_test_cases = {
    # string,        set_and_not_null, set_but_null, unset
    "-$parameter-": (
        "-set-",
        "--",
        "--",
    ),
    "-${parameter}-": (
        "-set-",
        "--",
        "--",
    ),
    "-${parameter:-word}-": (
        "-set-",
        "-word-",
        "-word-",
    ),
    "-${parameter-word}-": (
        "-set-",
        "--",
        "-word-",
    ),
    "-${parameter:=word}-": (
        "-set-",
        "-word-",
        "-word-",
    ),
    "-${parameter=word}-": (
        "-set-",
        "--",
        "-word-",
    ),
    "-${parameter:?word}-": (
        "-set-",
        "error",
        "error",
    ),
    "-${parameter?word}-": (
        "-set-",
        "--",
        "error",
    ),
    "-${parameter:+word}-": (
        "-word-",
        "--",
        "--",
    ),
    "- ${parameter:+word} -": (
        "- word -",
        "-  -",
        "-  -",
    ),
    "-${parameter+word}-": (
        "-word-",
        "-word-",
        "--",
    ),
    "-${#parameter}-": (
        "-3-",
        "-0-",
        "-0-",
    ),
}

affix_test_cases = {
    # string,               parameter, result
    "-${parameter%/*}-": (
        "aa/bb/cc",
        "-aa/bb-",
    ),
    "-${parameter%%/*}-": (
        "aa/bb/cc",
        "-aa-",
    ),
    "-${parameter#*/}-": (
        "aa/bb/cc",
        "-bb/cc-",
    ),
    "-${parameter##*/}-": (
        "aa/bb/cc",
        "-cc-",
    ),
}

substring_test_cases = {
    # string,               parameter, result
    "-${parameter:0:2}-": (
        "aa/bb/cc",
        "-aa-",
    ),
    "-${parameter:3:2}-": (
        "aa/bb/cc",
        "-bb-",
    ),
    "- ${parameter:3:2} -": (
        "aa/bb/cc",
        "- bb -",
    ),
    "-${parameter:6}-": (
        "aa/bb/cc",
        "-cc-",
    ),
}

replace_test_cases = {
    # string,               parameter, result
    "-${parameter/aa/bb}-": (
        "aa/bb/cc",
        "-bb/bb/cc-",
    ),
    "-${parameter/aa}-": (
        "aa/bb/cc",
        "-/bb/cc-",
    ),
    "-${parameter/ aa / - zz }-": (
        "bb/ aa /cc",
        "-bb/ - zz /cc-",
    ),
    "-${parameter/aa/}-": (
        "aa/bb/cc",
        "-/bb/cc-",
    ),
    "-${parameter/aa/zz}-": (
        "aa/bb/aa",
        "-zz/bb/aa-",
    ),
    "- ${parameter/aa/zz} -": (
        "aa/bb/aa",
        "- zz/bb/aa -",
    ),
    "-${parameter//aa/zz}-": (
        "aa/bb/aa",
        "-zz/bb/zz-",
    ),
    "-${parameter//aa}-": (
        "aa/bb/aa",
        "-/bb/-",
    ),
    "-${parameter//aa/ zz}-": (
        "aa/bb/aa",
        "- zz/bb/ zz-",
    ),
    "-${parameter/aa}-": (
        "aa/bb/aa",
        "-/bb/aa-",
    ),
    "-${parameter//aa}-": (
        "aa/bb/aa",
        "-/bb/-",
    ),
}

simple_test_cases = {
    # string,               env, result
    "-${parameter/$aa/$bb}-": (
        dict(
            parameter="FOO/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        "-BAR/bb/cc-",
    ),
    "- ${parameter/$aa/$bb} -": (
        dict(
            parameter="FOO/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        "- BAR/bb/cc -",
    ),
    "-$parameter/$aa/$bb-": (
        dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        "-aa/bb/cc/FOO/BAR-",
    ),
    "-${parameter/${aa}/${bb}}-": (
        dict(
            parameter="FOO/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        "-BAR/bb/cc-",
    ),
    "-$parameter/$aa/${bb}-": (
        dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        "-aa/bb/cc/FOO/BAR-",
    ),
    "- $parameter/$aa/${bb} -": (
        dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        "- aa/bb/cc/FOO/BAR -",
    ),
}

simple_simple_test_cases = {
    # string,               env, result
    "-$parameter/$aa/$bb-": (
        dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        "-aa/bb/cc/FOO/BAR-",
    ),
    "-$parameter/$aa/${bb}-": (
        dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        "-aa/bb/cc/FOO/BAR-",
    ),
    "- $parameter/$aa/${bb} -": (
        dict(
            parameter="aa/bb/cc",
            aa="FOO",
            bb="BAR",
        ),
        "- aa/bb/cc/FOO/BAR -",
    ),
}

test_envs = (
    {
        "parameter": "set",
        "word": "word",
    },  # set and not null
    {
        "parameter": "",
        "word": "word",
    },  # set but null
    {
        "word": "word",
    },  # unset
)

test_case_map = (
    "Set and not null",
    "Set, but null",
    "Unset",
)


def test_expand():
    for string, tc in subst_test_cases.items():
        for i, env in enumerate(test_envs):
            env = dict(env)  # Don't allow tests to mutate each other's envs
            try:
                result = string, pex.expand(string, env), tc[i], test_case_map[i]
                assert result[1] == result[2], result
            except pex.ParameterExpansionNullError:
                assert tc[i] == "error", (string, tc[i], test_case_map[i])

    for string, (parameter, expected) in affix_test_cases.items():
        env = {"parameter": parameter}
        assert pex.expand(string, env) == expected


def test_substring():
    for string, (parameter, expected) in substring_test_cases.items():
        env = {"parameter": parameter}
        assert pex.expand(string, env) == expected, (string, parameter)


def test_replace():
    for string, (parameter, expected) in replace_test_cases.items():
        env = {"parameter": parameter}
        assert pex.expand(string, env) == expected, (string, parameter)


def test_simple():
    for string, (env, expected) in simple_test_cases.items():
        assert pex.expand(string, env) == expected, (string, env)


def test_expand_simple():
    for string, (env, expected) in simple_simple_test_cases.items():
        assert parameter_expansion.pe.expand_simple(string, env) == expected, (
            string,
            env,
        )


def test_expand_strict_raises_Exception():
    string = "- $parameter/$aa/${bb}"
    env = dict(foo="bar", bar="baz")
    try:
        pex.expand(string, env, strict=True)
        raise Exception("ParameterExpansionNullError should be raised")
    except pex.ParameterExpansionNullError:
        pass


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
