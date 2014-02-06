# Oct/09 - MS
from OpenOrange import *
from Routine import Routine

class BankStatementImport(Routine):

    def run(self):
        record = self.getRecord()

        ofile = open(record.Filename,"r")
        flines = ofile.readlines()
        for ln in range(12,len(flines)):
            cline = flines[ln]
            col1 = (0,10)
            col2 = (16,71)
            col3 = (71,84)
            col4 = (84,105)
            col5 = (105,128)
            transdate = stringToDate(cline[col1[0]:col1[1]])
            if (transdate >= record.FromDate and transdate <= record.ToDate):
                #comment = cline[16:114].strip()
                #debit = float(cline[114:130].replace(".","").replace(",","."))
                #credit = float(cline[131:154].replace(".","").replace(",","."))
                
                comment = cline[col2[0]:col2[1]].strip()
                debit = float(cline[col3[0]:col3[1]].replace(".","").replace(",","."))
                credit = float(cline[col4[0]:col4[1]].replace(".","").replace(",","."))
                
                print transdate,comment,debit,credit

                from PersonalTrans import PersonalTrans, PersonalTransConceptRow, PersonalTransPaymentRow
                ptrans = PersonalTrans()
                ptrans.defaults()
                ptrans.TransDate = transdate
                ptrans.Description = comment
                if (debit > 0):
                    ptrans.Type = ptrans.EXPENSE
                    amount = debit
                else:
                    ptrans.Type = ptrans.INCOME
                    amount = credit
                if ("EXTRACCION POR CAJEROS AUTOMATICOS" in comment):
                    ptrans.Type = ptrans.TRANSFERENCE
                
                ptrans.SupCode = "0004"
                ptrans.pasteSupCode()
                from Wallet import Wallet
                person = Wallet.bring(record.Wallet).Owner
                ptrans.Person = person
                
                drow = PersonalTransConceptRow()
                drow.Concept = "VARIOS"
                drow.pasteConcept(ptrans)
                drow.Qty = 1
                drow.Price = amount
                drow.pastePrice(ptrans)

                ptrans.Concepts.append(drow)

                prow = PersonalTransPaymentRow()
                prow.Wallet = record.Wallet
                prow.pasteWallet(ptrans)
                prow.Amount = amount

                ptrans.Payments.append(prow)

                ptrans.sumUp()
                res = ptrans.save()
                if (not res): 
                    message(res)
                else:
                    commit()
