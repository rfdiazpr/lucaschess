import os
import time
import shutil

from PyQt4 import QtGui, QtCore

import Code.VarGen as VarGen
import Code.Util as Util
import Code.STS as STS
import Code.ControlPosicion as ControlPosicion
import Code.QT.QTUtil as QTUtil
import Code.QT.QTUtil2 as QTUtil2
import Code.QT.QTVarios as QTVarios
import Code.QT.Colocacion as Colocacion
import Code.QT.Iconos as Iconos
import Code.QT.Controles as Controles
import Code.QT.PantallaMotores as PantallaMotores
import Code.QT.Columnas as Columnas
import Code.QT.Grid as Grid
import Code.QT.FormLayout as FormLayout
import Code.QT.Tablero as Tablero

class WRun(QTVarios.WDialogo):
    def __init__(self, wParent, sts, work, procesador):
        titulo = "%s - %s" % (sts.name, work.ref)
        icono = Iconos.STS()
        extparam = "runsts"
        QTVarios.WDialogo.__init__(self, wParent, titulo, icono, extparam)

        self.work = work
        self.sts = sts
        self.xengine = procesador.creaGestorMotor(work.configEngine(), work.seconds*1000, work.depth)
        self.playing = False
        self.configuracion = procesador.configuracion
        dic = self.configuracion.leeVariables("STSRUN")
        self.hideBoard = dic["HIDEBOARD"] if dic else False

        # Toolbar
        liAcciones = [(_("Close"), Iconos.MainMenu(), self.cerrar), None,
                      (_("Run"), Iconos.Run(), self.run),
                      (_("Pause"), Iconos.Pelicula_Pausa(), self.pause), None,
                      (_("Config"), Iconos.Configurar(), self.config), None,
        ]
        self.tb = tb = Controles.TBrutina(self, liAcciones, tamIcon=24)

        # Board
        confTablero = self.configuracion.confTablero("STS", 32)
        self.tablero = Tablero.Tablero(self, confTablero)
        self.tablero.crea()

        # Area resultados
        oColumnas = Columnas.ListaColumnas()
        oColumnas.nueva("GROUP", _("Group"), 180)
        oColumnas.nueva("DONE", _("Done"), 100, siCentrado=True)
        oColumnas.nueva("RESULT", _("Result"), 150, siCentrado=True)
        self.grid = Grid.Grid(self, oColumnas, siSelecFilas=True)

        # self.splitter = splitter = QtGui.QSplitter(self)
        # splitter.addWidget(self.tablero)
        # splitter.addWidget(self.grid)
        # self.registrarSplitter(splitter,"base")

        layout = Colocacion.H()
        layout.control(self.tablero)
        layout.control(self.grid)
        layout.margen(3)

        ly = Colocacion.V().control(tb).otro(layout)

        self.setLayout(ly)

        self.recuperarVideo(siTam=True, anchoDefecto=800, altoDefecto=430)

        resp = self.sts.siguientePosicion(self.work)
        if resp:
            self.tb.setAccionVisible(self.pause, False)
            self.tb.setAccionVisible(self.run, True)
        else:
            self.tb.setAccionVisible(self.pause, False)
            self.tb.setAccionVisible(self.run, False)

        self.setViewBoard()

    def cerrar(self):
        self.xengine.terminar()
        self.guardarVideo()
        self.playing = False
        self.accept()

    def closeEvent(self, event):
        self.cerrar()

    def config(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion("show", _("Show board") if self.hideBoard else _("Hide board"), Iconos.Camara())
        resp = menu.lanza()
        if resp:
            self.hideBoard = not self.hideBoard
            self.configuracion.escVariables("STSRUN", {"HIDEBOARD": self.hideBoard})
            self.setViewBoard()

    def setViewBoard(self):
        if self.hideBoard:
            self.tablero.hide()
        else:
            self.tablero.show()

    def run(self):
        self.tb.setAccionVisible(self.pause, True)
        self.tb.setAccionVisible(self.run, False)
        self.playing = True
        while self.playing:
            self.siguiente()

    def pause(self):
        self.tb.setAccionVisible(self.pause, False)
        self.tb.setAccionVisible(self.run, True)
        self.playing = False

    def siguiente(self):
        resp = self.sts.siguientePosicion(self.work)
        if resp:
            self.ngroup, self.nfen, self.elem = resp
            if not self.hideBoard:
                cp = ControlPosicion.ControlPosicion()
                cp.leeFen(self.elem.fen)
                self.tablero.ponPosicion(cp)
                self.xengine.ponGuiDispatch(self.dispatch)
                xpt, xa1h8 = self.elem.bestA1H8()
                self.tablero.quitaFlechas()
                self.tablero.creaFlechaTmp(xa1h8[:2], xa1h8[2:], False)
            if not self.playing:
                return
            t0 = time.time()
            mrm = self.xengine.analiza(self.elem.fen)
            t1 = time.time()-t0
            if mrm:
                rm = mrm.mejorMov()
                if rm:
                    mov = rm.movimiento()
                    if mov:
                        if not self.hideBoard:
                            self.tablero.creaFlechaTmp(rm.desde, rm.hasta, True)
                        self.sts.setResult(self.work, self.ngroup, self.nfen, mov, t1)
                        self.grid.refresh()

        else:
            self.tb.setAccionVisible(self.pause, False)
            self.tb.setAccionVisible(self.run, False)
            self.playing = False

        QTUtil.refreshGUI()

    def dispatch(self, rm):
        if rm.desde:
            self.tablero.creaFlechaTmp(rm.desde, rm.hasta, True)
        QTUtil.refreshGUI()
        return self.playing

    def gridNumDatos(self, grid):
        return len(self.sts.groups)

    def gridDato(self, grid, fila, oColumna):
        columna = oColumna.clave
        group = self.sts.groups.group(fila)
        if columna == "GROUP":
            return group.name
        elif columna == "DONE":
            return self.sts.donePositions(self.work, fila)
        elif columna == "RESULT":
            return self.sts.donePoints(self.work, fila)

class WWork(QtGui.QDialog):
    def __init__(self, wParent, sts, work):
        super(WWork, self).__init__(wParent)

        self.work = work

        self.setWindowTitle(sts.name)
        self.setWindowIcon(Iconos.Motor())
        self.setWindowFlags(
            QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)

        tb = QTUtil2.tbAcceptCancel(self)

        # Tabs
        tab = Controles.Tab()

        # Tab-basic --------------------------------------------------
        lbRef = Controles.LB(self, _("Reference") + ": ")
        self.edRef = Controles.ED(self, work.ref).anchoMinimo(360)

        lbInfo = Controles.LB(self, _("Information") + ": ")
        self.emInfo = Controles.EM(self, work.info, siHTML=False).anchoMinimo(360).altoFijo(60)

        lbDepth = Controles.LB(self, _("Maximum depth") + ": ")
        self.sbDepth = Controles.SB(self, work.depth, 0, 50)

        lbSeconds = Controles.LB(self, _("Maximum seconds to think") + ": ")
        self.sbSeconds = Controles.SB(self, work.seconds, 0, 9999)

        lbSample = Controles.LB(self, _("Sample") + ": ")
        self.sbIni = Controles.SB(self, work.ini + 1, 1, 100).capturaCambiado(self.changeSample)
        self.sbIni.isIni = True
        lbGuion = Controles.LB(self, _("to"))
        self.sbEnd = Controles.SB(self, work.end + 1, 1, 100).capturaCambiado(self.changeSample)
        self.sbEnd.isIni = False

        # self.lbError = Controles.LB(self).ponTipoLetra(peso=75).ponColorN("red")
        # self.lbError.hide()

        lySample = Colocacion.H().control(self.sbIni).control(lbGuion).control(self.sbEnd)
        ly = Colocacion.G()
        ly.controld(lbRef, 0, 0).control(self.edRef, 0, 1)
        ly.controld(lbInfo, 1, 0).control(self.emInfo, 1, 1)
        ly.controld(lbDepth, 2, 0).control(self.sbDepth, 2, 1)
        ly.controld(lbSeconds, 3, 0).control(self.sbSeconds, 3, 1)
        ly.controld(lbSample, 4, 0).otro(lySample, 4, 1)

        w = QtGui.QWidget()
        w.setLayout(ly)
        tab.nuevaTab(w, _("Basic data"))

        # Tab-Engine
        scrollArea = PantallaMotores.genOpcionesME(self, work.me)
        tab.nuevaTab(scrollArea, _("Engine options"))

        # Tab-Groups
        btAll = Controles.PB(self, _("All"), self.setAll, plano=False)
        btNone = Controles.PB(self, _("None"), self.setNone, plano=False)
        lyAN = Colocacion.H().control(btAll).espacio(10).control(btNone)
        self.liGroups = []
        ly = Colocacion.G()
        ly.columnaVacia(1, 10)
        fil = 0
        col = 0
        num = len(sts.groups)
        mitad = num / 2 + num % 2

        for x in range(num):
            group = sts.groups.group(x)
            chb = Controles.CHB(self, _F(group.name), work.liGroupActive[x])
            self.liGroups.append(chb)
            col = 0 if x < mitad else 2
            fil = x % mitad

            ly.control(chb, fil, col)
        ly.otroc(lyAN, mitad, 0, numColumnas=3)

        w = QtGui.QWidget()
        w.setLayout(ly)
        tab.nuevaTab(w, _("Groups"))

        layout = Colocacion.V().control(tb).control(tab).margen(8)
        self.setLayout(layout)

        self.edRef.setFocus()

    def changeSample(self):
        vIni = self.sbIni.valor()
        vEnd = self.sbEnd.valor()
        p = self.sender()
        if vEnd < vIni:
            if p.isIni:
                self.sbEnd.ponValor(vIni)
            else:
                self.sbIni.ponValor(vEnd)

    def setAll(self):
        for group in self.liGroups:
            group.ponValor(True)

    def setNone(self):
        for group in self.liGroups:
            group.ponValor(False)

    def aceptar(self):
        self.work.ref = self.edRef.texto()
        self.work.info = self.emInfo.texto()
        self.work.depth = self.sbDepth.valor()
        self.work.seconds = self.sbSeconds.valor()
        self.work.ini = self.sbIni.valor() - 1
        self.work.end = self.sbEnd.valor() - 1
        me = self.work.me
        PantallaMotores.saveOpcionesME(me)
        for n, group in enumerate(self.liGroups):
            self.work.liGroupActive[n] = group.valor()
        self.accept()

class WUnSTS(QTVarios.WDialogo):
    def __init__(self, wParent, sts, procesador):
        titulo = sts.name
        icono = Iconos.STS()
        extparam = "unsts"
        QTVarios.WDialogo.__init__(self, wParent, titulo, icono, extparam)

        # Datos
        self.sts = sts
        self.procesador = procesador

        # Toolbar
        liAcciones = [(_("Close"), Iconos.MainMenu(), self.terminar), None,
                      (_("Run"), Iconos.Run(), self.wkRun), None,
                      (_("New"), Iconos.NuevoMas(), self.wkNew), None,
                      (_("Edit"), Iconos.Modificar(), self.wkEdit), None,
                      (_("Copy"), Iconos.Copiar(), self.wkCopy), None,
                      (_("Remove"), Iconos.Borrar(), self.wkRemove), None,
                      (_("Up"), Iconos.Arriba(), self.up),
                      (_("Down"), Iconos.Abajo(), self.down), None,
                      (_("Export"), Iconos.Grabar(), self.export), None,
                      (_("Config"), Iconos.Configurar(), self.configurar), None,
        ]
        tb = Controles.TBrutina(self, liAcciones, tamIcon=24)

        # # Grid works
        oColumnas = Columnas.ListaColumnas()
        oColumnas.nueva("POS", _("N."), 30, siCentrado=True)
        oColumnas.nueva("REF", _("Reference"), 100)
        oColumnas.nueva("TIME", _("Time"), 50, siCentrado=True)
        oColumnas.nueva("DEPTH", _("Depth"), 50, siCentrado=True)
        oColumnas.nueva("SAMPLE", _("Sample"), 50, siCentrado=True)
        oColumnas.nueva("RESULT", _("Result"), 150, siCentrado=True)
        oColumnas.nueva("ELO", _("Elo"), 80, siCentrado=True)
        oColumnas.nueva("WORKTIME", _("Work time"), 80, siCentrado=True)
        for x in range(len(sts.groups)):
            group = sts.groups.group(x)
            oColumnas.nueva("T%d" % x, group.name, 140, siCentrado=True)
        self.grid = Grid.Grid(self, oColumnas, siSelecFilas=True, siSeleccionMultiple=True)
        self.registrarGrid(self.grid)

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).margen(8)
        self.setLayout(layout)

        self.recuperarVideo(siTam=True, anchoDefecto=800, altoDefecto=430)

        self.grid.gotop()

    def terminar(self):
        self.guardarVideo()
        self.accept()

    def closeEvent(self, event):
        self.guardarVideo()

    def configurar(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion("formula", _("Formula to calculate elo"), Iconos.STS())
        resp = menu.lanza()
        if resp:
            X = self.sts.X
            K = self.sts.K
            while True:
                liGen = [(None, None)]
                liGen.append((None, "X * %s + K" % _("Result")))
                config = FormLayout.Editbox("X", 100, tipo=float, decimales=4)
                liGen.append(( config, X ))
                config = FormLayout.Editbox("K", 100, tipo=float, decimales=4)
                liGen.append(( config, K ))
                resultado = FormLayout.fedit(liGen, title=_("Formula to calculate elo"), parent=self, icon=Iconos.Elo(),
                                             siDefecto=True)
                if resultado:
                    resp, valor = resultado
                    if resp == 'defecto':
                        X = self.sts.Xdefault
                        K = self.sts.Kdefault
                    else:
                        x, k = valor
                        self.sts.formulaChange(x, k)
                        self.grid.refresh()
                        return
                else:
                    return

    def export(self):
        resp = QTUtil2.salvaFichero(self, _("CSV file"), VarGen.configuracion.dirSalvados, _("File") + " csv (*.csv)",
                                    True)
        if resp:
            self.sts.writeCSV(resp)

    def up(self):
        fila = self.grid.recno()
        if self.sts.up(fila):
            self.grid.goto(fila - 1, 0)
            self.grid.refresh()

    def down(self):
        fila = self.grid.recno()
        if self.sts.down(fila):
            self.grid.goto(fila + 1, 0)
            self.grid.refresh()

    def wkRun(self):
        fila = self.grid.recno()
        if fila >= 0:
            work = self.sts.getWork(fila)
            w = WRun(self, self.sts, work, self.procesador)
            w.exec_()

    def wkEdit(self):
        fila = self.grid.recno()
        if fila >= 0:
            work = self.sts.getWork(fila)
            w = WWork(self, self.sts, work)
            if w.exec_():
                self.sts.save()

    def wkNew(self, work=None):
        if work is None:
            me = PantallaMotores.selectEngine(self)
            if not me:
                return
            work = self.sts.createWork(me)

        w = WWork(self, self.sts, work)
        if w.exec_():
            self.sts.addWork(work)
            self.sts.save()
            self.grid.refresh()
            self.grid.gobottom()
        return work

    def wkCopy(self):
        fila = self.grid.recno()
        if fila >= 0:
            work = self.sts.getWork(fila)
            self.wkNew(work.clone())

    def wkRemove(self):
        fila = self.grid.recno()
        if fila >= 0:
            work = self.sts.getWork(fila)
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), work.ref)):
                self.sts.removeWork(fila)
                self.sts.save()
                self.grid.refresh()

    def gridNumDatos(self, grid):
        return len(self.sts.works)

    def gridDato(self, grid, fila, oColumna):
        work = self.sts.works.lista[fila]
        columna = oColumna.clave
        if columna == "POS":
            return str(fila + 1)
        if columna == "REF":
            return work.ref
        if columna == "TIME":
            return str(work.seconds) if work.seconds else "-"
        if columna == "DEPTH":
            return str(work.depth) if work.depth else "-"
        if columna == "SAMPLE":
            return "%d-%d" % (work.ini + 1, work.end + 1)
        if columna == "RESULT":
            return self.sts.allPoints(work)
        if columna == "ELO":
            return self.sts.elo(work)
        if columna == "WORKTIME":
            secs = work.workTime
            if secs == 0.0:
                return "-"
            d = int(secs*10)%10
            s = int(secs)%60
            m = int(secs)//60
            return "%d' %d.%d\""%(m,s,d)
        test = int(columna[1:])
        return self.sts.donePoints(work, test)

    def gridDobleClickCabecera(self, grid, oCol):
        if oCol.clave != "POS":
            self.sts.ordenWorks(oCol.clave)
            self.sts.save()
            self.grid.refresh()
            self.grid.gotop()

class WSTS(QTVarios.WDialogo):
    def __init__(self, wParent, procesador):

        titulo = _("STS: Strategic Test Suite")
        icono = Iconos.STS()
        extparam = "sts"
        QTVarios.WDialogo.__init__(self, wParent, titulo, icono, extparam)

        # Datos
        self.procesador = procesador
        self.carpetaSTS = procesador.configuracion.carpetaSTS
        self.lista = self.leeSTS()

        # Toolbar
        liAcciones = (  (_("Close"), Iconos.MainMenu(), self.terminar),
                        (_("Select"), Iconos.Seleccionar(), self.modificar),
                        (_("New"), Iconos.NuevoMas(), self.crear),
                        (_("Rename"), Iconos.Rename(), self.rename),
                        (_("Copy"), Iconos.Copiar(), self.copiar),
                        (_("Remove"), Iconos.Borrar(), self.borrar),
        )
        tb = Controles.TBrutina(self, liAcciones)
        if len(self.lista) == 0:
            for x in (self.modificar, self.borrar, self.copiar, self.rename):
                tb.setAccionVisible(x, False)

        # grid
        oColumnas = Columnas.ListaColumnas()
        oColumnas.nueva("NOMBRE", _("Name"), 240)
        oColumnas.nueva("FECHA", _("Date"), 120, siCentrado=True)

        self.grid = Grid.Grid(self, oColumnas, siSelecFilas=True)
        self.registrarGrid(self.grid)

        lb = Controles.LB(self,
            '<a href="https://sites.google.com/site/strategictestsuite/about-1">%s</a>  %s: <b>Dan Corbit & Swaminathan</b>' % (
                _("More info"), _("Authors")))

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).control(lb).margen(8)
        self.setLayout(layout)

        self.recuperarVideo(siTam=True, anchoDefecto=400, altoDefecto=500)

        self.grid.gotop()

    def leeSTS(self):
        li = []
        Util.creaCarpeta(self.carpetaSTS)
        for x in Util.listdir(self.carpetaSTS, siUnicode=True):
            if x.lower().endswith(".sts"):
                fich = os.path.join(self.carpetaSTS, x)
                st = os.stat(fich)
                li.append((x, st.st_ctime, st.st_mtime))

        sorted(li, key=lambda x: x[2], reverse=True)  # por ultima modificacin y al reves
        return li

    def gridNumDatos(self, grid):
        return len(self.lista)

    def gridDato(self, grid, fila, oColumna):
        columna = oColumna.clave
        nombre, fcreacion, fmanten = self.lista[fila]
        if columna == "NOMBRE":
            return nombre[:-4]
        elif columna == "FECHA":
            tm = time.localtime(fmanten)
            return "%d-%02d-%d, %2d:%02d" % (tm.tm_mday, tm.tm_mon, tm.tm_year, tm.tm_hour, tm.tm_min)

    def terminar(self):
        self.guardarVideo()
        self.accept()

    def gridDobleClick(self, grid, fila, columna):
        self.modificar()

    def modificar(self):
        n = self.grid.recno()
        if n >= 0:
            nombre = self.lista[n][0][:-4]
            sts = STS.STS(nombre)
            self.trabajar(sts)

    def nombreNum(self, num):
        return self.lista[num][0][:-4]

    def crear(self):
        nombre = self.editarNombre("", True)
        if nombre:
            sts = STS.STS(nombre)
            sts.save()
            self.grid.refresh()
            self.reread()
            self.trabajar(sts)

    def reread(self):
        self.lista = self.leeSTS()
        self.grid.refresh()

    def rename(self):
        n = self.grid.recno()
        if n >= 0:
            nombreOri = self.nombreNum(n)
            nombreDest = self.editarNombre(nombreOri)
            pathOri = os.path.join(self.carpetaSTS, nombreOri + ".sts")
            pathDest = os.path.join(self.carpetaSTS, nombreDest + ".sts")
            shutil.move(pathOri, pathDest)
            self.reread()

    def editarNombre(self, previo, siNuevo=False):
        while True:
            liGen = [(None, None)]
            liGen.append((_("Name") + ":", previo))
            resultado = FormLayout.fedit(liGen, title=_("STS: Strategic Test Suite"), parent=self, icon=Iconos.STS())
            if resultado:
                accion, liGen = resultado
                nombre = Util.validNomFichero(liGen[0].strip())
                if nombre:
                    if not siNuevo and previo == nombre:
                        return None
                    path = os.path.join(self.carpetaSTS, nombre + ".sts")
                    if os.path.isfile(path):
                        QTUtil2.mensError(self, _("The file %s already exist") % nombre)
                        continue
                    return nombre
                else:
                    return None
            else:
                return None

    def trabajar(self, sts):
        w = WUnSTS(self, sts, self.procesador)
        w.exec_()

    def borrar(self):
        n = self.grid.recno()
        if n >= 0:
            nombre = self.nombreNum(n)
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), nombre)):
                path = os.path.join(self.carpetaSTS, nombre + ".sts")
                os.remove(path)
                self.reread()

    def copiar(self):
        n = self.grid.recno()
        if n >= 0:
            nombreBase = self.nombreNum(n)
            nombre = self.editarNombre(nombreBase, True)
            if nombre:
                sts = STS.STS(nombreBase)
                sts.saveCopyNew(nombre)
                sts = STS.STS(nombre)
                self.reread()
                self.trabajar(sts)

def sts(procesador, parent):
    w = WSTS(parent, procesador)
    w.exec_()

