# std
import sys
import math
import contextlib
import random
import StringIO
import types
import dis as original_dis
# pytest
import pytest
# backports
from backports import dis as backports_dis


################################################################################
#                               Objects To Test                                #
################################################################################


from test import dis_module


@staticmethod
def tricky(x, y, c, d, e=[], z=True, *args, **kwds):
    def f(c=c):
        print(x, y, z, c, d, e, f)
    yield x, y, z, c, d, e, f


def outer(a=1, b=2):
    def f(c=3, d=4):
        def inner(e=5, f=6):
            print(a, b, c, d, e, f)
        print(a, b, c, d)
        return inner
    print(a, b, '', 1, [], {}, "Hello world!")
    return f


def jumpy():
    # This won't actually run (but that's OK, we only disassemble it)
    for i in range(10):
        print(i)
        if i < 4:
            continue
        if i > 6:
            break
    else:
        print("I can haz else clause?")
    while i:
        print(i)
        i -= 1
        if i > 6:
            continue
        if i < 4:
            break
    else:
        print("Who let lolcatz into this test suite?")
    try:
        1 / 0
    except ZeroDivisionError:
        print("Here we go, here we go, here we go...")
    else:
        with i as dodgy:
            print("Never reach this")
    finally:
        print("OK, now we're done")


def generator(x):
    yield x


def bug708901():
    for res in range(1,
                     10):
        pass


def bug1333982(x=[]):
    assert 0, ([s for s in x] +
               1)


compound_stmt_str = """\
x = 0
while 1:
    x += 1"""
# Trailing newline has been deliberately omitted


simple_stmt_str = "x = x + 1"


expr_str = "x + 1"


def simple_function(a):
    print(a)
    return 1


class Class:

    def __init__(self, x):
        self.x = x == 1

    @staticmethod
    def sm(x):
        x = x == 1

    @classmethod
    def cm(cls, x):
        cls.x = x == 1

    def im(self, x):
        self.x = x == 1


code_object = ''


raw_bytecode = ''


generator_expression = (x for x in random.sample('dis', 2) if ord(x) < ord('m'))


expression_with_lambda = lambda: sorted([1,2,3], key=lambda x: x)


list_comprehension = lambda: [x for x in random.sample('dis', 2) if ord(x) < ord('m')]


set_comprehension = lambda: {x for x in random.sample('dis', 2) if ord(x) < ord('m')}


dict_comprehension = lambda: {x: x for x in random.sample('dis', 2) if ord(x) < ord('m')}


try:
    raise RuntimeError()
except RuntimeError:
    traceback = sys.exc_info()[2]


instance_method = Class.im


static_method = Class.sm


class_method = Class.cm


capture = 'dis'


def closure():
    return capture


def closure_reference():

    capture_ref = 'backports.dis'

    def inner():
        return capture


def complex_function_1():
    def outer(b, n, l):
        def function(a, b=b, c=None, *args, **kwargs):
            v = [x for x in args] + [(x, y) for x, y in kwargs.iteritems()]
            print(v)
            return v
        yield function(math.pi, l, c=32, kwarg=n) + [n, l]
    return outer


def complex_function_2():
    def function():
        it = range(0, int(math.pi * 10))
        for i, x in enumerate(it):
            if x == 1:
                next(it)
            elif x / 2 == 1:
                continue
            elif i > 10:
                break
            else:
                for i in xrange(2):
                    next(it)
                else:
                    x += 1
        else:
            while not True:
                break
    return function


def function_with_try():
    def function():
        try:
            1 / 0
        except:
            raise RuntimeError()
        else:
            print('else')
        finally:
            print('finally')
    return function


@contextlib.contextmanager
def decorated():
    yield


def class_decorator(cls):
    class Other(cls):
        pass
    return Other


@class_decorator
class DecoratedClass:
    def __init__(self):
        pass


code_with_extended_arg = \
    chr(backports_dis.opmap["JUMP_FORWARD"]) + chr(0) + chr(0) +\
    chr(backports_dis.EXTENDED_ARG) + chr(1) + chr(0) +\
    chr(backports_dis.opmap["JUMP_FORWARD"]) + chr(0) + chr(0) +\
    chr(backports_dis.opmap["RETURN_VALUE"])


objects_to_test = dict(
    dis_module=dis_module,
    tricky=tricky,
    outer=outer,
    jumpy=jumpy,
    generator=generator,
    bug708901=bug708901,
    bug1333982=bug1333982,
    compound_stmt_str=compound_stmt_str,
    simple_stmt_str=simple_stmt_str,
    expr_str=expr_str,
    simple_function=simple_function,
    Class=Class,
    code_object=code_object,
    raw_bytecode=raw_bytecode,
    generator_expression=generator_expression,
    list_comprehension=list_comprehension,
    set_comprehension=set_comprehension,
    dict_comprehension=dict_comprehension,
    traceback=traceback,
    instance_method=instance_method,
    static_method=static_method,
    class_method=class_method,
    closure=closure,
    closure_reference=closure_reference,
    complex_function_1=complex_function_1,
    complex_function_2=complex_function_2,
    function_with_try=function_with_try,
    decorated=decorated,
    DecoratedClass=DecoratedClass,
    expression_with_lambda=expression_with_lambda,
    code_with_extended_arg=code_with_extended_arg,
)


################################################################################
#                             Expected dis Output                              #
################################################################################


dis_module_dis_expected = """\
"""


tricky_dis_expected = """\
"""


outer_dis_expected = """\
"""


jumpy_dis_expected = """\
 38           0 SETUP_LOOP              64 (to 67)
              3 LOAD_GLOBAL              0 (range)
              6 LOAD_CONST               1 (10)
              9 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
             12 GET_ITER
        >>   13 FOR_ITER                45 (to 61)
             16 STORE_FAST               0 (i)

 39          19 LOAD_FAST                0 (i)
             22 PRINT_ITEM
             23 PRINT_NEWLINE

 40          24 LOAD_FAST                0 (i)
             27 LOAD_CONST               2 (4)
             30 COMPARE_OP               0 (<)
             33 POP_JUMP_IF_FALSE       42

 41          36 JUMP_ABSOLUTE           13
             39 JUMP_FORWARD             0 (to 42)

 42     >>   42 LOAD_FAST                0 (i)
             45 LOAD_CONST               3 (6)
             48 COMPARE_OP               4 (>)
             51 POP_JUMP_IF_FALSE       13

 43          54 BREAK_LOOP
             55 JUMP_ABSOLUTE           13
             58 JUMP_ABSOLUTE           13
        >>   61 POP_BLOCK

 45          62 LOAD_CONST               4 ('I can haz else clause?')
             65 PRINT_ITEM
             66 PRINT_NEWLINE

 46     >>   67 SETUP_LOOP              64 (to 134)
        >>   70 LOAD_FAST                0 (i)
             73 POP_JUMP_IF_FALSE      128

 47          76 LOAD_FAST                0 (i)
             79 PRINT_ITEM
             80 PRINT_NEWLINE

 48          81 LOAD_FAST                0 (i)
             84 LOAD_CONST               5 (1)
             87 INPLACE_SUBTRACT
             88 STORE_FAST               0 (i)

 49          91 LOAD_FAST                0 (i)
             94 LOAD_CONST               3 (6)
             97 COMPARE_OP               4 (>)
            100 POP_JUMP_IF_FALSE      109

 50         103 JUMP_ABSOLUTE           70
            106 JUMP_FORWARD             0 (to 109)

 51     >>  109 LOAD_FAST                0 (i)
            112 LOAD_CONST               2 (4)
            115 COMPARE_OP               0 (<)
            118 POP_JUMP_IF_FALSE       70

 52         121 BREAK_LOOP
            122 JUMP_ABSOLUTE           70
            125 JUMP_ABSOLUTE           70
        >>  128 POP_BLOCK

 54         129 LOAD_CONST               6 ('Who let lolcatz into this test suite?')
            132 PRINT_ITEM
            133 PRINT_NEWLINE

 55     >>  134 SETUP_FINALLY           61 (to 198)
            137 SETUP_EXCEPT            12 (to 152)

 56         140 LOAD_CONST               5 (1)
            143 LOAD_CONST               7 (0)
            146 BINARY_DIVIDE
            147 POP_TOP
            148 POP_BLOCK
            149 JUMP_FORWARD            22 (to 174)

 57     >>  152 DUP_TOP
            153 LOAD_GLOBAL              1 (ZeroDivisionError)
            156 COMPARE_OP              10 (exception match)
            159 POP_JUMP_IF_FALSE      173
            162 POP_TOP
            163 POP_TOP
            164 POP_TOP

 58         165 LOAD_CONST               8 ('Here we go, here we go, here we go...')
            168 PRINT_ITEM
            169 PRINT_NEWLINE
            170 JUMP_FORWARD            21 (to 194)
        >>  173 END_FINALLY

 60     >>  174 LOAD_FAST                0 (i)
            177 SETUP_WITH              12 (to 192)
            180 STORE_FAST               1 (dodgy)

 61         183 LOAD_CONST               9 ('Never reach this')
            186 PRINT_ITEM
            187 PRINT_NEWLINE
            188 POP_BLOCK
            189 LOAD_CONST               0 (None)
        >>  192 WITH_CLEANUP
            193 END_FINALLY
        >>  194 POP_BLOCK
            195 LOAD_CONST               0 (None)

 63     >>  198 LOAD_CONST              10 ("OK, now we're done")
            201 PRINT_ITEM
            202 PRINT_NEWLINE
            203 END_FINALLY
            204 LOAD_CONST               0 (None)
            207 RETURN_VALUE
"""


generator_dis_expected = """\
"""


bug708901_dis_expected = """\
"""


bug1333982_dis_expected = """\
 76           0 LOAD_CONST               1 (0)
              3 STORE_FAST               1 (@py_assert0)
              6 LOAD_FAST                1 (@py_assert0)
              9 POP_JUMP_IF_TRUE        98
             12 LOAD_GLOBAL              0 (@pytest_ar)
             15 LOAD_ATTR                1 (_format_assertmsg)
             18 BUILD_LIST               0
             21 LOAD_FAST                0 (x)
             24 GET_ITER
        >>   25 FOR_ITER                12 (to 40)
             28 STORE_FAST               2 (s)
             31 LOAD_FAST                2 (s)
             34 LIST_APPEND              2
             37 JUMP_ABSOLUTE           25
        >>   40 LOAD_CONST               2 (1)
             43 BINARY_ADD
             44 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
             47 LOAD_CONST               3 ('\\n>assert %(py1)s')
             50 BINARY_ADD
             51 BUILD_MAP                1
             54 LOAD_GLOBAL              0 (@pytest_ar)
             57 LOAD_ATTR                2 (_saferepr)
             60 LOAD_FAST                1 (@py_assert0)
             63 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
             66 LOAD_CONST               4 ('py1')
             69 STORE_MAP
             70 BINARY_MODULO
             71 STORE_FAST               3 (@py_format2)
             74 LOAD_GLOBAL              3 (AssertionError)
             77 LOAD_GLOBAL              0 (@pytest_ar)
             80 LOAD_ATTR                4 (_format_explanation)
             83 LOAD_FAST                3 (@py_format2)
             86 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
             89 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
             92 RAISE_VARARGS            1
             95 JUMP_FORWARD             0 (to 98)
        >>   98 LOAD_CONST               0 (None)
            101 STORE_FAST               1 (@py_assert0)
            104 LOAD_CONST               0 (None)
            107 RETURN_VALUE
"""


compound_stmt_str_dis_expected = """\
"""


simple_stmt_str_dis_expected = """\
"""


expr_str_dis_expected = """\
"""


simple_function_dis_expected = """\
"""


Class_dis_expected = """\
"""


code_object_dis_expected = """\
"""


raw_bytecode_dis_expected = """\
"""


generator_expression_dis_expected = """\
"""


list_comprehension_dis_expected = """\
"""


set_comprehension_dis_expected = """\
"""


dict_comprehension_dis_expected = """\
130           0 LOAD_CONST               1 (<code object <dictcomp> at 02DA8B60, file "D:\Personal\github\backports.dis\src\backports\tests\test_objects.py", line 130>)
              3 MAKE_FUNCTION            0
              6 LOAD_CONST               2 ('dis')
              9 GET_ITER
             10 CALL_FUNCTION            1 (1 positional, 0 keyword pair)
             13 RETURN_VALUE
"""


traceback_dis_expected = """\
"""


instance_method_dis_expected = """\
"""


static_method_dis_expected = """\
"""


class_method_dis_expected = """\
"""


closure_dis_expected = """\
152           0 LOAD_GLOBAL              0 (capture)
              3 RETURN_VALUE
"""


closure_reference_dis_expected = """\
"""


complex_function_1_dis_expected = """\
"""


complex_function_2_dis_expected = """\
"""


function_with_try_dis_expected = """\
"""


decorated_dis_expected = """\
"""


DecoratedClass_dis_expected = """\
"""


expression_with_lambda_dis_expected = """\
"""


code_with_extended_arg_dis_expected = """\
"""


################################################################################
#                          Expected code_info Output                           #
################################################################################


dis_module_code_info_expected = """\
"""


tricky_code_info_expected = """\
"""


outer_code_info_expected = """\
"""


jumpy_code_info_expected = """\
"""


generator_code_info_expected = """\
"""


bug708901_code_info_expected = """\
"""


bug1333982_code_info_expected = """\
"""


compound_stmt_str_code_info_expected = """\
"""


simple_stmt_str_code_info_expected = """\
"""


expr_str_code_info_expected = """\
"""


simple_function_code_info_expected = """\
"""


Class_code_info_expected = """\
"""


code_object_code_info_expected = """\
"""


raw_bytecode_code_info_expected = """\
"""


generator_expression_code_info_expected = """\
"""


list_comprehension_code_info_expected = """\
"""


set_comprehension_code_info_expected = """\
"""


dict_comprehension_code_info_expected = """\
"""


traceback_code_info_expected = """\
"""


instance_method_code_info_expected = """\
"""


static_method_code_info_expected = """\
"""


class_method_code_info_expected = """\
"""


closure_code_info_expected = """\
"""


closure_reference_code_info_expected = """\
"""


complex_function_1_code_info_expected = """\
"""


complex_function_2_code_info_expected = """\
"""


function_with_try_code_info_expected = """\
"""


decorated_code_info_expected = """\
"""


DecoratedClass_code_info_expected = """\
"""


expression_with_lambda_code_info_expected = """\
"""


code_with_extended_arg_code_info_expected = """\
"""


################################################################################
#                       Expected get_instructions Output                       #
################################################################################


dis_module_get_instructions_expected = [
]


tricky_get_instructions_expected = [
]


outer_get_instructions_expected = [
]


jumpy_get_instructions_expected = [
]


generator_get_instructions_expected = [
]


bug708901_get_instructions_expected = [
]


bug1333982_get_instructions_expected = [
]


compound_stmt_str_get_instructions_expected = [
]


simple_stmt_str_get_instructions_expected = [
]


expr_str_get_instructions_expected = [
]


simple_function_get_instructions_expected = [
]


Class_get_instructions_expected = [
]


code_object_get_instructions_expected = [
]


raw_bytecode_get_instructions_expected = [
]


generator_expression_get_instructions_expected = [
]


list_comprehension_get_instructions_expected = [
]


set_comprehension_get_instructions_expected = [
]


dict_comprehension_get_instructions_expected = [
]


traceback_get_instructions_expected = [
]


instance_method_get_instructions_expected = [
]


static_method_get_instructions_expected = [
]


class_method_get_instructions_expected = [
]


closure_get_instructions_expected = [
]


closure_reference_get_instructions_expected = [
]


complex_function_1_get_instructions_expected = [
]


complex_function_2_get_instructions_expected = [
]


function_with_try_get_instructions_expected = [
]


decorated_get_instructions_expected = [
]


DecoratedClass_get_instructions_expected = [
]


expression_with_lambda_get_instructions_expected = [
]


code_with_extended_arg_get_instructions_expected = [

]


################################################################################
#                       Verify Expected Output Declared                        #
################################################################################


def get_expected_name(object_to_test, function_to_test):
    return '_'.join([object_to_test, function_to_test, 'expected'])


def verify_expected_declared():
    for object_to_test in objects_to_test:
        for function_to_test in ('dis', 'code_info', 'get_instructions'):
            expected = get_expected_name(object_to_test, function_to_test)
            assert expected in globals(), expected + ' not declared'


verify_expected_declared()

################################################################################
#                              Data Driven Tests                               #
################################################################################


@pytest.mark.parametrize('object_name, object_to_test', objects_to_test.items())
def test_dis(object_name, object_to_test):
    stream = StringIO.StringIO()
    if isinstance(object_to_test, types.TracebackType):
        backports_dis.distb(object_to_test, stream)
    else:
        backports_dis.dis(object_to_test, stream)
    actual = stream.getvalue()
    expected = globals()[get_expected_name(object_name, 'dis')]
    open('actual', 'w').write(actual)
    open('expected', 'w').write(expected)
    #dis_output_compare(expected, actual, object_name)
    #assert actual == expected, 'Failure in ' + object_name


@pytest.mark.parametrize('object_name, object_to_test', objects_to_test.items())
def test_code_info(object_name, object_to_test):
    for object_to_test in objects_to_test:
        pass


@pytest.mark.parametrize('object_name, object_to_test', objects_to_test.items())
def test_instructions(object_name, object_to_test):
    for object_to_test in objects_to_test:
        pass


@pytest.mark.parametrize('object_name, object_to_test', objects_to_test.items())
def test_backports_vs_original(object_name, object_to_test):
    for object_to_test in objects_to_test:
        pass


################################################################################
#                           Extra Tests For Coverage                           #
################################################################################



################################################################################
#                                ByteCode Tests                                #
################################################################################
