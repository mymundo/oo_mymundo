# Oct/09 - MS
from OpenOrange import *

ParentConcept = SuperClass("Concept","Master",__file__)
class Concept(ParentConcept):
    buffer = RecordBuffer("Concept")

    def defaults(self):
        ParentConcept.defaults(self)
        self.Type = 0

    def check(self):
        res = ParentConcept.check(self)
        if (not res): return res
        if (not self.Description):
            return self.FieldErrorResponse("NONBLANKERR","Description")
        if (not self.Account):
            return self.FieldErrorResponse("NONBLANKERR","Account")
        return res