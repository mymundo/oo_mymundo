from OpenOrange import *

ParentMonedero = SuperClass("Monedero","Numerable",__file__)
class Monedero(ParentMonedero):

    def genPersonalTrans(self):
        from PersonalTrans import *
        for row in self.Detail:
            ptrans = PersonalTrans()
            ptrans.defaults()
            ptrans.TransDate = row.Date
            ptrans.TransTime = row.Time
            ptrans.Type = ptrans.EXPENSE
            ptrans.OriginType = 9001
            ptrans.OriginNr = self.SerNr
            from Wallet import Wallet
            wal = Wallet.bring(self.Wallet)
            if (wal):
                ptrans.Person = wal.Owner
            ptrans.Description = "Viaje en Subte - %s" %(row.Station)

            crow = PersonalTransConceptRow()
            crow.Concept = "TRANSP"
            crow.pasteConcept(ptrans)
            crow.Qty = 1
            crow.Price = 1.10
            crow.pastePrice(ptrans)

            ptrans.Concepts.append(crow)

            prow = PersonalTransPaymentRow()
            prow.Wallet = self.Wallet
            prow.pasteWallet(ptrans)
            prow.Amount = 1.10

            ptrans.Payments.append(prow)
            ptrans.Status = 1
            ptrans.sumUp()
            res = ptrans.save()
            if (res):
                row.Processed = True
                commit()
        return True

ParentMonederoDetailRow = SuperClass("MonederoDetailRow","Record",__file__)
class MonederoDetailRow(ParentMonederoDetailRow):
    
    def pasteStation(self, record):
        squery = Query()
        squery.sql  = "SELECT Code FROM SubteStation "
        squery.sql += "WHERE?AND lower(Code) LIKE lower('%s%%') " %(self.Station)
        squery.sql += "ORDER BY Code " 

        if (squery.open()):
            if (squery.count() > 0):
                self.Station = squery[0].Code
        