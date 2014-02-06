# Oct/09 - MS
from OpenOrange import *
from Report import Report
from GlobalTools import *

class WalletStatus(Report):

    def run(self):
        record = self.getRecord()

        #self.setAutoRefresh(10000)

        if (hasattr(self,"isFirstLine")):
            delattr(self,"isFirstLine")
        self.printReportTitle("Wallet Status")

        tquery = Query()
        tquery.sql  = "SELECT * FROM ( "
        tquery.sql += "SELECT NULL TransDate, NULL TransTime, NULL SerNr, PT.Type, PT.Concept, 'SALDO INICIAL' TransDescription, "
        tquery.sql += "PTPr.Wallet, PTPr.Description, "
        tquery.sql += "SUM((CASE PT.Type "
        tquery.sql += " WHEN i|0| THEN PTPr.Amount "
        tquery.sql += " WHEN i|1| THEN 0.0 "
        tquery.sql += " WHEN i|2| THEN 0.0 "
        tquery.sql += "END)) InAmount, "
        tquery.sql += "SUM((CASE PT.Type "
        tquery.sql += " WHEN i|0| THEN 0.0 "
        tquery.sql += " WHEN i|1| THEN PTPr.Amount "
        tquery.sql += " WHEN i|2| THEN PTPr.Amount "
        tquery.sql += "END)) OutAmount "
        tquery.sql += "FROM PersonalTransPaymentRow PTPr " 
        tquery.sql += "INNER JOIN PersonalTrans PT ON PTPr.masterId = PT.internalId " 
        tquery.sql += "INNER JOIN Wallet W ON PTPr.Wallet = W.Code " 
        tquery.sql += "WHERE?AND (PT.TransDate < d|%s| ) "  %(record.FromDate)
        tquery.sql += "WHERE?AND (PT.Status = i|1|) "
        if (record.Wallet):
            tquery.sql += "WHERE?AND PTPr.Wallet = s|%s| " %(record.Wallet)
        if (record.Owner):
            tquery.sql += "WHERE?AND W.Owner = s|%s| " %(record.Owner)
        tquery.sql += "GROUP BY PTPr.Wallet " 
        tquery.sql += " UNION ALL  "
        tquery.sql += "SELECT PT.TransDate, PT.TransTime, PT.SerNr, PT.Type, PT.Concept, PT.Description TransDescription, "
        tquery.sql += "PTPr.Wallet, PTPr.Description, "
        tquery.sql += "(CASE PT.Type "
        tquery.sql += " WHEN i|0| THEN PTPr.Amount "
        tquery.sql += " WHEN i|1| THEN 0.0 "
        tquery.sql += " WHEN i|2| THEN 0.0 "
        tquery.sql += "END ) InAmount, "
        tquery.sql += "(CASE PT.Type "
        tquery.sql += " WHEN i|0| THEN 0.0 "
        tquery.sql += " WHEN i|1| THEN PTPr.Amount "
        tquery.sql += " WHEN i|2| THEN PTPr.Amount "
        tquery.sql += "END ) OutAmount "
        tquery.sql += "FROM PersonalTransPaymentRow PTPr " 
        tquery.sql += "INNER JOIN PersonalTrans PT ON PTPr.masterId = PT.internalId " 
        tquery.sql += "INNER JOIN Wallet W ON PTPr.Wallet = W.Code " 
        tquery.sql += "WHERE?AND (PT.TransDate BETWEEN d|%s| AND d|%s|) "  %(record.FromDate,record.ToDate)
        tquery.sql += "WHERE?AND (PT.Status = i|1|) "
        if (record.Wallet):
            tquery.sql += "WHERE?AND PTPr.Wallet = s|%s| " %(record.Wallet)
        if (record.Owner):
            tquery.sql += "WHERE?AND W.Owner = s|%s| " %(record.Owner)
        tquery.sql += ") AS T1 "
        tquery.sql += "ORDER BY T1.Wallet, T1.TransDate, T1.TransTime " 

        log(tquery.sql)
        if (tquery.open()):
            self.startTable()
            
            lastw = ""
            balance = 0
            for tline in tquery:
                if (lastw != tline.Wallet):
                    self.doWalletClose(lastw,balance)
                    self.blankRow()
                    self.startRow(Style="B")
                    self.addValue(tline.Wallet)
                    self.addValue(tline.Description,ColSpan="6")
                    self.endRow()

                    self.startRow(Style="A")
                    self.addValue(tr("Date"))
                    self.addValue(tr("Time"))
                    self.addValue(tr("Transaction"))
                    self.addValue(tr("Description"))
                    self.addValue(tr("Income"))
                    self.addValue(tr("Purchase"))
                    self.addValue(tr("Balance"))
                    self.endRow()
                    lastw = tline.Wallet
                    balance = 0
                self.startRow()
                if (not tline.fields("TransDate").isNone()):
                    self.addValue(tline.TransDate.strftime("%d/%m/%Y"))
                else:
                    self.addValue("")
                self.addValue(tline.TransTime)
                self.addValue(tline.SerNr,Window="PersonalTransWindow",FieldName="SerNr")
                self.addValue(tline.TransDescription)
                self.addValue(tline.InAmount)
                self.addValue(tline.OutAmount)
                balance += tline.InAmount - tline.OutAmount
                self.addValue(balance)
                self.endRow()
            self.doWalletClose(lastw,balance)
            self.endTable()

    def doWalletClose(self, lastw, balance):
        if (not hasattr(self,"isFirstLine")):
            self.isFirstLine = True
        if (not self.isFirstLine):
            self.startRow(Style="A")
            self.addValue(tr("Balance"),ColSpan="6",Align="right")
            self.addValue(balance)
            self.endRow()
            
            self.startRow()
            self.addValue(tr("New"),CallMethod="genPersonalTrans",Parameter="%s" %(lastw),ColSpan="2",Color="blue")
            self.endRow()

        if (self.isFirstLine):
            self.isFirstLine = False

    def genPersonalTrans(self, param, value):
        record = self.getRecord()
        from Wallet import Wallet
        wall = Wallet.bring(param)
        if (wall):
            from PersonalTrans import PersonalTrans, PersonalTransPaymentRow
            ptrans = PersonalTrans()
            ptrans.defaults()
            ptrans.TransDate = record.FromDate
            ptrans.Person = wall.Owner
            paymentrow = PersonalTransPaymentRow()
            paymentrow.Wallet = wall.Code
            paymentrow.pasteWallet(ptrans)
            ptrans.Payments.append(paymentrow)
            openWindow(ptrans)