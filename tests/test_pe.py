import pe

subst_test_cases = {
    # string,        set_and_not_null, set_but_null, unset
    "-$parameter-":         ("-set-",  "--",         "--",),
    "-${parameter}-":       ("-set-",  "--",         "--",),
    "-${parameter:-word}-": ("-set-",  "-word-",     "-word-",),
    "-${parameter-word}-":  ("-set-",  "--",         "-word-",),
    "-${parameter:=word}-": ("-set-",  "-word-",     "-word-",),
    "-${parameter=word}-":  ("-set-",  "--",         "-word-",),
    "-${parameter:?word}-": ("-set-",  "error",      "error",),
    "-${parameter?word}-":  ("-set-",  "--",         "error",),
    "-${parameter:+word}-": ("-word-", "--",         "--",),
    "-${parameter+word}-":  ("-word-", "-word-",     "--",),
    "-${#parameter}-":      ("-3-",    "-0-",        "-0-",),
}

affix_test_cases = {
    # string,               parameter, result
    "-${parameter%/*}-":  ("aa/bb/cc", "-aa/bb-",),
    "-${parameter%%/*}-": ("aa/bb/cc", "-aa-",),
    "-${parameter#*/}-":  ("aa/bb/cc", "-bb/cc-",),
    "-${parameter##*/}-": ("aa/bb/cc", "-cc-",),
}

test_envs = (
    { "parameter": "set", "word": "word", }, # set and not null
    { "parameter": "", "word": "word", }, # set but null
    { "word": "word", }, # unset
)

test_case_map = ("Set and not null", "Set, but null", "Unset",)

def test():
    for string, tc in subst_test_cases.iteritems():
        for i, env in enumerate(test_envs):
            env = dict(env) # Don't allow tests to mutate each other's envs
            try:
                result = string, pe.expand(string, env), tc[i], test_case_map[i]
                assert result[1] == result[2], result
            except pe.ParameterExpansionNullError:
                assert tc[i] == "error", (string, tc[i], test_case_map[i])

    for string, tc in affix_test_cases.iteritems():
        env = {"parameter": tc[0],}
        from nose.tools import set_trace; set_trace()
        result = string, pe.expand(string, env), tc
        assert result[1] == tc[1], result
