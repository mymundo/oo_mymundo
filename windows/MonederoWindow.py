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

    def activateNextCell(self, matrixname, row, col):
        columns = self.getMatrixColumns(matrixname)
        if matrixname == "DetailMatrix":
            if columns[col] == "Station": # To Next Row
                col = 0
                row += 1
            else:
                row,col = getNextCol(columns,row,col,"")
        else:
            row,col = getNextCol(columns,row,col,"")
        return (row,col)