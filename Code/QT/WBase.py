from PyQt4 import QtCore, QtGui

from Code.Constantes import *
import Code.VarGen as VarGen
import Code.QT.Iconos as Iconos
import Code.QT.Tablero as Tablero
import Code.QT.QTUtil as QTUtil
import Code.QT.QTUtil2 as QTUtil2
import Code.QT.Controles as Controles
import Code.QT.QTVarios as QTVarios
import Code.QT.Delegados as Delegados
import Code.QT.Columnas as Columnas
import Code.QT.Grid as Grid
import Code.QT.Colocacion as Colocacion
import Code.QT.WCapturas as WCapturas

class WBase(QtGui.QWidget):
    def __init__(self, parent, gestor):
        super(WBase, self).__init__(parent)

        self.gestor = gestor

        self.centipawns = VarGen.configuracion.centipawns

        self.procesandoEventos = None

        # self.setBackgroundRole(QtGui.QPalette.Light)
        self.setWindowIcon(Iconos.Aplicacion())
        self.setStyleSheet("QToolButton { padding: 0px; }")

        self.creaToolBar()
        self.creaTablero()

        self.creaCapturas()
        lyBI = self.creaBloqueInformacion()
        self.lyBI = lyBI

        lyT = Colocacion.V().control(self.tablero).relleno()

        lyAI = Colocacion.H().relleno().controli(self.capturas).otroi(lyT).otroi(lyBI).relleno().margen(0)
        ly = Colocacion.V().control(self.tb).relleno().otro(lyAI).relleno().margen(2)

        self.setLayout(ly)

        self.preparaColoresPGN()

    def preparaColoresPGN(self):
        self.colorMateNegativo = QTUtil.qtColorRGB(0, 0, 0)
        self.colorMatePositivo = QTUtil.qtColorRGB(159, 0, 159)
        self.colorNegativo = QTUtil.qtColorRGB(255, 0, 0)
        self.colorPositivo = QTUtil.qtColorRGB(0, 0, 255)

        self.colorBlanco = QTUtil.qtColorRGB(255, 255, 255)

    def ponGestor(self, gestor):
        self.gestor = gestor

    def creaToolBar(self):
        self.tb = QtGui.QToolBar("BASICO", self)
        self.tb.setIconSize(QtCore.QSize(32, 32))
        self.tb.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        # self.tb.setStyleSheet("QWidget { background: #AFC3D7 }")
        # self.tb.setStyleSheet("QToolBar {background: #AFC3D7;border-bottom: 1px solid black; border-top: 1px solid black;}");

        self.preparaTB()

    def creaTablero(self):
        ae = QTUtil.altoEscritorio()
        mx = 64 if ae >= 750 else 48
        confTablero = self.gestor.configuracion.confTablero("BASE", mx)
        self.tablero = Tablero.Tablero(self, confTablero)
        self.tablero.crea()
        self.tablero.setFocus()

        Delegados.generaPM(self.tablero.piezas)

    def columnas60(self, siPoner, cNivel):
        oColumnas = self.pgn.oColumnas
        oColumnas.liColumnas[0].cabecera = cNivel if siPoner else _("N.")
        oColumnas.liColumnas[1].cabecera = _("Errors") if siPoner else _("White")
        oColumnas.liColumnas[2].cabecera = _("Second(s)") if siPoner else _("Black")
        oColumnas.liColumnas[0].clave = "NIVEL" if siPoner else "NUMERO"
        oColumnas.liColumnas[1].clave = "ERRORES" if siPoner else "BLANCAS"
        oColumnas.liColumnas[2].clave = "TIEMPO" if siPoner else "NEGRAS"
        self.pgn.releerColumnas()

        self.pgn.seleccionaFilas(siPoner, False)

    def creaBloqueInformacion(self):
        nAnchoPgn = self.gestor.configuracion.anchoPGN
        nAnchoColor = (nAnchoPgn - 35 - 20) / 2
        nAnchoLabels = max(int((nAnchoPgn - 3) / 2), 140)
        # # Pgn
        oColumnas = Columnas.ListaColumnas()
        oColumnas.nueva("NUMERO", _("N."), 35, siCentrado=True)
        siFigurinesPGN = self.gestor.configuracion.figurinesPGN
        oColumnas.nueva("BLANCAS", _("White"), nAnchoColor,
                        edicion=Delegados.EtiquetaPGN(True if siFigurinesPGN else None))
        oColumnas.nueva("NEGRAS", _("Black"), nAnchoColor,
                        edicion=Delegados.EtiquetaPGN(False if siFigurinesPGN else None))
        self.pgn = Grid.Grid(self, oColumnas, siCabeceraMovible=False)
        self.pgn.setMinimumWidth(nAnchoPgn)
        configuracion = self.gestor.configuracion
        self.pgn.tipoLetra(puntos=configuracion.puntosPGN)
        self.pgn.ponAltoFila(configuracion.altoFilaPGN)

        # # Blancas y negras
        f = Controles.TipoLetra(puntos=self.gestor.configuracion.tamFontRotulos + 2, peso=75)
        bl, ng = _("White"), _("Black")
        self.lbJugBlancas = Controles.LB(self, bl).anchoFijo(nAnchoLabels).alinCentrado().ponFuente(f).ponColorFondoN("black",
                                                                                                                "white").ponWrap()
        self.lbJugNegras = Controles.LB(self, ng).anchoFijo(nAnchoLabels).alinCentrado().ponFuente(f).ponColorFondoN("white",
                                                                                                               "black").ponWrap()
        self.lbJugBlancas.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Raised)
        self.lbJugNegras.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Raised)

        ## Relojes
        f = Controles.TipoLetra(puntos=30, peso=75)
        self.lbRelojBlancas = Controles.LB(self, "00:00").ponFuente(f).alinCentrado().ponColorFondoN("#076C9F",
                                                                                               "#EFEFEF").anchoMinimo(
            nAnchoLabels)
        self.lbRelojNegras = Controles.LB(self, "00:00").ponFuente(f).alinCentrado().ponColorFondoN("#076C9F",
                                                                                              "#EFEFEF").anchoMinimo(
            nAnchoLabels)
        self.lbRelojBlancas.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Raised)
        self.lbRelojNegras.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Raised)

        ## Revisando
        f = Controles.TipoLetra(puntos=14, peso=75)
        self.lbRevision = Controles.LB(self, _("Reviewing...")).alinCentrado().ponFuente(f).ponFondoN("#b3b3b3")

        ## Ayudas
        self.ayudasUD = QTVarios.LCNumero(3)

        f = Controles.TipoLetra(puntos=12)
        self.lbCredito = Controles.LB(self, _("Available hints") + " :   ").alinCentrado().ponFuente(f)

        ## Boton de tutor activo
        self.btActivarTutor = Controles.PB(self, "", rutina=self.cambiaSiActivarTutor,
                                           plano=False)  #.anchoFijo( nAnchoPgn )

        ## Rotulos de informacion
        f = Controles.TipoLetra(puntos=self.gestor.configuracion.tamFontRotulos)
        self.lbRotulo1 = Controles.LB(self).ponWrap().ponFuente(f)
        self.lbRotulo2 = Controles.LB(self).ponWrap().ponFuente(f)
        f9 = Controles.TipoLetra(puntos=9)
        self.lbRotulo3 = Controles.LB(self).ponWrap().ponFuente(f9)
        # self.lbRotulo1.setStyleSheet("*{ border: 1px solid darkgray }")
        # self.lbRotulo2.setStyleSheet("*{ border: 1px solid darkgray }")
        self.lbRotulo3.setStyleSheet("*{ border: 1px solid darkgray }")
        self.lbRotulo3.altoFijo(48)

        # Lo escondemos todo
        self.lbJugBlancas.hide()
        self.lbJugNegras.hide()
        self.lbRelojBlancas.hide()
        self.lbRelojNegras.hide()
        self.pgn.hide()
        self.lbRevision.hide()
        self.ayudasUD.hide()
        self.lbCredito.hide()
        self.btActivarTutor.hide()
        self.lbRotulo1.hide()
        self.lbRotulo2.hide()
        self.lbRotulo3.hide()

        # Layout

        ## Remoto
        lyColor = Colocacion.G()
        lyColor.controlc(self.lbJugBlancas, 0, 0).controlc(self.lbJugNegras, 0, 1)
        lyColor.controlc(self.lbRelojBlancas, 1, 0).controlc(self.lbRelojNegras, 1, 1)

        ## Ayudas
        lyAyudas = Colocacion.H().relleno().control(self.lbCredito).control(self.ayudasUD).relleno().ponSeparacion(1)

        ## Todo
        lyV = Colocacion.V().otro(lyColor).control(self.pgn)
        lyV.control(self.lbRevision).otro(lyAyudas).control(self.btActivarTutor)
        lyV.control(self.lbRotulo1).control(self.lbRotulo2).control(self.lbRotulo3)

        return lyV

    def preparaTB(self):

        self.dicTB = {}

        liOpciones = ( ( _("Quit"), Iconos.Terminar(), k_terminar ),
                       ( _("Play"), Iconos.Libre(), k_play ),
                       ( _("Competition"), Iconos.NuevaPartida(), k_competicion ),
                       ( _("Elo-Rating"), Iconos.Elo(), k_elo ),
                       ( _("Training"), Iconos.Entrenamiento(), k_entrenamiento ),
                       ( _("Options"), Iconos.Opciones(), k_opciones ),
                       ( _("Information"), Iconos.Informacion(), k_informacion ),
                       ( _("Save"), Iconos.Grabar(), k_grabar ),
                       ( _("Save as"), Iconos.GrabarComo(), k_grabarComo ),
                       ( _("Open"), Iconos.Recuperar(), k_recuperar ),
                       ( _("Resign"), Iconos.Abandonar(), k_abandonar ),
                       ( _("Reinit"), Iconos.Reiniciar(), k_reiniciar ),
                       ( _("Takeback"), Iconos.Atras(), k_atras ),
                       ( _("Adjourn"), Iconos.Aplazar(), k_aplazar ),
                       ( _("End game"), Iconos.FinPartida(), k_finpartida ),
                       ( _("Close"), Iconos.MainMenu(), k_mainmenu ),
                       ( _("Reinit"), Iconos.Reiniciar(), k_ent_empezar ),
                       ( _("Previous"), Iconos.Anterior(), k_anterior ),
                       ( _("Next"), Iconos.Siguiente(), k_siguiente ),
                       ( _("Quit"), Iconos.FinPartida(), k_pgnFin ),
                       ( _("Paste PGN"), Iconos.Pegar(), k_pgnPaste ),
                       ( _("Read PGN"), Iconos.Fichero(), k_pgnFichero ),
                       ( _("PGN Labels"), Iconos.InformacionPGN(), k_pgnInformacion ),
                       ( _("Other game"), Iconos.FicheroRepite(), k_pgnFicheroRepite ),
                       ( _("My games"), Iconos.NuestroFichero(), k_pgnNuestroFichero ),
                       ( _("Resign"), Iconos.Rendirse(), k_rendirse ),
                       ( _("Draw"), Iconos.Tablas(), k_tablas ),
                       ( _("Boxrooms PGN"), Iconos.Trasteros(), k_trasteros ),
                       ( _("End"), Iconos.MainMenu(), k_peliculaTerminar ),
                       ( _("Slow"), Iconos.Pelicula_Lento(), k_peliculaLento ),
                       ( _("Pause"), Iconos.Pelicula_Pausa(), k_peliculaPausa ),
                       ( _("Continue"), Iconos.Pelicula_Seguir(), k_peliculaSeguir ),
                       ( _("Fast"), Iconos.Pelicula_Rapido(), k_peliculaRapido ),
                       ( _("Repeat"), Iconos.Pelicula_Repetir(), k_peliculaRepetir ),
                       ( _("Play"), Iconos.Jugar(), k_jugar ),
                       ( _("Help"), Iconos.AyudaGR(), k_ayuda ),
                       ( _("Level"), Iconos.Jugar(), k_mateNivel ),
                       ( _("Accept"), Iconos.Aceptar(), k_aceptar ),
                       ( _("Cancel"), Iconos.Cancelar(), k_cancelar ),
                       ( _("Game of the day"), Iconos.LM(), k_jugadadia ),
                       ( _("Config"), Iconos.Configurar(), k_configurar ),
                       ( _("Utilities"), Iconos.Utilidades(), k_utilidades ),
                       ( _("Variants"), Iconos.VariantesG(), k_variantes ),
                       ( _("Tools"), Iconos.Tools(), k_tools ),
                       ( _("Change"), Iconos.Cambiar(), k_cambiar),
                       ( _("Show text"), Iconos.Modificar(), k_showtext),
                       ( _("Help to move"), Iconos.BotonAyuda(), k_ayudaMover),
                       ( _("Send"), Iconos.Enviar(), k_enviar),
                       # ( "Debug", Iconos.Camara(), 999),# Martin debug
        )

        cf = self.gestor.configuracion
        peso = 75 if cf.boldTB else 50
        puntos = cf.puntosTB
        font = Controles.TipoLetra(puntos=puntos, peso=peso)

        for titulo, icono, clave in liOpciones:
            accion = QtGui.QAction(titulo, None)
            accion.setIcon(icono)
            accion.setIconText(titulo)
            accion.setFont(font)
            self.connect(accion, QtCore.SIGNAL("triggered()"), self.procesarAccion)
            accion.clave = clave
            self.dicTB[clave] = accion

    def procesarAccion(self):
        self.gestor.procesarAccion(self.sender().clave)

    def ponToolBar(self, liAcciones, separator=False):

        # liAcciones = list(liAcciones) # Martin debug
        # liAcciones.append( 999 )

        self.tb.clear()
        for k in liAcciones:
            self.dicTB[k].setVisible(True)
            self.dicTB[k].setEnabled(True)
            self.tb.addAction(self.dicTB[k])
            if separator:
                self.tb.addSeparator()

        self.tb.liAcciones = liAcciones
        self.tb.update()
        QTUtil.refreshGUI()

        # if getattr( self, "problemTB", True ):
        # x = self.tb.height()
        # if x > 50:
        # x+= 2
        # self.problemTB = False
        # self.tb.setFixedHeight(x)
        # self.tb.update()
        # QTUtil.refreshGUI()

    def dameToolBar(self):
        return self.tb.liAcciones

    def habilitaToolbar(self, kopcion, siHabilitar):
        self.dicTB[kopcion].setEnabled(siHabilitar)

    def mostrarOpcionToolbar(self, kopcion, siMostrar):
        self.dicTB[kopcion].setVisible(siMostrar)

    def ponActivarTutor(self, siActivar):
        if siActivar:
            mens = _("Tutor enabled")
        else:
            mens = _("Tutor disabled")
        self.btActivarTutor.setText(mens)

    def cambiaSiActivarTutor(self):
        self.gestor.cambiaActivarTutor()

    def gridNumDatos(self, grid):
        return self.gestor.numDatos()

    def gridBotonIzquierdo(self, grid, fila, columna):
        self.gestor.pgnMueveBase(fila, columna.clave)

    def gridBotonDerecho(self, grid, fila, columna, modificadores):
        self.gestor.pgnMueveBase(fila, columna.clave)

        if modificadores.siControl:
            self.gestor.capturas()
        else:
            self.gestor.pgnInformacion(fila, columna.clave)

    def gridDobleClick(self, grid, fila, columna):
        if columna.clave == "NUMERO":
            return
        self.gestor.analizaPosicion(fila, columna.clave)

    def gridMouseCabecera(self, grid, columna):
        colBlancas = self.pgn.oColumnas.columna(1)
        colNegras = self.pgn.oColumnas.columna(2)
        nuevoTam = 0
        if colBlancas.ancho != self.pgn.columnWidth(1):
            nuevoTam = self.pgn.columnWidth(1)
        elif colNegras.ancho != self.pgn.columnWidth(2):
            nuevoTam = self.pgn.columnWidth(2)

        if nuevoTam:
            colBlancas.ancho = nuevoTam
            colNegras.ancho = nuevoTam
            self.pgn.ponAnchosColumnas()
            nAnchoPgn = nuevoTam * 2 + 35 + 20
            self.pgn.setMinimumWidth(nAnchoPgn)
            QTUtil.refreshGUI()
            self.gestor.configuracion.anchoPGN = nAnchoPgn
            self.gestor.configuracion.graba()

    def gridTeclaControl(self, grid, k, siShift, siControl, siAlt):
        self.teclaPulsada("G", k)

    def gridWheelEvent(self, ogrid, siAdelante):
        self.teclaPulsada("T", 16777236 if not siAdelante else 16777234)

    def gridDato(self, grid, fila, oColumna):
        controlPGN = self.gestor.pgn

        col = oColumna.clave
        if col == "NUMERO":
            return controlPGN.dato(fila, col)

        jg = controlPGN.soloJugada(fila, col)
        if not jg:
            return self.gestor.pgn.dato(fila, col)  # GestorMate,...

        if not controlPGN.siMostrar:
            return "-"

        color = None
        info = ""
        indicadorInicial = None
        liNAGs = jg.critica.split(" ")

        # NAG_1=Jugada buena NAG_2=Jugada mala NAG_3=Muy buena jugada NAG_4=Muy mala jugada
        NAG_0, NAG_1, NAG_2, NAG_3, NAG_4, NAG_5, NAG_6 = range(7)
        nag = NAG_0
        if jg.analisis:
            multianalisis, pos = jg.analisis
            analisis = multianalisis.liMultiPV[pos]
            mate = analisis.mate
            siW = jg.posicionBase.siBlancas
            if mate:
                if mate == 1:
                    info = ""
                else:
                    if not siW:
                        mate = -mate
                    info = "(M%+d)" % mate
            else:
                pts = analisis.puntos
                if not siW:
                    pts = -pts
                if self.centipawns:
                    info = "(" + str(pts) + ")"
                else:
                    info = "(%+0.2f)" % float(pts / 100.0)
            nb = analisis.nivelBlunder()
            if nb:
                if nb > 100:
                    nag = NAG_4
                else:
                    nag = NAG_2
            elif analisis.nivelBrillante():
                nag = NAG_3
            elif pos == 0 or analisis.puntosABS() == multianalisis.liMultiPV[0].puntosABS():
                nag = NAG_1

            criticaDirecta = jg.criticaDirecta
            if criticaDirecta:
                nag = {"??": NAG_4, "?": NAG_2, "!!": NAG_3, "!": NAG_1, "!?": NAG_5, "?!": NAG_6}.get(criticaDirecta,
                                                                                                       NAG_0)

            for critica in liNAGs:
                if critica in ("1", "2", "3", "4", "5", "6"):
                    nag = int(critica)
                    break

        if jg.siApertura or jg.critica or jg.comentario or jg.variantes:
            siA = jg.siApertura
            nR = 0
            if jg.critica and nag == NAG_0:
                nR += 1
            if jg.comentario:
                nR += 1
            if jg.variantes:
                nR += 1
            if siA:
                indicadorInicial = "R" if nR == 0 else "S"
            elif nR == 1:
                indicadorInicial = "V"
            elif nR > 1:
                indicadorInicial = "M"

        if jg.siXFCC:
            indicadorInicial = "X"

        pgn = jg.pgnFigurinesSP() if self.gestor.configuracion.figurinesPGN else jg.pgnSP()
        if nag:
            c = self.gestor.configuracion
            color = \
                {NAG_1: c.color_nag1, NAG_2: c.color_nag2, NAG_3: c.color_nag3, NAG_4: c.color_nag4,
                 NAG_5: c.color_nag5,
                 NAG_6: c.color_nag6}[nag]

        return pgn, color, info, indicadorInicial, liNAGs

    def gridPonValor(self, grid, fila, oColumna, valor):
        """
        Al a_adir los editores, pasa por aqui
        """
        pass
        # ~ #--------------------------------------------------------------------------------------------------------------------------------
        # ~ def gridColorTexto( self, fila, oColumna ):
        #~ analisis = self.gestor.pgn.analisis(fila, oColumna.clave)
        #~ if analisis:
        #~ mate = analisis.mate
        #~ if mate:
        #~ return self.colorBlanco
        #~ else:
        #~ puntos = analisis.puntos
        #~ if puntos > 0:
        #~ if puntos < 1000:
        #~ return self.colorPositivo.darker( 1000-puntos )
        #~ else:
        #~ return self.colorBlanco
        #~ else:
        #~ if puntos > -1000:
        #~ return self.colorNegativo.darker( -(-1000-puntos) )
        #~ else:
        #~ return self.colorBlanco

        #~ return None
        #~ #--------------------------------------------------------------------------------------------------------------------------------
        #~ def gridColorFondo( self, fila, oColumna ):
        #~ analisis = self.gestor.pgn.analisis(fila, oColumna.clave)
        #~ if analisis:
        #~ mate = analisis.mate
        #~ if mate:
        #~ if mate < 0:
        #~ return self.colorMateNegativo
        #~ else:
        #~ return self.colorMatePositivo
        #~ else:
        #~ puntos = analisis.puntos
        #~ if puntos > 0:
        #~ if puntos < 1000:
        #~ return self.colorPositivo.lighter( 1000-puntos )
        #~ else:
        #~ return self.colorPositivo
        #~ else:
        #~ if puntos > -1000:
        #~ return self.colorNegativo.lighter( -(-1000-puntos) )
        #~ else:
        #~ return self.colorNegativo

        #~ return None

    def keyPressEvent(self, event):
        self.teclaPulsada("V", event.key())

    def tableroWheelEvent(self, tablero, siAdelante):
        self.teclaPulsada("T", 16777236 if siAdelante else 16777234)

    def teclaPulsada(self, tipo, tecla):
        if self.procesandoEventos:
            QTUtil.refreshGUI()
            return
        self.procesandoEventos = True

        if tecla == self.gestor.teclaPanico:
            self.gestor.siTeclaPanico = True
        else:
            dic = QTUtil2.dicTeclas()
            if tecla in dic:
                if hasattr(self.gestor, "mueveJugada"):
                    self.gestor.mueveJugada(dic[tecla])
            elif tecla in (16777220, 16777221):  # intros
                fila, columna = self.pgn.posActual()
                if columna.clave != "NUMERO":
                    if hasattr(self.gestor, "analizaPosicion"):
                        self.gestor.analizaPosicion(fila, columna.clave)
            else:
                if hasattr(self.gestor, "controlTeclado"):
                    self.gestor.controlTeclado(tecla)
        self.procesandoEventos = False

    def pgnRefresh(self):
        self.pgn.refresh()

    def activaJuego(self, siActivar, siReloj, siAyudas=None):
        self.pgn.setVisible(siActivar)
        self.lbRevision.hide()
        if siAyudas is None:
            siAyudas = siActivar
        self.ayudasUD.setVisible(siAyudas)
        self.lbCredito.setVisible(siAyudas)
        self.btActivarTutor.setVisible(siActivar)
        self.lbRotulo1.setVisible(False)
        self.lbRotulo2.setVisible(False)
        self.lbRotulo3.setVisible(False)

        self.lbJugBlancas.setVisible(siReloj)
        self.lbJugNegras.setVisible(siReloj)
        self.lbRelojBlancas.setVisible(siReloj)
        self.lbRelojNegras.setVisible(siReloj)

    def ponDatosReloj(self, bl, rb, ng, rn):
        self.lbJugBlancas.altoMinimo(0)
        self.lbJugNegras.altoMinimo(0)

        self.lbJugBlancas.ponTexto(bl)
        self.lbJugNegras.ponTexto(ng)
        self.ponRelojBlancas(rb, "00:00")
        self.ponRelojNegras(rn, "00:00")

        QTUtil.refreshGUI()

        hb = self.lbJugBlancas.height()
        hn = self.lbJugNegras.height()
        if hb > hn:
            self.lbJugNegras.altoMinimo(hb)
        elif hb < hn:
            self.lbJugBlancas.altoMinimo(hn)

    def cambiaRotulosReloj(self, bl, ng):
        self.lbJugBlancas.ponTexto(bl)
        self.lbJugNegras.ponTexto(ng)

    def ponAyudas(self, puntos, siQuitarAtras=True):

        if puntos > 50:
            self.ayudasUD.setVisible(False)
            self.lbCredito.setVisible(False)
        else:
            self.ayudasUD.pon(puntos)

        if (puntos == 0) and siQuitarAtras:
            if k_atras in self.tb.liAcciones:
                self.dicTB[k_atras].setVisible(False)

    def quitaAyudas(self, siTambienTutorAtras, siQuitarAtras=True):
        self.ayudasUD.setVisible(False)
        self.lbCredito.setVisible(False)
        if siTambienTutorAtras:
            self.btActivarTutor.setVisible(False)
            if siQuitarAtras and (k_atras in self.tb.liAcciones):
                self.dicTB[k_atras].setVisible(False)

    def ponRotulo1(self, rotulo):
        if rotulo:
            self.lbRotulo1.ponTexto(rotulo)
            self.lbRotulo1.show()
        else:
            self.lbRotulo1.hide()
        return self.lbRotulo1

    def ponRotulo2(self, rotulo):
        if rotulo:
            self.lbRotulo2.ponTexto(rotulo)
            self.lbRotulo2.show()
        else:
            self.lbRotulo2.hide()
        return self.lbRotulo2

    def alturaRotulo3(self, px):
        self.lbRotulo3.altoFijo(px)

    def ponRotulo3(self, rotulo):
        if rotulo is not None:
            self.lbRotulo3.ponTexto(rotulo)
            self.lbRotulo3.show()
        else:
            self.lbRotulo3.hide()
        return self.lbRotulo3

    def ponRelojBlancas(self, tm, tm2):
        self.lbRelojBlancas.ponTexto(tm + '<br><FONT SIZE="-4">' + tm2)

    def ponRelojNegras(self, tm, tm2):
        self.lbRelojNegras.ponTexto(tm + '<br><FONT SIZE="-4">' + tm2)

    def creaCapturas(self):
        self.capturas = WCapturas.CapturaLista(self, self.tablero)
