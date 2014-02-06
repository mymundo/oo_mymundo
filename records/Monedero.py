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

    def checkDetailRows(self):
        for row in self.Detail:
            rquery = Query()
            rquery.sql  = "SELECT COUNT(MDr.internalId) Cnt, MDr.rowNr, M.SerNr  FROM MonederoDetailRow MDr "
            rquery.sql += "INNER JOIN Monedero M ON MDr.masterId = M.internalId "
            rquery.sql += "WHERE?AND (MDr.Date = d|%s| " %(row.Date)
            rquery.sql += "AND MDr.Time = t|%s| " %(row.Time)
            rquery.sql += "AND Station = s|%s|) " %(row.Station)
            rquery.sql += "AND MDr.internalId <> i|%s| " %(row.internalId)
            rquery.sql += "AND M.Wallet = s|%s| " %(self.Wallet) 
            rquery.sql += "AND M.SerNr <> i|%s| " %(self.SerNr)

            if (rquery.open() and rquery[0].Cnt > 0):
                mstring = "%s. %s %s, %s %s" %(tr("RECORDALREADYEXISTS"),tr("Number"),rquery[0].SerNr,tr("Row"),rquery[0].rowNr+1)
                return row.FieldErrorResponse(mstring,"Station")
        return True

    def checkDupDetailRows(self):
        curlist = {}
        for row in self.Detail:
            rstring = "%s%s%s" %(row.Date,row.Time,row.Station)
            if (rstring in curlist.keys()):
                mstring = "%s. %s %s" %(tr("RECORDALREADYEXISTS"),tr("Row"),curlist[rstring]+1)
                return row.FieldErrorResponse(mstring,"Station")
            curlist[rstring] = row.rowNr
        return True

    def check(self):
        res = ParentMonedero.check(self)
        if (not res): return res
        res = self.checkDupDetailRows()
        if (not res): return res
        res = self.checkDetailRows()
        if (not res): return res
        return res

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
        