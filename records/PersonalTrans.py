# Oct/09 - MS
from OpenOrange import *
from GlobalTools import *

ParentPersonalTrans = SuperClass("PersonalTrans","FinancialTrans",__file__)
class PersonalTrans(ParentPersonalTrans):

    def defaults(self):
        ParentPersonalTrans.defaults(self)
        self.Person = getMasterRecordField("User","Person",self.User)
        self.Type = 1

    def pasteSupCode(self):
        self.SupName = getMasterRecordField("Supplier","Name",self.SupCode)

#    def pasteConcept(self):
#        self.Description = getMasterRecordField("Concept","Description",self.Concept)
#        self.Type = getMasterRecordField("Concept","Type",self.Concept)

    def sumUp(self):
        ctotal = 0
        ptotal = 0
        for cline in self.Concepts:
            ctotal += cline.RowTotal
        for pline in self.Payments:
            ptotal += pline.Amount
        self.TotalConcepts = self.roundValue(ctotal,"TotalConcepts")
        self.TotalPayments = self.roundValue(ptotal,"TotalPayments")

    def checkConceptRows(self):
        for cline in self.Concepts:
            if (not cline.Price):
                return cline.FieldErrorResponse("NONBLANKERR","Price")
            #if (cline.Price < 0):
            #    return cline.FieldErrorResponse("Negative Values No Allowed","Price")
            if (cline.Qty < 0):
                return cline.FieldErrorResponse("Negative Values No Allowed","Qty")
        return True

    def checkPaymentRows(self):
        for pline in self.Payments:
            if (not pline.Amount):
                return pline.FieldErrorResponse("NONBLANKERR","Amount")
            #if (pline.Amount < 0):
            #    return pline.FieldErrorResponse("Negative Values No Allowed","Amount")
        return True

    def check(self):
        res = ParentPersonalTrans.check(self)
        if (not res): return res
        res = self.checkConceptRows()
        if (not res): return res
        res = self.checkPaymentRows()
        if (not res): return res
        if (self.confirming()):
            if (self.Type == 2):
                if (not self.TransferTo):
                    res = self.FieldErrorResponse("NONBLANKERR","TransferTo")
            if (self.TotalConcepts != self.TotalPayments):
                res = self.FieldErrorResponse("NONBLANKERR","Person")
                try:
                    res = self.Concepts[0].FieldErrorResponse("NOBALANCEERR","Concept")
                except:
                    return res
        return res

    def afterInsert(self):
        res = ParentPersonalTrans.afterInsert(self)
        if not res: return res
        if (self.Type == 2  and (self.confirming() or self.unconfirming())):
            res = self.genTransference(self.unconfirming())
            if (not res): return res
        return res

    def afterUpdate(self):
        res = ParentPersonalTrans.afterUpdate(self)
        if (not res): return res
        if (self.Type == 2 and (self.confirming() or self.unconfirming())):
            res = self.genTransference(self.unconfirming())
            if (not res): return res
        return res

    def genTransference(self, revert):
        if (not revert):
            trans = self.clone()
            trans.SerNr = None
            trans.ToSerNr = None
            person = getMasterRecordField("Wallet","Owner",self.TransferTo)
            trans.Person = person
            trans.TransferTo = None
            trans.Type = 0
            trans.Payments.clear()
            prow = PersonalTransPaymentRow()
            prow.Wallet = self.TransferTo
            prow.pasteWallet(trans)
            prow.Amount = self.TotalPayments
            trans.Payments.append(prow)
            trans.OriginNr = self.SerNr
            trans.OriginType = 9000
            res = trans.save()
        else:
            trans = PersonalTrans()
            trans.OriginNr = self.SerNr
            trans.OriginType = 9000
            if (trans.load()):
                res = trans.forceDelete()
        return res

ParentPersonalTransConceptRow = SuperClass("PersonalTransConceptRow","Record",__file__)
class PersonalTransConceptRow(ParentPersonalTransConceptRow):

    def sumUp(self, record):
        self.RowTotal = self.Qty * self.Price
        self.RowTotal = record.roundValue(self.RowTotal,"Concepts","RowTotal")

    def pasteConcept(self, record):
        self.Description = getMasterRecordField("Concept","Description",self.Concept)

    def pasteArtCode(self, record):
        from Item import Item
        itm = Item.bring(self.ArtCode)
        if (itm):
            self.Description = itm.Name
            self.Price = itm.getCost()

    def pastePrice(self, record):
        self.RowTotal = self.Qty * self.Price

ParentPersonalTransPaymentRow = SuperClass("PersonalTransPaymentRow","Record",__file__)
class PersonalTransPaymentRow(ParentPersonalTransPaymentRow):

    def pasteWallet(self, record):
        self.Description = getMasterRecordField("Wallet","Description",self.Wallet)