# Oct/09 - MS
from OpenOrange import *
from GlobalTools import *

ParentPersonalTransWindow = SuperClass("PersonalTransWindow","FinancialTransWindow",__file__)
class PersonalTransWindow(ParentPersonalTransWindow):

    def afterEdit(self, fieldname):
        afterEdit(self, fieldname)

    def afterEditRow(self, fname, rfname, rownr):
        afterEditRow(self, fname, rfname, rownr)
        record = self.getRecord()
        if (fname == "Concepts"):
            if (rfname in ("Price","Qty","RowTotal")):
                row = record.Concepts[rownr]
                row.sumUp(record)
                record.sumUp()
            elif (rfname == "ArtCode"):
                row = record.Concepts[rownr]
                if (row.ArtCode):
                    from Item import Item
                    itm = Item.bring(row.ArtCode)
                    if (not itm):
                        #Codigo
                        res = getString("Artículo Inexistente, Ingrese Codigo")
                        if (not res): return
                        if (len(res) != 13):
                            if (not " " in res):
                                message("Codigo Inválido")
                                return
                            prefix,code = res.split(" ")
                            icode = prefix+code.rjust(12,"0")
                        else:
                            icode = res
                        #Descripcion
                        res = getString("Ingrese Descripción")
                        if (not res): return
                        iname = res
                        #Grupo
                        gquery = Query()
                        gquery.sql  = "SELECT * FROM ItemGroup ORDER BY Name "
                        if (gquery.open()):
                            glist = []
                            for gline in gquery:
                                glist.append("%s:%s" %(gline.Name,gline.Code))
                            res = getSelection("Grupo de Articulos", tuple(glist))
                            if (not res): return
                            igroup = res.split(":")[1]
                        #Unidad de Medida
                        uquery = Query()
                        uquery.sql  = "SELECT * FROM Unit ORDER BY Name "
                        if (uquery.open()):
                            ulist = []
                            for uline in uquery:
                                ulist.append("%s:%s" %(uline.Name,uline.Code))
                            res = getSelection("Unidad de Medida", tuple(ulist))
                            if (not res): return
                            iunit = res.split(":")[1]
                        #Precio
                        res = getString("Precio")
                        if (not res): return res
                        iprice = float(res)
                        ###
                        itm = Item()
                        itm.Code = icode
                        itm.Name = iname
                        itm.ItemGroup = igroup
                        itm.Unit = iunit
                        res = itm.save()
                        if (not res): 
                            message("No se pudo crear Artículo. %s" %(res))
                            return res
                        else:
                            commit()
                        icost = itm.getItemCost()
                        icost.SubCost = iprice
                        res = icost.save()
                        if (not res):
                            message("No se pudo crear Costo de Artículo. %s" %(res))
                            return res
                        else:
                            commit()
                        row.ArtCode = icode
                        row.pasteArtCode(record)


        elif (fname == "Payments"):
            row = record.Payments[rownr]
            if (rfname in ("Amount")):
                record.sumUp()

#    def filterPasteWindow(self, fname):
#        res = ParentPersonalTransWindow.filterPasteWindow(self, fname)
#        if fname == "Concept":
#            if (res):
#                res += " AND "
#            else:
#                res = ""
#            res += "{IsGeneric} = i|1|"
#        return res

    def filterPasteWindowRow(self, fname, rfname,rownr):
        res = ParentPersonalTransWindow.filterPasteWindowRow(self, fname, rfname,rownr)
        record = self.getRecord()
        if (fname == "Concepts"):
            if (rfname == "Concept"):
                if (res):
                    res += " AND "
                else:
                    res = ""
                res += " Type = i|%s| " %(record.Type)
        elif (fname == "Payments"):
            if (rfname == "Wallet"):
                if (res):
                    res += " AND "
                else:
                    res = ""
                res += "{Owner} = s|%s| " %(record.Person)
        return res

    def afterDeleteRow(self, dname, rownr):
        ParentPersonalTransWindow.afterDeleteRow(self, dname, rownr)
        if (dname in ("Concepts","Payments")):
            self.getRecord().sumUp()
