#!/usr/bin/python

# The token takes a type and value.
class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """
        String representation of the Token class.
        """

        return "Token({type}, {value})".format(
            type = self.type,
            value = repr(self.value)
        )

    def __repr__(self):
        return self.__str__()
