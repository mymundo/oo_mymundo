from OpenOrange import *
from GlobalTools import *

ParentMonederoWindow = SuperClass("MonederoWindow","NumerableWindow",__file__)
class MonederoWindow(ParentMonederoWindow):
    
    def afterEdit(self, fname):
        afterEdit(self, fname)

    def afterEditRow(self, fname, rfname, rownr):
        afterEditRow(self, fname, rfname, rownr)
    
    def genPersonalTrans(self):
        record = self.getRecord()
        res = record.genPersonalTrans()
        if (res):
            res = record.save()
            if (res):
                commit()
                record.refresh()
