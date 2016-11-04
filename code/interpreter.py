#!/usr/bin/python

import os.path
from code.enum import Enum as Enum
from code.exceptions import SyntaxException as SyntaxException
from code.token import Token as Token
from code.stack import Stack as Stack

# The interpreter takes an input file and can:
#   check the syntax of the expression and
#   evaluate the value of the expression
class Interpreter(object):
    def __init__(self, path):
        """
        Interpreter initialization
        """

        self.content = None
        self.pos = 0
        self.lex = None
        self.stack = Stack()

        if os.path.isfile(path):
            with open(path, 'r') as f:
                self.content = f.read()
        else:
            self.error("File not found.")

    def error(self, error=""):
        """
        Raises an error. Refers to the (optional) error
        and the current position of the pointer
        """

        raise SyntaxException(
            'Error parsing input. {0}\r\n\tPosition: {1}'.format(
                error,
                self.pos
            )
        )

    def skip(self):
        """
        Skips to the next token
        """

        self.pos += 1
        return self.get()

    def get(self):
        """
        Breaks the file content into tokens. One token at a time.
        """

        content = self.content

        # If the position of the pointer is past the end of the file,
        # then return an EOF token
        if self.pos > len(content) - 1:
            return Token(Enum.EOF, None)

        # Get the character at the position
        current = content[self.pos]

        # If the current character is {T,F},
        # then return a BOOL token
        if current in {"T", "F"}:
            self.pos += 1
            return Token(Enum.BOOL, current)

        # If the current is a "-" THEN ">",
        # then return an IMPLY token
        if current == "-":
            value = current
            self.pos += 1
            current = content[self.pos]

            if current == ">":
                self.pos += 1
                return Token(Enum.IMPLY, value + current)
            else:
                self.error("The character '-' must be followed by a '>'")

        # If the current character is "v",
        # then return an OR token
        if current == "v":
            self.pos += 1
            return Token(Enum.OR, current)

        # If the current character is "^",
        # then return an AND token
        if current == "^":
            self.pos += 1
            return Token(Enum.AND, current)

        # If the current character is "~",
        # then return a NOT token
        if current == "~":
            self.pos += 1
            return Token(Enum.NOT, current)

        # If the current character is {" ", "\n", "\r", "\t"},
        # then skip the space
        if current.isspace() or current in {"\n", "\r", "\t"}:
            #self.pos += 1
            #return Token(Enum.WHITESPACE, current)
            return self.skip()

        # If the current character is ".",
        # then return a PERIOD token
        if current == ".":
            self.pos += 1
            return Token(Enum.PERIOD, current)

        # If the current character is "(",
        # then return an OPEN_PAREN token
        if current == "(":
            self.pos += 1
            return Token(Enum.OPEN_PAREN, current)

        # If the current character is ")",
        # then return an CLOSED_PAREN token
        if current == ")":
            self.pos += 1
            return Token(Enum.CLOSED_PAREN, current)

        self.error("The character '{0}' is an invalid character".format(current))

    def is_valid(self):
        """
        Checks if the syntax is valid
        """

        self.pos = 0
        self.lex = self.get()
        del self.stack.items[:]
        isValid = False

        try:
            isValid = self.B()
        except Exception as e:
            print(e)

        return isValid

    def eval(self):
        """
        Evaluate the value of the given expression
        """

        val = None

        if self.is_valid():
            # The final value is stored at the top of the stack
            val = self.stack.pop()

        return val

    def B(self):
        """
        Evalute the expression <B>
        """

        if self.IT():
            if self.lex.type == Enum.PERIOD:
                self.lex = self.get()
                return True
            else:
                self.error("Expected a '.', received '{0}'".format(self.lex.value))

        return False

    def IT(self):
        """
        Evaulate the expression <IT>
        """

        if self.OT():
            return self.IT_Tail()

        return False

    def IT_Tail(self):
        """
        Evaluate the expression <IT_Tail>
        """

        # For the empty set, check the selection set
        if self.lex.type in {Enum.PERIOD, Enum.OPEN_PAREN}:
            return True

        if self.lex.type == Enum.IMPLY:
            self.lex = self.get()
            if self.OT():
                valR = self.stack.pop()
                valL = self.stack.pop()
                self.stack.push("F" if (valL == "T" and valR == "F") else "T")
                return self.IT_Tail()
        elif self.lex.type in {Enum.PERIOD, Enum.CLOSED_PAREN}:
            return True
        else:
            self.error("Expected a '->', '.', '(', or ')';"
                       " received '{0}'".format(self.lex.value))

        return False

    def OT(self):
        """
        Evaluate the expression <OT>
        """

        if self.AT():
            return self.OT_Tail()

        return False

    def OT_Tail(self):
        """
        Evaluate the expression <OT_Tail>
        """

        # For the empty set, check the selection set
        if self.lex.type in {Enum.IMPLY, Enum.PERIOD, Enum.CLOSED_PAREN}:
            return True

        if self.lex.type == Enum.OR:
            self.lex = self.get()
            if self.AT():
                # Pop the top 2 values off the stack,
                # then push the result of the values ORed together
                #   T = T OR T = T OR F = F OR T
                #   F = F OR F
                val0 = self.stack.pop()
                val1 = self.stack.pop()
                self.stack.push("T" if (val0 == "T" or val1 == "T") else "F")
                return self.OT_Tail()
        else:
            self.error("Expected a '->', '.', ')', or 'v'; received '{0}'".format(self.lex.value))

        return False

    def AT(self):
        """
        Evaluate the expression <AT>
        """

        if self.L():
            return self.AT_Tail()

        return False

    def AT_Tail(self):
        """
        Evaluate the expression <AT_Tail>
        """

        # For the empty set, check the selection set
        if self.lex.type in {Enum.OR, Enum.IMPLY, Enum.PERIOD, Enum.CLOSED_PAREN}:
            return True

        if self.lex.type == Enum.AND:
            self.lex = self.get()
            if self.L():
                # Pop the top 2 values off the stack,
                # then push the result of the values ANDed together
                #   T = T AND T
                #   F = F AND F = T AND F = F AND T
                val0 = self.stack.pop()
                val1 = self.stack.pop()
                self.stack.push("T" if (val0 == "T" and val1 == "T") else "F")
                return self.AT_Tail()
        else:
            self.error("Expected a 'v', '->', '.', ')', or '^'; received '{0}'".format(self.lex.value))

        return False

    def L(self):
        """
        Evaluate the expression <L>
        """

        if self.lex.type == Enum.NOT:
            self.lex = self.get()
            if self.L():
                # Pop the top value off the stack,
                # then flip the value
                #   T = ~F
                #   F = ~T
                val = self.stack.pop()
                self.stack.push("F" if val == "T" else "T")
                return True

        return self.A()

    def A(self):
        """
        Evaluate the expression <A>
        """

        if self.lex.type == Enum.BOOL:
            # Push the atom {"T", "F"} to the stack
            self.stack.push(self.lex.value)
            self.lex = self.get()
            return True
        elif self.lex.type == Enum.OPEN_PAREN:
            self.lex = self.get()
            if self.IT():
                if self.lex.type == Enum.CLOSED_PAREN:
                    self.lex = self.get()
                    return True
                else:
                    self.error("Expected a ')', received {0}".format(self.lex.value))
            else:
                self.error("IT term required after '('")

        self.error("Expected a '~', 'T', 'F', or '('; received '{0}'".format(self.lex.value))
