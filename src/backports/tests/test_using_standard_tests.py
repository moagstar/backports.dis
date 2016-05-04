# Minimal tests for dis module

from test.test_support import run_unittest
import unittest
import sys
import backports.dis as dis
import StringIO


def _f(a):
    print a
    return 1

dis_f = """\
 %-4d         0 LOAD_FAST                0 (a)
              3 PRINT_ITEM
              4 PRINT_NEWLINE

 %-4d         5 LOAD_CONST               1 (1)
              8 RETURN_VALUE
"""%(_f.func_code.co_firstlineno + 1,
     _f.func_code.co_firstlineno + 2)


def bug708901():
    for res in range(1,
                     10):
        pass

dis_bug708901 = """\
 %-4d         0 SETUP_LOOP              23 (to 26)
              3 LOAD_GLOBAL              0 (range)
              6 LOAD_CONST               1 (1)

 %-4d         9 LOAD_CONST               2 (10)
             12 CALL_FUNCTION            2 (2 positional, 0 keyword pair)
             15 GET_ITER
        >>   16 FOR_ITER                 6 (to 25)
             19 STORE_FAST               0 (res)

 %-4d        22 JUMP_ABSOLUTE           16
        >>   25 POP_BLOCK
        >>   26 LOAD_CONST               0 (None)
             29 RETURN_VALUE
"""%(bug708901.func_code.co_firstlineno + 1,
     bug708901.func_code.co_firstlineno + 2,
     bug708901.func_code.co_firstlineno + 3)


def bug1333982(x=[]):
    assert 0, ([s for s in x] +
              1)
    pass

# this looks very different to the standard python dis test expected bytecode
# this is because py.test patches the assert functionality
dis_bug1333982 = """\
 %-4d         0 LOAD_CONST               1 (0)
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
             47 LOAD_CONST               3 ('\\n>assert %%(py1)s')
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

 %-4d       104 LOAD_CONST               0 (None)
            107 RETURN_VALUE
"""%(bug1333982.func_code.co_firstlineno + 1,
     bug1333982.func_code.co_firstlineno + 3)

_BIG_LINENO_FORMAT = """\
%3d           0 LOAD_GLOBAL              0 (spam)
              3 POP_TOP
              4 LOAD_CONST               0 (None)
              7 RETURN_VALUE
"""

class DisTests(unittest.TestCase):

    def do_disassembly_test(self, func, expected):
        s = StringIO.StringIO()
        save_stdout = sys.stdout
        sys.stdout = s
        dis.dis(func)
        sys.stdout = save_stdout
        got = s.getvalue()
        # Trim trailing blanks (if any).
        lines = got.split('\n')
        lines = [line.rstrip() for line in lines]
        expected = expected.split("\n")
        import difflib
        if expected != lines:
            self.fail(
                "events did not match expectation:\n" +
                "\n".join(difflib.ndiff(expected,
                                        lines)))

    def test_opmap(self):
        self.assertEqual(dis.opmap["STOP_CODE"], 0)
        self.assertEqual(dis.opmap["LOAD_CONST"] in dis.hasconst, True)
        self.assertEqual(dis.opmap["STORE_NAME"] in dis.hasname, True)

    def test_opname(self):
        self.assertEqual(dis.opname[dis.opmap["LOAD_FAST"]], "LOAD_FAST")

    def test_boundaries(self):
        self.assertEqual(dis.opmap["EXTENDED_ARG"], dis.EXTENDED_ARG)
        self.assertEqual(dis.opmap["STORE_NAME"], dis.HAVE_ARGUMENT)

    def test_dis(self):
        self.do_disassembly_test(_f, dis_f)

    def test_bug_708901(self):
        self.do_disassembly_test(bug708901, dis_bug708901)

    def test_bug_1333982(self):
        # This one is checking bytecodes generated for an `assert` statement,
        # so fails if the tests are run with -O.  Skip this test then.
        if __debug__:
            self.do_disassembly_test(bug1333982, dis_bug1333982)

    def test_big_linenos(self):
        def func(count):
            namespace = {}
            func = "def foo():\n " + "".join(["\n "] * count + ["spam\n"])
            exec func in namespace
            return namespace['foo']

        # Test all small ranges
        for i in xrange(1, 300):
            expected = _BIG_LINENO_FORMAT % (i + 2)
            self.do_disassembly_test(func(i), expected)

        # Test some larger ranges too
        for i in xrange(300, 5000, 10):
            expected = _BIG_LINENO_FORMAT % (i + 2)
            self.do_disassembly_test(func(i), expected)