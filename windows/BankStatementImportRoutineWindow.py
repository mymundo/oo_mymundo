# Oct/09 - MS
from OpenOrange import *

ParentBankStatementImportRoutineWindow = SuperClass("BankStatementImportRoutineWindow","RoutineWindow",__file__)
class BankStatementImportRoutineWindow(ParentBankStatementImportRoutineWindow):

    def buttonClicked(self, bname):
        record = self.getRecord()
        if (bname == "selectSourceFile"):
            fname = getOpenFileName(tr("Select"))
            if (fname):
                record.Filename = fname
