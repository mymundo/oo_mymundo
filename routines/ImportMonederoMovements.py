# Oct/09 - MS
from OpenOrange import *
from Routine import Routine
from PersonalTrans import PersonalTrans,PersonalTransConceptRow,PersonalTransPaymentRow
from GlobalTools import *

class ImportMonederoMovements(Routine):

    def run(self):
        record = self.getRecord()
        
        fname = getOpenFileName(tr("Select File"))

        ofile = open(fname,"r")

        counter = 0
        for fline in ofile.readlines():
            flist = fline.split("\t")
            transdate = flist[0][0:11]
            transtime = flist[0][11:20].strip()
            comment = "%s %s" %(flist[1],flist[2])
            amount = float(flist[3])
            if (amount < 0):
                comment = "Consumo - %s" %(comment)
            else:
                comment = "Recarga - %s" %(comment)
            ptrans = PersonalTrans()
            ptrans.defaults()
            ptrans.TransDate = transdate
            ptrans.TransTime = transtime
            ptrans.SupCode = record.SupCode
            ptrans.pasteSupCode()
            ptrans.Person = getMasterRecordField("Wallet","Owner",record.Wallet)
            if (amount < 0):
                ptrans.Type = 1
            else:
                ptrans.Type = 0
            ptrans.Description = comment

            amount = abs(amount)
            ptcrow = PersonalTransConceptRow()
            ptcrow.Concept = record.Concept
            ptcrow.pasteConcept(ptrans)
            ptcrow.Qty = 1
            ptcrow.Price = amount
            ptcrow.pastePrice(ptrans)
            ptrans.Concepts.append(ptcrow)
            
            ptprow = PersonalTransPaymentRow()
            ptprow.Wallet = record.Wallet
            ptprow.pasteWallet(ptrans)
            ptprow.Amount = amount
            ptrans.Payments.append(ptprow)
            
            ptrans.sumUp()

            res = ptrans.save()
            if (not res):
                message(res)
                return False
            else:
                counter += 1
        message("%s movimientos importados" %(counter))
        commit()


