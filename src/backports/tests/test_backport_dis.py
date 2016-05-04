# std
import sys
import inspect
import types
import math
import re
import contextlib
from StringIO import StringIO
import dis as original
from functools import wraps
# backport.dis
from backports import dis as backport
# pytest
import pytest


############################## Utility Functions ###############################

def do_dis(object_to_test, module_to_use, stream=None):
    """
    Perform the call to dis, ensuring that the correct function (dis vs distb)
    is called depending on the object type

    :param object_to_test: The object under test.
    :param module_to_use: The module in which dis resides.
    :param stream: The stream to write data to.
    """

    if isinstance(object_to_test, types.TracebackType):
        if stream:
            module_to_use.distb(object_to_test, stream)
        else:
            module_to_use.distb(object_to_test)
    else:
        if stream:
            module_to_use.dis(object_to_test, stream)
        else:
            module_to_use.dis(object_to_test)


def dump_to_disk(test_function, actual, expected):
    """
    Dump the actual and expected information to disk which can be useful for
    determining why a test is failing

    :param test_function: The function which returns the object to test.
    :param actual: The result from the backport dis module.
    :param expected: The result from the original dis module.
    """
    # change to if 1 to dump actual and expected output to disk
    if 0:
        with open(test_function.__name__ + '_actual', 'w') as a:
            a.write(actual)
        with open(test_function.__name__ + '_expected', 'w') as a:
            a.write(expected)


def get_backport(object_to_test):
    """
    Use the backport dis module to get the disassembled information about a
    code object.

    :param object_to_test: The object to pass to dis.

    :return: String containing the disassmbled code.
    """
    stream = StringIO()
    do_dis(object_to_test, backport, stream)
    return stream.getvalue()


def get_original(object_to_test):
    """
    Use the original dis module to get the disassembled information about a
    code object.

    :param object_to_test: The object to pass to dis.

    :return: String containing the disassmbled code.
    """
    stream = StringIO()
    stdout = sys.stdout
    sys.stdout = stream
    try:
        if isinstance(object_to_test, types.GeneratorType):
            object_to_test = object_to_test.gi_frame.f_code

        # disassembling of strings seems pretty broken in python2 just compile
        # the string to a code object and compare the result
        if isinstance(object_to_test, str):
            object_to_test = compile(object_to_test, '<dis>', 'exec')

        do_dis(object_to_test, original)
    finally:
        sys.stdout = stdout

    return stream.getvalue().strip()


def normalize(output):
    """
    Normalize the output from the dis module to account for expected
    differences between python 2 and python 3:

        * Pointers in the string
        * Addition of hasnargs

    :param output: The output from the dis module.

    :return: Normalized output.
    """
    # remove any code object addresses which will be different between
    # expected and actual
    regex = re.compile('code object [^ ]* at (0x)?[0-9A-Fa-f]*')
    output = regex.sub('', output)

    # remove (<n> positional, <n> keyword pair) which is not supported in
    # python2
    regex = re.compile('\([0-9]+ positional\, [0-9]+ keyword pair\)')
    output = regex.sub('', output)

    return output


def compare(dis_output1, dis_output2):
    """
    Compare the output from two dis modules, taking into account the fact that
    padding is different between python 2 and 3 so ignore whitespace when
    comparing.

    :param dis_output1: The output from the first dis module.
    :param dis_output2: The output from the second dis module.
    """
    actual_lines = dis_output1.split('\n')
    expected_lines = dis_output2.split('\n')
    for actual_line, expected_line in zip(actual_lines, expected_lines):
        if actual_line.replace(' ', '') != expected_line.replace(' ', ''):
            assert dis_output1 == dis_output2


def backport_dis_test(test_function):
    """
    Decorator which can be used to verify that the backport.dis module produces
    the expected result by comparing with the result from the standard dis
    module.

    :param test_function: The function which returns the object to test.

    :return: The decorated function.
    """

    @wraps(test_function)
    def inner():
        object_to_test = test_function()
        actual = get_backport(object_to_test)
        expected = get_original(object_to_test)
        dump_to_disk(test_function, actual, expected)
        actual = normalize(actual)
        expected = normalize(expected)
        compare(actual, expected)

    inner.test_function = test_function

    return inner


########################## Backport vs Original Tests ##########################

@backport_dis_test
def test_traceback():
    try:
        raise Exception()
    except:
        return sys.exc_info()[2]


@backport_dis_test
def test_method():
    class Class:
        def method(self):
            return 0
    return Class.method


@backport_dis_test
def test_closure():
    capture = 'backports.dis'
    def function():
        return capture
    return function


@backport_dis_test
def test_closure_reference():
    def function():
        capture = 'backports.dis'
        def inner():
            return capture
    return function


@backport_dis_test
def test_function():
    def function():
        return 0
    return function


@backport_dis_test
def test_generator():
    return (x for x in 'backport.dis' if ord(x) < 24)


@backport_dis_test
def test_class():
    class Class:
        def method(self):
            return 0
    return Class


@backport_dis_test
def test_module():
    return sys


@backport_dis_test
def test_code_object():
    generator = test_generator.test_function
    return generator().gi_frame.f_code


@backport_dis_test
def test_raw_bytecode():
    return compile('''def function(): return 0''', '<string>', 'exec')


@backport_dis_test
def test_source_code():
    return '''def function(): return 0'''


@backport_dis_test
def perform_last_traceback_test():
    return None  # dis(None) is equivalent to sys.last_traceback


@contextlib.contextmanager
def set_last_traceback(value):
    """
    Temporarily set the last traceback value on sys, restoring upon exit.
    If value is None then any existing value of last_traceback will be
    deleted.

    :param value: The new value of last_traceback to set (None to delete
                  existing)
    """
    last = getattr(sys, 'last_traceback', None)
    if value:
        sys.last_traceback = value
    elif last:
        del sys.last_traceback
    try:
        yield
    finally:
        if last:
            sys.last_traceback = last


def test_last_traceback():
    try:
        raise Exception()
    except:
        with set_last_traceback(sys.exc_info()[2]):
            perform_last_traceback_test()


def test_no_last_traceback():
    with set_last_traceback(None):
        with pytest.raises(RuntimeError):
            perform_last_traceback_test()


############################# Test Misc Functions ##############################

def test_unknown():
    with pytest.raises(TypeError):
        backport.dis(math.pi)


def test_pretty_flags():
    assert backport.pretty_flags(1 | 4 | 32) == 'OPTIMIZED, VARARGS, GENERATOR'
    assert backport.pretty_flags(512 | 2048) == '0x200, 0x800'
    assert backport.pretty_flags(8589934592) == '0x200000000'  # 2^33


def test_get_code_object():
    raise NotImplementedError()


def test_code_info_method():
    class Class:
        def method(self):
            return None
    file = __file__
    expected = '''Name:              method
Filename:          {file}
Argument count:    1
Number of locals:  1
Stack size:        1
Flags:             OPTIMIZED, NEWLOCALS, NESTED, NOFREE
Constants:
   0: None
Names:
   0: None
Variable names:
   0: self'''.format(**locals())
    actual = backport.code_info(Class.method)
    assert actual == expected


def test_code_info_function():
    def function(param):
        return None
    file = __file__
    expected = '''Name:              function
Filename:          {file}
Argument count:    1
Number of locals:  1
Stack size:        1
Flags:             OPTIMIZED, NEWLOCALS, NESTED, NOFREE
Constants:
   0: None
Names:
   0: None
Variable names:
   0: param'''.format(**locals())
    actual = backport.code_info(function)
    assert actual == expected


def test_code_info_generator():
    generator = (x for x in 'backports.dis')
    file = __file__
    expected = '''Name:              <genexpr>
Filename:          {file}
Argument count:    1
Number of locals:  2
Stack size:        2
Flags:             OPTIMIZED, NEWLOCALS, NESTED, GENERATOR, NOFREE
Constants:
   0: None
Variable names:
   0: .0
   1: x'''.format(**locals())
    actual = backport.code_info(generator)
    assert actual == expected


def test_code_info_source_code():
    source_code = '(x for x in "backports.dis")'
    file = __file__
    expected = """Name:              <module>
Filename:          <disassembly>
Argument count:    0
Number of locals:  0
Stack size:        2
Flags:             NOFREE, 0x10000
Constants:
   0: <, file "<disassembly>", line 1>
   1: 'backports.dis'"""
    actual = backport.code_info(source_code)
    expected = normalize(expected)
    actual = normalize(actual)
    assert actual == expected


def test_code_info_code_object():
    source_code = compile('(x for x in "backports.dis")', '<str>', 'exec')
    file = __file__
    expected = """Name:              <module>
Filename:          <str>
Argument count:    0
Number of locals:  0
Stack size:        2
Flags:             NOFREE
Constants:
   0: <, file "<str>", line 1>
   1: 'backports.dis'
   2: None"""
    actual = backport.code_info(source_code)
    expected = normalize(expected)
    actual = normalize(actual)
    assert actual == expected


def test_code_info_type_error():
    with pytest.raises(TypeError):
        backport.code_info(math.pi)


def test_code_info_closure():
    capture = 'backports.dis'
    def function():
        return capture
    file = __file__
    expected = '''Name:              function
Filename:          {file}
Argument count:    0
Number of locals:  0
Stack size:        1
Flags:             OPTIMIZED, NEWLOCALS, NESTED
Constants:
   0: None
Free variables:
   0: capture'''.format(**locals())
    actual = backport.code_info(function)
    assert actual == expected


def test_code_info_closure_referenced():
    def function():
        capture = 'backports.dis'
        def inner():
            return capture
    line = inspect.getframeinfo(inspect.currentframe()).lineno - 2
    file = __file__
    expected = '''Name:              function
Filename:          {file}
Argument count:    0
Number of locals:  1
Stack size:        2
Flags:             OPTIMIZED, NEWLOCALS, NESTED
Constants:
   0: None
   1: 'backports.dis'
   2: <, file "{file}", line {line}>
Variable names:
   0: inner
Cell variables:
   0: capture'''.format(**locals())
    actual = backport.code_info(function)
    expected = normalize(expected)
    actual = normalize(actual)
    assert actual == expected


def test_format_code_info():
    raise NotImplementedError()


def test_show_code():
    class Class:
        def method(self):
            return None
    file = __file__
    expected = '''Name:              method
Filename:          {file}
Argument count:    1
Number of locals:  1
Stack size:        1
Flags:             OPTIMIZED, NEWLOCALS, NESTED, NOFREE
Constants:
   0: None
Names:
   0: None
Variable names:
   0: self
'''.format(**locals())
    stream = StringIO()
    backport.show_code(Class.method, stream)
    actual = stream.getvalue()
    assert actual == expected


def test_get_instructions():
    actual = list(backport.get_instructions(x for x in [1,2,3]))
    starts_line = inspect.getframeinfo(inspect.currentframe()).lineno - 1
    expected = [
       backport._Instruction(opname='LOAD_FAST', opcode=124, arg=0, argval='.0', argrepr='.0', offset=0, starts_line=starts_line, is_jump_target=False),
       backport._Instruction(opname='FOR_ITER', opcode=93, arg=11, argval=17, argrepr='to 17', offset=3, starts_line=None, is_jump_target=True),
       backport._Instruction(opname='STORE_FAST', opcode=125, arg=1, argval='x', argrepr='x', offset=6, starts_line=None, is_jump_target=False),
       backport._Instruction(opname='LOAD_FAST', opcode=124, arg=1, argval='x', argrepr='x', offset=9, starts_line=None, is_jump_target=False),
       backport._Instruction(opname='YIELD_VALUE', opcode=86, arg=None, argval=None, argrepr='', offset=12, starts_line=None, is_jump_target=False),
       backport._Instruction(opname='POP_TOP', opcode=1, arg=None, argval=None, argrepr='', offset=13, starts_line=None, is_jump_target=False),
       backport._Instruction(opname='JUMP_ABSOLUTE', opcode=113, arg=3, argval=3, argrepr='', offset=14, starts_line=None, is_jump_target=False),
       backport._Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval=None, argrepr='None', offset=17, starts_line=None, is_jump_target=True),
       backport._Instruction(opname='RETURN_VALUE', opcode=83, arg=None, argval=None, argrepr='', offset=20, starts_line=None, is_jump_target=False),
    ]
    assert actual == expected


def test_get_instructions_with_offset():
    def function():
        print(None)
        return None
    actual = list(backport.get_instructions(function, 999))
    expected = [
        backport._Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval=None, argrepr='None', offset=0, starts_line=1000, is_jump_target=False),
        backport._Instruction(opname='PRINT_ITEM', opcode=71, arg=None, argval=None, argrepr='', offset=3, starts_line=None, is_jump_target=False),
        backport._Instruction(opname='PRINT_NEWLINE', opcode=72, arg=None, argval=None, argrepr='', offset=4, starts_line=None, is_jump_target=False),
        backport._Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval=None, argrepr='None', offset=5, starts_line=1001, is_jump_target=False),
        backport._Instruction(opname='RETURN_VALUE', opcode=83, arg=None, argval=None, argrepr='', offset=8, starts_line=None, is_jump_target=False)
    ]
    assert actual == expected


def test_with_extended_arg():
    raise NotImplementedError()


############################# Test Bytecode Class ##############################

class TestBytecode():

    def test_construct(self):
        raise NotImplementedError()

    def test_iterate(self):
        raise NotImplementedError()

    def test_repr(self):
        raise NotImplementedError()

    def test_from_traceback(self):
        raise NotImplementedError()

    def test_info(self):
        raise NotImplementedError()

    def test_dis(self):
        raise NotImplementedError()


################################# Test Program #################################

def test_program():
    raise NotImplementedError()
