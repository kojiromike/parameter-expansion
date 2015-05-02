test_cases = {
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
    "-${parameter%word}":   ("--",     "--",         "--",),
    "-${parameter%%word}-": ("--",     "--",         "--",),
    "-${parameter#word}-":  ("--",     "--",         "--",),
    "-${parameter##word}-": ("--",     "--",         "--",),
}

test_envs = (
    { "parameter": "set", "word": "word", }, # set and not null
    { "parameter": "", "word": "word", }, # set but null
    { "word": "word", }, # unset
)

from pe import expand

def test():
    for string, tc in test_cases.iteritems():
        for i, env in enumerate(test_envs):
            from nose.tools import set_trace; set_trace()
            result = expand(string, env), tc[i]
            assert expand(string, env) == tc[i], result
