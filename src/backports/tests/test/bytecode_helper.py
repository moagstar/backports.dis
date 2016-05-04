"""bytecode_helper - support tools for testing correct bytecode generation"""

import unittest
import backports.dis as dis
import StringIO
import re


_UNSPECIFIED = object()


class BytecodeTestCase(unittest.TestCase):
    """Custom assertion methods for inspecting bytecode."""

    def get_disassembly_as_string(self, co):
        s = StringIO.StringIO()
        dis.dis(co, file=s)
        return s.getvalue()

    def assertInBytecode(self, x, opname, argval=_UNSPECIFIED):
        """Returns instr if op is found, otherwise throws AssertionError"""
        for instr in dis.get_instructions(x):
            if instr.opname == opname:
                if argval is _UNSPECIFIED or instr.argval == argval:
                    return instr
        disassembly = self.get_disassembly_as_string(x)
        if argval is _UNSPECIFIED:
            msg = '%s not found in bytecode:\n%s' % (opname, disassembly)
        else:
            msg = '(%s,%r) not found in bytecode:\n%s'
            msg = msg % (opname, argval, disassembly)
        self.fail(msg)

    def assertNotInBytecode(self, x, opname, argval=_UNSPECIFIED):
        """Throws AssertionError if op is found"""
        for instr in dis.get_instructions(x):
            if instr.opname == opname:
                disassembly = self.get_disassembly_as_string(x)
                if argval is _UNSPECIFIED:
                    msg = '%s occurs in bytecode:\n%s' % (opname, disassembly)
                elif instr.argval == argval:
                    msg = '(%s,%r) occurs in bytecode:\n%s'
                    msg = msg % (opname, argval, disassembly)
                self.fail(msg)

    def assertRegex(self, text, expected_regex, msg=None):
        """Fail the test unless the text matches the regular expression."""
        if isinstance(expected_regex, (str, bytes)):
            assert expected_regex, "expected_regex must not be empty."
            expected_regex = re.compile(expected_regex)
        if not expected_regex.search(text):
            standardMsg = "Regex didn't match: %r not found in %r" % (
                expected_regex.pattern, text)
            # _formatMessage ensures the longMessage option is respected
            msg = self._formatMessage(msg, standardMsg)
            raise self.failureException(msg)