import os
import sys
import shutil
import time
import subprocess
import codecs

from PyQt4 import QtGui

import Code.VarGen as VarGen
import Code.Util as Util
import Code.ControlPosicion as ControlPosicion
import Code.Books as Books
import Code.Torneo as Torneo
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
import Code.QT.WinPosition as WinPosition

class WResult(QTVarios.WDialogo):
    def __init__(self, wParent, torneo, torneoTMP, gestor):

        titulo = _("Results")
        icono = Iconos.Torneos()
        extparam = "unresulttorneo"
        QTVarios.WDialogo.__init__(self, wParent, titulo, icono, extparam)

        # Datos
        self.torneo = torneo
        self.torneoTMP = torneoTMP
        self.gestor = gestor
        self.liResult = self.torneo.rehacerResult()
        self.liResultTMP = self.torneoTMP.rehacerResult()

        # Tabs
        self.tab = tab = Controles.Tab()

        # Tab-configuracion --------------------------------------------------
        w = QtGui.QWidget()
        # # Grid
        oColumnas = Columnas.ListaColumnas()
        oColumnas.nueva("NUMERO", _("N."), 35, siCentrado=True)
        oColumnas.nueva("MOTOR", _("Engine"), 190, siCentrado=True)
        oColumnas.nueva("GANADOS", _("Wins"), 120, siCentrado=True)
        oColumnas.nueva("PERDIDOS", _("Lost"), 120, siCentrado=True)
        oColumnas.nueva("TABLAS", _("Draw"), 120, siCentrado=True)
        oColumnas.nueva("PUNTOS", _("Points"), 120, siCentrado=True)
        self.gridResultTMP = Grid.Grid(self, oColumnas, siSelecFilas=True, id="T")
        # # Layout
        layout = Colocacion.V().control(self.gridResultTMP)
        w.setLayout(layout)
        tab.nuevaTab(w, _("Current"))

        # Tab-configuracion --------------------------------------------------
        w = QtGui.QWidget()
        ## Grid
        oColumnas = Columnas.ListaColumnas()
        oColumnas.nueva("NUMERO", _("N."), 35, siCentrado=True)
        oColumnas.nueva("MOTOR", _("Engine"), 190, siCentrado=True)
        oColumnas.nueva("GANADOS", _("Wins"), 120, siCentrado=True)
        oColumnas.nueva("PERDIDOS", _("Lost"), 120, siCentrado=True)
        oColumnas.nueva("TABLAS", _("Draw"), 120, siCentrado=True)
        oColumnas.nueva("PUNTOS", _("Points"), 120, siCentrado=True)
        self.gridResult = Grid.Grid(self, oColumnas, siSelecFilas=True, id="B")
        ## Layout
        layout = Colocacion.V().control(self.gridResult)
        w.setLayout(layout)
        tab.nuevaTab(w, _("All"))

        layout = Colocacion.V().control(tab).margen(8)
        self.setLayout(layout)

        self.registrarGrid(self.gridResultTMP)
        self.registrarGrid(self.gridResult)
        self.recuperarVideo(siTam=True, anchoDefecto=800, altoDefecto=430)

        self.gridResult.gotop()
        self.gridResultTMP.gotop()

    def refresh(self):
        self.liResult = self.torneo.rehacerResult()
        self.liResultTMP = self.torneoTMP.rehacerResult()
        self.gridResult.refresh()
        self.gridResultTMP.refresh()

    def gridNumDatos(self, grid):
        return self.torneoTMP.numEngines() if grid.id == "T" else self.torneo.numEngines()

    def gridDato(self, grid, fila, oColumna):
        columna = oColumna.clave
        liResult = self.liResultTMP if grid.id == "T" else self.liResult
        rs = liResult[fila]
        if columna == "NUMERO":
            return str(fila + 1)
        elif columna == "MOTOR":
            return rs["EN"].alias
        elif columna == "GANADOS":
            w, b = rs["WIN"]
            t = w + b
            return "0" if t == 0 else "%d (%d-%d)" % (t, w, b)
        elif columna == "PERDIDOS":
            w, b = rs["LOST"]
            t = w + b
            return "0" if t == 0 else "%d (%d-%d)" % (t, w, b)
        elif columna == "TABLAS":
            w, b = rs["DRAW"]
            t = w + b
            return "0" if t == 0 else "%d (%d-%d)" % (t, w, b)
        elif columna == "PUNTOS":
            p = rs["PTS"]
            return "%d.%d" % (p / 10, p % 10)

    def closeEvent(self, event):
        self.guardarVideo()
        self.gestor.wresult = None

    def terminar(self):
        self.guardarVideo()
        self.close()

class WUnTorneo(QTVarios.WDialogo):
    def __init__(self, wParent, torneo):

        titulo = _("Competition")
        icono = Iconos.Torneos()
        extparam = "untorneo"
        QTVarios.WDialogo.__init__(self, wParent, titulo, icono, extparam)

        # Datos
        self.torneo = torneo
        self.liEnActual = []
        self.xjugar = None
        self.liResult = None

        # Toolbar
        liAcciones = (   ( _("Save") + "+" + _("Quit"), Iconos.MainMenu(), "terminar" ), None,
                         ( _("Cancel"), Iconos.Cancelar(), "cancelar" ), None,
                         ( _("Play"), Iconos.Pelicula_Seguir(), "gmJugar" ), None,
        )
        tb = Controles.TB(self, liAcciones)

        # Tabs
        self.tab = tab = Controles.Tab()

        # Tab-configuracion --------------------------------------------------
        w = QtGui.QWidget()
        # # Nombre
        lbNombre = Controles.LB(self, _("Name") + ": ")
        self.edNombre = Controles.ED(w, torneo.nombre())
        # # Resign
        lbResign = Controles.LB(self, _("Minimum points to assign winner") + ": ")
        self.sbResign = Controles.SB(self, torneo.resign(), 60, 10000)
        ## Draw-plys
        lbDrawMinPly = Controles.LB(self, _("Minimum moves to assign draw") + ": ")
        self.sbDrawMinPly = Controles.SB(self, torneo.drawMinPly(), 20, 9999)
        ## Draw-puntos
        lbDrawRange = Controles.LB(self, _("Maximum points to assign draw") + ": ")
        self.sbDrawRange = Controles.SB(self, torneo.drawRange(), 0, 50)

        lbBook = Controles.LB(self, _("Opening book") + ": ")
        fvar = VarGen.configuracion.ficheroBooks
        self.listaLibros = Books.ListaLibros()
        self.listaLibros.recuperaVar(fvar)
        ## Comprobamos que todos esten accesibles
        self.listaLibros.comprueba()
        li = [(x.nombre, x.path) for x in self.listaLibros.lista]
        li.insert(0, ("* " + _("Default"), ""))
        self.cbBooks = Controles.CB(self, li, torneo.book())
        btNuevoBook = Controles.PB(self, "", self.nuevoBook, plano=False).ponIcono(Iconos.Nuevo(), tamIcon=16)
        lyBook = Colocacion.H().control(self.cbBooks).control(btNuevoBook).relleno()

        ## Posicion inicial
        lbFEN = Controles.LB(self, _("Initial position") + ": ")
        self.fen = torneo.fen()
        self.btPosicion = Controles.PB(self, " " * 5 + _("Change") + " " * 5, self.posicionEditar).ponPlano(False)
        self.btPosicionQuitar = Controles.PB(self, "", self.posicionQuitar).ponIcono(Iconos.Motor_No())
        self.btPosicionPegar = Controles.PB(self, "", self.posicionPegar).ponIcono(Iconos.Pegar16()).ponToolTip(
            _("Paste FEN position"))
        lyFEN = Colocacion.H().control(self.btPosicionQuitar).control(self.btPosicion).control(
            self.btPosicionPegar).relleno()

        ## Norman Pollock
        lbNorman = Controles.LB(self, '%s(<a href="http://www.hoflink.com/~npollock/chess.html">?</a>): '%_("Initial position from Norman Pollock openings database"))
        self.chbNorman = Controles.CHB(self, " ", self.torneo.norman())

        ## Layout
        layout = Colocacion.G()
        layout.controld(lbNombre, 0, 0).control(self.edNombre, 0, 1)
        layout.controld(lbResign, 1, 0).control(self.sbResign, 1, 1)
        layout.controld(lbDrawMinPly, 2, 0).control(self.sbDrawMinPly, 2, 1)
        layout.controld(lbDrawRange, 3, 0).control(self.sbDrawRange, 3, 1)
        layout.controld(lbBook, 4, 0).otro(lyBook, 4, 1)
        layout.controld(lbFEN, 5, 0).otro(lyFEN, 5, 1)
        layout.controld(lbNorman, 6, 0).control(self.chbNorman, 6, 1)
        layoutV = Colocacion.V().relleno().otro(layout).relleno()
        layoutH = Colocacion.H().relleno().otro(layoutV).relleno()

        ## Creamos
        w.setLayout(layoutH)
        tab.nuevaTab(w, _("Configuration"))

        # Tab-engines --------------------------------------------------
        self.splitterEngines = QtGui.QSplitter(self)
        self.registrarSplitter(self.splitterEngines, "engines")
        ## TB
        liAcciones = [( _("New"), Iconos.TutorialesCrear(), "enNuevo" ), None,
                      ( _("Modify"), Iconos.Modificar(), "enModificar" ), None,
                      ( _("Remove"), Iconos.Borrar(), "enBorrar" ), None,
                      ( _("Copy"), Iconos.Copiar(), "enCopiar" ), None,
                      ( _("Import"), Iconos.MasDoc(), "enImportar" ), None,
        ]
        tbEnA = Controles.TB(self, liAcciones, tamIcon=24)

        ## Grid engine
        oColumnas = Columnas.ListaColumnas()
        oColumnas.nueva("ALIAS", _("Alias"), 209)
        self.gridEnginesAlias = Grid.Grid(self, oColumnas, siSelecFilas=True, id="EA", siSeleccionMultiple=True)
        self.registrarGrid(self.gridEnginesAlias)

        w = QtGui.QWidget()
        ly = Colocacion.V().control(self.gridEnginesAlias).margen(0)
        w.setLayout(ly)
        self.splitterEngines.addWidget(w)

        oColumnas = Columnas.ListaColumnas()
        oColumnas.nueva("CAMPO", _("Label"), 200, siDerecha=True)
        oColumnas.nueva("VALOR", _("Value"), 286)
        self.gridEnginesValores = Grid.Grid(self, oColumnas, siSelecFilas=False, id="EV")
        self.registrarGrid(self.gridEnginesValores)

        w = QtGui.QWidget()
        ly = Colocacion.V().control(self.gridEnginesValores).margen(0)
        w.setLayout(ly)
        self.splitterEngines.addWidget(w)

        self.splitterEngines.setSizes([250, 520])  # por defecto

        w = QtGui.QWidget()
        ly = Colocacion.V().control(tbEnA).control(self.splitterEngines)
        w.setLayout(ly)
        tab.nuevaTab(w, _("Engines"))

        ## Creamos

        # Tab-games --------------------------------------------------
        w = QtGui.QWidget()
        ## TB
        liAcciones = [( _("New"), Iconos.TutorialesCrear(), "gmCrear" ), None,
                      ( _("Remove"), Iconos.Borrar(), "gmBorrar" ), None,
                      ( _("Show"), Iconos.PGN(), "gmMostrar" ), None,
                      ( _("Save") + "(%s)" % _("PGN"), Iconos.GrabarComo(), "gmGuardar" ), None,
        ]
        tbEnG = Controles.TB(self, liAcciones, tamIcon=24)
        ## Grid engine
        oColumnas = Columnas.ListaColumnas()
        oColumnas.nueva("WHITE", _("White"), 190, siCentrado=True)
        oColumnas.nueva("BLACK", _("Black"), 190, siCentrado=True)
        oColumnas.nueva("RESULT", _("Result"), 190, siCentrado=True)
        oColumnas.nueva("TIEMPO", _("Time"), 170, siCentrado=True)
        self.gridGames = Grid.Grid(self, oColumnas, siSelecFilas=True, id="G", siSeleccionMultiple=True)
        self.registrarGrid(self.gridGames)
        ## Layout
        layout = Colocacion.V().control(tbEnG).control(self.gridGames)

        ## Creamos
        w.setLayout(layout)
        tab.nuevaTab(w, _("Games"))

        # Tab-resultado --------------------------------------------------
        w = QtGui.QWidget()

        ## Grid
        oColumnas = Columnas.ListaColumnas()
        oColumnas.nueva("NUMERO", _("N."), 35, siCentrado=True)
        oColumnas.nueva("MOTOR", _("Engine"), 190, siCentrado=True)
        oColumnas.nueva("GANADOS", _("Wins"), 120, siCentrado=True)
        oColumnas.nueva("PERDIDOS", _("Lost"), 120, siCentrado=True)
        oColumnas.nueva("TABLAS", _("Draw"), 120, siCentrado=True)
        oColumnas.nueva("PUNTOS", _("Points"), 120, siCentrado=True)
        self.gridResult = Grid.Grid(self, oColumnas, siSelecFilas=True, id="R")
        self.registrarGrid(self.gridResult)
        ## Layout
        layout = Colocacion.V().control(self.gridResult)

        ## Creamos
        w.setLayout(layout)
        tab.nuevaTab(w, _("Result"))

        # Layout
        layout = Colocacion.V().control(tb).control(tab).margen(8)
        self.setLayout(layout)

        self.recuperarVideo(siTam=True, anchoDefecto=800, altoDefecto=430)

        self.gridEnginesAlias.gotop()

        self.edNombre.setFocus()

        self.muestraPosicion()

    def muestraPosicion(self):
        if self.fen:
            rotulo = self.fen
            self.btPosicionQuitar.show()
            self.btPosicionPegar.show()
            self.chbNorman.ponValor(False)
        else:
            rotulo = _("Change")
            self.btPosicionQuitar.hide()
            self.btPosicionPegar.show()
        rotulo = " " * 5 + rotulo + " " * 5
        self.btPosicion.ponTexto(rotulo)

    def posicionEditar(self):
        resp = WinPosition.editarPosicion(self, VarGen.configuracion, self.fen)
        if resp is not None:
            self.fen = resp
            self.muestraPosicion()

    def posicionQuitar(self):
        self.fen = ""
        self.muestraPosicion()

    def posicionPegar(self):
        texto = QTUtil.traePortapapeles()
        if texto:
            cp = ControlPosicion.ControlPosicion()
            try:
                cp.leeFen(texto.strip())
                self.fen = cp.fen()
                if self.fen == ControlPosicion.FEN_INICIAL:
                    self.fen = ""
                self.muestraPosicion()
            except:
                pass

    def nuevoBook(self):
        fbin = QTUtil2.leeFichero(self, self.listaLibros.path, "bin", titulo=_("Polyglot book"))
        if fbin:
            self.listaLibros.path = os.path.dirname(fbin)
            nombre = os.path.basename(fbin)[:-4]
            b = Books.Libro("P", nombre, fbin, False)
            self.listaLibros.nuevo(b)
            fvar = VarGen.configuracion.ficheroBooks
            self.listaLibros.guardaVar(fvar)
            li = [(x.nombre, x.path) for x in self.listaLibros.lista]
            li.insert(0, ("* " + _("Default"), "*"))
            self.cbBooks.rehacer(li, b.path)

    def gridNumDatos(self, grid):
        gid = grid.id
        if gid == "EA":
            return self.torneo.numEngines()
        elif gid == "EV":
            return len(self.liEnActual)
        elif gid == "R":
            return self.torneo.numEngines()
        else:
            return self.torneo.numGames()

    def gridDato(self, grid, fila, oColumna):
        columna = oColumna.clave
        gid = grid.id
        if gid == "EA":
            return self.gridDatoEnginesAlias(fila, columna)
        elif gid == "EV":
            return self.gridDatoEnginesValores(fila, columna)
        elif gid == "R":
            return self.gridDatoResult(fila, columna)
        else:
            return self.gridDatoGames(fila, columna)

    def gridDatoEnginesAlias(self, fila, columna):
        me = self.torneo.liEngines()[fila]
        if columna == "ALIAS":
            return me.alias

    def gridDatoEnginesValores(self, fila, columna):
        li = self.liEnActual[fila]
        if columna == "CAMPO":
            return li[0]
        else:
            return str(li[1])

    def borraResult(self):
        self.liResult = None

    def gridDatoResult(self, fila, columna):
        if self.liResult is None:
            self.liResult = self.torneo.rehacerResult()
        rs = self.liResult[fila]
        if columna == "NUMERO":
            return str(fila + 1)
        elif columna == "MOTOR":
            return rs["EN"].alias
        elif columna == "GANADOS":
            w, b = rs["WIN"]
            t = w + b
            return "0" if t == 0 else "%d (%d-%d)" % (t, w, b)
        elif columna == "PERDIDOS":
            w, b = rs["LOST"]
            t = w + b
            return "0" if t == 0 else "%d (%d-%d)" % (t, w, b)
        elif columna == "TABLAS":
            w, b = rs["DRAW"]
            t = w + b
            return "0" if t == 0 else "%d (%d-%d)" % (t, w, b)
        elif columna == "PUNTOS":
            p = rs["PTS"]
            return "%d.%d" % (p / 10, p % 10)

    def gridDatoGames(self, fila, columna):
        gm = self.torneo.liGames()[fila]
        if columna == "WHITE":
            en = self.torneo.buscaHEngine(gm.hwhite())
            return en.alias if en else "???"
        elif columna == "BLACK":
            en = self.torneo.buscaHEngine(gm.hblack())
            return en.alias if en else "???"
        elif columna == "RESULT":
            resp = gm.result()
            dic = {None: "?", 1: "1-0", 0: "1/2-1/2", 2: "0-1"}
            return dic[resp]
        elif columna == "TIEMPO":
            return gm.etiTiempo()

    def gridCambiadoRegistro(self, grid, fila, columna):
        if grid.id == "EA":
            self.actEngine()
            self.gridEnginesValores.refresh()

    def actEngine(self):
        self.liEnActual = []
        fila = self.gridEnginesAlias.recno()
        if fila < 0:
            return

        me = self.torneo.liEngines()[fila]
        # tipo, clave, rotulo, valor
        self.liEnActual.append(( _("Engine"), me.idName ))
        self.liEnActual.append(( _("Author"), me.idAuthor ))
        self.liEnActual.append(( _("File"), me.exe ))
        self.liEnActual.append(( _("Information"), me.idInfo.replace("\n", " - ") ))
        self.liEnActual.append(( "ELO", me.elo ))
        self.liEnActual.append(( _("Maximum depth"), me.depth() ))
        self.liEnActual.append(( _("Maximum seconds to think"), me.time() ))
        pbook = me.book()
        if pbook == "-":
            pbook = "* " + _("Engine book")
        else:
            if pbook == "*":
                pbook = "* " + _("Default")
            dic = {
                "au": _("Uniform random"),
                "ap": _("Proportional random"),
                "mp": _("Always the highest percentage"),
            }
            pbook += "   (%s)" % dic[me.bookRR()]

        self.liEnActual.append(( _("Opening book"), pbook ))

        for opcion in me.liOpciones:
            self.liEnActual.append(( opcion.nombre, str(opcion.valor) ))

    def procesarTB(self):
        accion = self.sender().clave
        eval("self.%s()" % accion)

    def terminar(self):
        if self.grabar():
            self.guardarVideo()
            self.accept()

    def gmJugar(self):
        if self.grabar():
            liGames = self.torneo.liGames()
            li = []
            sten = set()
            for gm in liGames:
                if gm.result() is None:
                    li.append(gm)
                    sten.add(gm.hwhite())
                    sten.add(gm.hblack())
            for heng in sten:
                engine = self.torneo.buscaHEngine(heng)
                if not engine:
                    QTUtil2.mensError(self, _("Some engine is not valid"))
                    return
                if not Util.existeFichero(engine.exe):
                    QTUtil2.mensError(self, "%s:\n\n%s\n\n%s" % (engine.alias, _("Path does not exist."), engine.exe))
                    return

            if li:
                self.xjugar = (self.torneo, li)
                self.guardarVideo()
                self.accept()
            else:
                QTUtil2.mensError(self, _("There are no pending games to play"))

    def verSiJugar(self):
        return self.xjugar

    def cancelar(self):
        self.guardarVideo()
        self.accept()

    def grabar(self):
        nombreInicial = self.torneo.nombre()
        fichInicial = self.torneo.fichero()
        nombre = self.edNombre.texto()
        if not nombre:
            QTUtil2.mensaje(self, _("Missing name"))
            self.tab.activa(0)
            self.edNombre.setFocus()
            return False
        self.torneo.resign(self.sbResign.valor())
        self.torneo.drawMinPly(self.sbDrawMinPly.valor())
        self.torneo.drawRange(self.sbDrawRange.valor())
        self.torneo.fen(self.fen)
        self.torneo.norman(self.chbNorman.valor())

        try:
            self.torneo.nombre(nombre)
            self.torneo.grabar()
            if fichInicial and self.torneo.fichero().lower() != fichInicial.lower():
                os.remove(fichInicial)
            return True
        except:
            self.torneo.nombre(nombreInicial)
            QTUtil2.mensaje(self, _("Unable to save") + "\n" + _("The tournament name contains incorrect characters"))
            return False

    def enNuevo(self):
        # Pedimos el ejecutable
        exeMotor = QTUtil2.leeFichero(self, self.torneo.ultCarpetaEngines(), "*", _("Engine"))
        if not exeMotor:
            return
        self.torneo.ultCarpetaEngines(os.path.dirname(exeMotor))

        # Leemos el UCI
        listaEngines = self.torneo.liEngines()
        me = Torneo.Engine()
        me.ponHuella(listaEngines)
        if not me.leerUCI(exeMotor):
            QTUtil2.mensaje(self, _X(_("The file %1 does not correspond to a UCI engine type."), exeMotor))
            return
        self.torneo.appendEngine(me)
        self.gridEnginesAlias.refresh()
        self.gridEnginesAlias.gobottom(0)

        self.borraResult()

    def enImportar(self):
        menu = QTVarios.LCMenu(self)
        lista = VarGen.configuracion.comboMotoresCompleto()
        nico = QTVarios.rondoPuntos()
        for nombre, clave in lista:
            menu.opcion(clave, nombre, nico.otro())

        resp = menu.lanza()
        if not resp:
            return

        me = Torneo.Engine()
        me.ponHuella(self.torneo.liEngines())
        me.leerConfigEngine(resp)
        self.torneo.appendEngine(me)
        self.gridEnginesAlias.refresh()
        self.gridEnginesAlias.gobottom(0)

        self.borraResult()

    def gridTeclaControl(self, grid, k, siShift, siControl, siAlt):
        if k == 16777223:
            if grid.id == "G":
                self.gmBorrar()
            elif grid.id == "EA":
                self.enBorrar()

    def gridDobleClick(self, grid, fila, columna):
        if grid.id in ["EA", "EV"]:
            self.enModificar()
        elif grid.id == "G":
            self.gmMostrar()

    def enModificar(self):
        fila = self.gridEnginesAlias.recno()
        if fila < 0:
            return
        listaEngines = self.torneo.liEngines()
        me = listaEngines[fila]
        w = PantallaMotores.WMotor(self, listaEngines, me, siTorneo=True)
        if w.exec_():
            self.actEngine()
            self.gridEnginesAlias.refresh()
            self.gridEnginesValores.refresh()

    def enBorrar(self):
        li = self.gridEnginesAlias.recnosSeleccionados()
        if li:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                self.torneo.delEngines(li)
                self.gridEnginesAlias.refresh()
                self.gridGames.refresh()
                self.gridEnginesAlias.setFocus()
                self.borraResult()

    def enCopiar(self):
        fila = self.gridEnginesAlias.recno()
        if fila >= 0:
            me = self.torneo.liEngines()[fila]
            self.torneo.copyEngine(me)
            self.gridEnginesAlias.refresh()
            self.gridEnginesAlias.gobottom(0)
            self.borraResult()

    def gmCrear(self):
        if self.torneo.numEngines() < 2:
            QTUtil2.mensError(self, _("You must create at least two engines"))
            return

        dicValores = VarGen.configuracion.leeVariables("crear_torneo")

        get = dicValores.get

        liGen = [(None, None)]

        config = FormLayout.Spinbox(_("Rounds"), 1, 999, 50)
        liGen.append(( config, get("ROUNDS", 1) ))

        liGen.append((None, None))

        config = FormLayout.Spinbox(_("Total minutes"), 1, 999, 50)
        liGen.append(( config, get("MINUTES", 10) ))

        config = FormLayout.Spinbox(_("Seconds added per move"), 0, 999, 50)
        liGen.append(( config, get("SECONDS", 0) ))

        liGen.append((None, _("Engines")))

        liEngines = self.torneo.liEngines()
        for pos, en in enumerate(liEngines):
            liGen.append(( en.alias, get(en.huella(), True) ))

        liGen.append((None, None))
        liGen.append(( _("Select all"), False ))

        reg = Util.Almacen()
        reg.form = None

        def dispatch(valor):
            if reg.form is None:
                reg.form = valor
                reg.liEngines = []
                leng = len(liEngines)
                for x in range(leng):
                    reg.liEngines.append(valor.getWidget(x + 3))
                reg.selectall = valor.getWidget(leng + 3)
                reg.valorall = False

            else:
                QTUtil.refreshGUI()
                select = reg.selectall.isChecked()
                if select != reg.valorall:
                    for uno in reg.liEngines:
                        uno.setChecked(select)
                    reg.valorall = select
                QTUtil.refreshGUI()

        resultado = FormLayout.fedit(liGen, title=_("Games"), parent=self, icon=Iconos.Torneos(), dispatch=dispatch)
        if resultado is None:
            return

        accion, liResp = resultado
        dicValores["ROUNDS"] = rounds = liResp[0]
        dicValores["MINUTES"] = minutos = liResp[1]
        dicValores["SECONDS"] = segundos = liResp[2]

        liSel = []
        for num in range(self.torneo.numEngines()):
            en = liEngines[num]
            dicValores[en.huella()] = si = liResp[3 + num]
            if si:
                liSel.append(en.huella())

        VarGen.configuracion.escVariables("crear_torneo", dicValores)

        nSel = len(liSel)
        if nSel < 2:
            QTUtil2.mensError(self, _("You must create at least two engines"))
            return

        for r in range(rounds):
            for x in range(0, nSel - 1):
                for y in range(x + 1, nSel):
                    self.torneo.nuevoGame(liSel[x], liSel[y], minutos, segundos)
                    self.torneo.nuevoGame(liSel[y], liSel[x], minutos, segundos)

        self.gridGames.refresh()
        self.gridGames.gobottom()
        self.borraResult()

    def gmBorrar(self):
        li = self.gridGames.recnosSeleccionados()
        if li:
            if QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                self.torneo.delGames(li)
                self.gridGames.refresh()
                self.borraResult()

    def pgnActual(self):
        nrec = self.gridGames.reccount()
        if not nrec:
            return None
        li = self.gridGames.recnosSeleccionados()
        if not li:
            li = range(nrec)
        return self.torneo.grabaPGNgames(li)

    def gmMostrar(self):
        pgn = self.pgnActual()
        if pgn:
            fpgn = Util.ficheroTemporal("Tmp", "pgn")
            f = codecs.open(fpgn, "w", "utf-8", 'ignore')
            f.write(pgn)
            f.close()

            # Se lanza otro LC con ese PGN
            QTUtil2.mensajeTemporal(self, _("One moment please..."), 0.3)
            if sys.argv[0].endswith(".py"):
                subprocess.Popen(["pythonw.exe" if VarGen.isWindows else "python", "./Lucas.py", fpgn])
            else:
                subprocess.Popen(["Lucas.exe" if VarGen.isWindows else "./Lucas", fpgn])

    def gmGuardar(self):
        pgn = self.pgnActual()
        if pgn:
            QTVarios.savePGN(self, pgn)

class WTorneos(QTVarios.WDialogo):
    def __init__(self, wParent):

        titulo = _("Tournaments between engines")
        icono = Iconos.Torneos()
        extparam = "torneos"
        QTVarios.WDialogo.__init__(self, wParent, titulo, icono, extparam)

        # Datos
        self.lista = self.leeTorneos()
        self.xjugar = None

        # Toolbar
        liAcciones = (   ( _("Quit"), Iconos.MainMenu(), "terminar", True ),
                         ( _("Modify"), Iconos.Modificar(), "modificar", False ),
                         ( _("New"), Iconos.TutorialesCrear(), "crear", True ),
                         ( _("Remove"), Iconos.Borrar(), "borrar", False ),
                         ( _("Copy"), Iconos.Copiar(), "copiar", False ),
        )
        li = []
        siTodos = len(self.lista) > 0
        for txt, ico, clv, siT in liAcciones:
            if siTodos or siT:
                li.append((txt, ico, clv))
                li.append(None)
        tb = Controles.TB(self, li)

        # grid
        oColumnas = Columnas.ListaColumnas()
        oColumnas.nueva("NOMBRE", _("Name"), 240)
        oColumnas.nueva("FECHA", _("Date"), 120, siCentrado=True)

        self.grid = Grid.Grid(self, oColumnas, siSelecFilas=True)
        self.registrarGrid(self.grid)

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).margen(8)
        self.setLayout(layout)

        self.recuperarVideo(siTam=True, anchoDefecto=400, altoDefecto=500)

        self.grid.gotop()

    def leeTorneos(self):
        li = []
        carpeta = VarGen.configuracion.carpeta
        for x in Util.listdir(carpeta, siUnicode=True):
            if x.lower().endswith(".mvm"):
                fich = os.path.join(carpeta, x)
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

    def procesarTB(self):
        accion = self.sender().clave
        eval("self.%s()" % accion)

    def terminar(self):
        self.guardarVideo()
        self.accept()

    def gridDobleClick(self, grid, fila, columna):
        self.modificar()

    def modificar(self):
        n = self.grid.recno()
        if n >= 0:
            nombre = self.lista[n][0][:-4]
            torneo = Torneo.Torneo(nombre)
            torneo.leer()
            self.trabajar(torneo)

    def crear(self):
        torneo = Torneo.Torneo()
        self.trabajar(torneo)

    def trabajar(self, torneo):
        w = WUnTorneo(self, torneo)
        w.exec_()

        self.lista = self.leeTorneos()
        self.grid.refresh()
        self.xjugar = w.verSiJugar()
        if self.xjugar:
            self.terminar()

    def verSiJugar(self):
        return self.xjugar

    def borrar(self):
        n = self.grid.recno()
        if n >= 0:
            nombre = self.lista[n][0][:-4]
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), nombre)):
                torneo = Torneo.Torneo(nombre)
                os.remove(torneo.fichero())
                self.lista = self.leeTorneos()
                self.grid.refresh()

    def copiar(self):
        reg = self.grid.recno()
        if reg >= 0:
            nombreBase = self.lista[reg][0][:-4]
            torneoBase = Torneo.Torneo(nombreBase)
            n = 1
            while True:
                nombre = nombreBase + "-%d" % n
                torneo = Torneo.Torneo(nombre)
                if os.path.isfile(torneo.fichero()):
                    n += 1
                else:
                    shutil.copy(torneoBase.fichero(), torneo.fichero())
                    self.lista = self.leeTorneos()
                    self.grid.refresh()
                    return

def torneos(parent):
    w = WTorneos(parent)
    if w.exec_():
        return w.verSiJugar()
    else:
        return None

def unTorneo(parent, torneo):
    w = WUnTorneo(parent, torneo)
    if w.exec_():
        return w.verSiJugar()
    else:
        return None

