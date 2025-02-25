# -*- coding: utf-8 -*-

NIVELBAK = 1

import os
import codecs
import operator

from PyQt4 import QtGui

from Code.Constantes import *
import Code.VarGen as VarGen
import Code.Traducir as Traducir
import Code.MotoresExternos as MotoresExternos
import Code.BaseConfig as BaseConfig

if VarGen.isLinux:
    import Code.EnginesLinux as Engines
else:
    import Code.EnginesWindows as Engines

import Code.Util as Util
import Code.CajonDesastre as CajonDesastre
import Code.TrListas as TrListas

LCFILEFOLDER = "./lc.folder"
LCBASEFOLDER = "./UsrData"

def activeFolder():
    if os.path.isfile(LCFILEFOLDER):
        f = open(LCFILEFOLDER)
        x = f.read().strip()
        f.close()
        if os.path.isdir(x):
            return x
    return LCBASEFOLDER

def isDefaultFolder():
    return activeFolder() == os.path.abspath(LCBASEFOLDER)

def changeFolder(nueva):
    if nueva:
        if os.path.abspath(nueva) == os.path.abspath(LCBASEFOLDER):
            return changeFolder(None)
        f = open(LCFILEFOLDER, "wb")
        f.write(nueva)
        f.close()
    else:
        Util.borraFichero(LCFILEFOLDER)

class Configuracion:
    def __init__(self, user):

        self.ponCarpetas(user)

        self.user = user

        self.siMain = user == ""

        self.id = Util.creaID()
        self.jugador = ""
        self.dirSalvados = ""
        self.dirPGN = ""
        self.dirJS = ""
        self.traductor = ""
        self.estilo = "Cleanlooks"
        self.vistaTutor = kTutorH

        self.efectosVisuales = True
        self.rapidezMovPiezas = 100
        self.guardarVariantesTutor = True

        self.siAtajosRaton = False  # predicitvo=True
        self.showCandidates = False

        self.siActivarCapturas = False
        self.siActivarInformacion = False

        self.tutorActivoPorDefecto = True

        self.version = ""

        self.elo = 0
        self.eloNC = 1600

        self.michelo = 1600
        self.micheloNC = 1600

        self.fics = 1200
        self.ficsNC = 1200

        self.fide = 1600
        self.fideNC = 1600

        self.siDGT = False

        self.coloresPGNdefecto()

        self.tamFontRotulos = 10
        self.anchoPGN = 283
        self.puntosPGN = 10
        self.altoFilaPGN = 22
        self.figurinesPGN = True

        self.showVariantes = False
        self.tipoMaterial = "D"

        self.familia = ""

        self.puntosMenu = 11
        self.boldMenu = False

        self.puntosTB = 11
        self.boldTB = False

        self.centipawns = False

        self.salvarGanados = False
        self.salvarPerdidos = False
        self.salvarAbandonados = False
        self.salvarFichero = ""

        self.salvarCSV = ""

        self.liTrasteros = []

        self.liFavoritos = []

        self.liPersonalidades = []

        self.dicRivales = Engines.leeRivales()

        self.rivalInicial = "rocinante" if VarGen.isLinux else "tarrasch"
        self.rival = self.buscaRival(self.rivalInicial)

        self.tutorInicial = "stockfish"
        self.tutor = self.buscaRival(self.tutorInicial)
        self.tutorMultiPV = 10 # 0: maximo
        self.tutorDifPts = 0
        self.tutorDifPorc = 0

        self.tiempoTutor = 3000

        self.siSuenaBeep = False
        self.siSuenaNuestro = False
        self.siSuenaJugada = False
        self.siSuenaResultados = False

        self.siNomPiezasEN = False

        self.voice = ""

        self.siAplazada = False

        self.grupos = BaseConfig.Grupos(self)

        self.grupos.nuevo("TarraschToy", 0, 1999, 0)
        self.grupos.nuevo("Bikjump", 2000, 2400, 600)
        self.grupos.nuevo("Greko", 2401, 2599, 1800)
        self.grupos.nuevo("Alaric", 2600, 2799, 3600)
        self.grupos.nuevo("Rybka", 2800, 3400, 6000)

    def start(self, version):
        self.lee()
        if version != self.version:
            CajonDesastre.compruebaCambioCarpetas(self)
            self.version = version
            self.graba()
        self.leeConfTableros()

    def changeActiveFolder(self, nueva):
        changeFolder(nueva)
        self.ponCarpetas(None)  # Siempre sera el principal
        CajonDesastre.compruebaCambioCarpetas(self)
        self.lee()

    def ponCarpetas(self, user):
        self.carpetaBase = activeFolder()

        self.carpetaUsers = "%s/users" % self.carpetaBase

        if user:
            Util.creaCarpeta(self.carpetaUsers)
            self.carpeta = "%s/users/%s" % (self.carpetaBase, user)
            Util.creaCarpeta(self.carpeta)
        else:
            Util.creaCarpeta(self.carpetaBase)
            self.carpeta = self.carpetaBase

        self.fichero = self.carpeta + "/lk70.pik"

        self.siPrimeraVez = not Util.existeFichero(self.fichero)

        Util.creaCarpeta(self.carpeta + "/confvid")
        self.plantillaVideo = self.carpeta + "/confvid/%s.video"

        self.ficheroSounds = "%s/sounds.pkd" % self.carpeta
        self.fichEstadElo = "%s/estad.pkli" % self.carpeta
        self.fichEstadMicElo = "%s/estadMic.pkli" % self.carpeta
        self.fichEstadFicsElo = "%s/estadFics.pkli" % self.carpeta
        self.fichEstadFideElo = "%s/estadFide.pkli" % self.carpeta
        self.ficheroBooks = "%s/books.lkv" % self.carpeta
        self.ficheroTrainBooks = "%s/booksTrain.lkv" % self.carpeta
        self.ficheroMate = "%s/mate.ddb" % self.carpeta
        self.ficheroMemoria = "%s/memo.pk" % self.carpeta
        self.ficheroMExternos = "%s/listaMotores.pkt" % self.carpeta
        self.ficheroRemoto = "%s/remoto.pke" % self.carpeta
        self.ficheroCliente = "%s/cliente.pke" % self.carpeta
        self.ficheroRemNueva = "%s/remnueva.pke" % self.carpeta
        self.ficheroEntMaquina = "%s/entmaquina.pke" % self.carpeta
        self.ficheroEntMaquinaConf = "%s/entmaquinaconf.pkd" % self.carpeta
        self.ficheroGM = "%s/gm.pke" % self.carpeta
        self.ficheroGMhisto = "%s/gmh.db" % self.carpeta
        self.ficheroPuntuacion = "%s/punt.pke" % self.carpeta
        self.ficheroDirSound = "%s/direc.pkv" % self.carpeta
        self.ficheroKibitzers = "%s/moscas.pkv" % self.carpeta
        self.ficheroEntAperturas = "%s/entaperturas.pkd" % self.carpeta
        self.ficheroEntAperturasPar = "%s/entaperturaspar.pkd" % self.carpeta
        self.ficheroPersAperturas = "%s/persaperturas.pkd" % self.carpeta
        self.ficheroAnalisis = "%s/paranalisis.pkd" % self.carpeta
        self.ficheroDailyTest = "%s/nivel.pkd" % self.carpeta
        self.ficheroTemas = "%s/themes.pkd" % self.carpeta
        self.dirPersonalTraining = "%s/Personal Training" % self.carpeta
        self.ficheroBMT = "%s/lucas.bmt" % self.carpeta
        self.ficheroPotencia = "%s/power.db" % self.carpeta
        self.ficheroPuente = "%s/bridge.db" % self.carpeta
        self.ficheroMoves = "%s/moves.dbl" % self.carpeta
        self.ficheroRecursos = "%s/recursos.dbl" % self.carpeta
        self.ficheroConfTableros = "%s/confTableros.pk" % self.carpeta
        self.ficheroBoxing = "%s/boxing.pk" % self.carpeta
        self.ficheroTrainings = "%s/trainings.pk" % self.carpeta
        self.ficheroHorses = "%s/horses.db" % self.carpeta
        self.ficheroBookGuide = "%s/Standard opening guide.pgo" % self.carpeta  # fix
        self.ficheroAnalisisBookGuide = "%s/analisisBookGuide.pkd" % self.carpeta  # fix
        self.ficheroLearnPGN = "%s/LearnPGN.db" % self.carpeta
        self.ficheroAlbumes = "%s/albumes.pkd" % self.carpeta
        self.ficheroPuntuaciones = "%s/hpoints.pkd" % self.carpeta

        self.ficheroSelectedPositions = "%s/Selected positions.fns" % self.dirPersonalTraining

        self.ficheroVariables = "%s/Variables.pk" % self.carpeta

        Util.creaCarpeta(self.dirPersonalTraining)

        self.ficheroDBgames = "%s/%s.lcg" % ( self.carpeta, _("Initial Database Games") )

        self.ficheroDBgamesFEN = "%s/%s.lcf" % ( self.carpeta, _("Positions database") )

        self.carpetaSTS = "%s/sts" % self.carpeta

    def setVoice(self):
        if self.voice:
            self.folderVoice = os.path.join( self.carpeta, "Voice", self.voice )
            self.folderVoiceWavs = os.path.join( self.folderVoice, "wavs" )
            self.folderVoiceHMM = os.path.join( self.folderVoice, "hmm" )
            self.folderVoiceLM = os.path.join( self.folderVoice, "lm" )
            if not os.path.isdir(self.folderVoice):
                os.makedirs(self.folderVoice)

            if not os.path.isdir(self.folderVoiceWavs):
                os.makedirs(self.folderVoiceWavs)
            self.ficheroVoice = "%s/trainingvoices.pkd" % self.folderVoice

    def compruebaBMT(self):
        if not Util.existeFichero(self.ficheroBMT):
            self.ficheroBMT = "%s/lucas.bmt" % self.carpeta

    def puntuacion(self):
        return self.grupos.puntuacion()

    def maxNivelCategoria(self, categoria):
        return self.rival.maxNivelCategoria(categoria)

    def limpia(self, nombre):
        self.elo = 0
        self.eloNC = 1600
        self.michelo = 1600
        self.micheloNC = 1600
        self.fics = 1200
        self.ficsNC = 1200
        self.fide = 1600
        self.fideNC = 1600
        self.grupos.limpia()
        self.id = Util.creaID()
        self.jugador = nombre
        self.dirSalvados = ""
        self.dirPGN = ""
        self.dirJS = ""
        self.liTrasteros = []

        self.salvarGanados = False
        self.salvarPerdidos = False
        self.salvarAbandonados = False
        self.salvarFichero = ""

        self.siActivarCapturas = False
        self.siActivarInformacion = False
        self.siAtajosRaton = False
        self.showCandidates = False

        self.salvarCSV = ""

        self.rival = self.buscaRival(self.rivalInicial)

    def buscaRival(self, clave, defecto=None):
        if clave in self.dicRivales:
            return self.dicRivales[clave]
        if defecto is None:
            defecto = self.rivalInicial
        return self.buscaRival(defecto)

    def buscaRivalExt(self, claveMotor):
        if claveMotor.startswith("*"):
            rival = MotoresExternos.buscaRivalExt(claveMotor)
            if rival is None:
                rival = self.buscaRival("critter")
        else:
            rival = self.buscaRival(claveMotor)
        return rival

    def buscaTutor(self, clave, defecto=None):
        if clave in self.dicRivales and self.dicRivales[clave].puedeSerTutor():
            return self.dicRivales[clave]

        listaMotoresExt = MotoresExternos.ListaMotoresExternos(self.ficheroMExternos)
        listaMotoresExt.leer()
        for motor in listaMotoresExt.liMotores:
            if clave == motor.alias:
                return MotoresExternos.ConfigMotor(motor)

        if defecto is None:
            defecto = self.tutorInicial
        return self.buscaRival(defecto)

    def buscaMotor(self, clave, defecto=None):
        if clave in self.dicRivales:
            return self.dicRivales[clave]

        listaMotoresExt = MotoresExternos.ListaMotoresExternos(self.ficheroMExternos)
        listaMotoresExt.leer()
        if clave.startswith("*"):
            clave = clave[1:]
        for motor in listaMotoresExt.liMotores:
            if clave == motor.alias:
                return MotoresExternos.ConfigMotor(motor)

        return self.buscaRival(defecto)

    def ayudaCambioTutor(self):
        li = []
        listaMotoresExt = MotoresExternos.ListaMotoresExternos(self.ficheroMExternos)
        listaMotoresExt.leer()
        for motor in listaMotoresExt.liMotores:
            if motor.multiPV > 10:
                li.append(( motor.alias, motor.alias + " *" ))
        for clave, cm in self.dicRivales.iteritems():
            if cm.puedeSerTutor():
                li.append((clave, cm.nombre))
        li = sorted(li, key=operator.itemgetter(1))
        li.insert(0, self.tutor.clave)
        return li

    def comboMotores(self):
        li = []
        for clave, cm in self.dicRivales.iteritems():
            li.append((cm.nombre, clave))
        return li

    def comboMotoresCompleto(self, siOrdenar=True):
        listaMotoresExt = MotoresExternos.ListaMotoresExternos(self.ficheroMExternos)
        listaMotoresExt.leer()
        liMotoresExt = []
        for motor in listaMotoresExt.liMotores:
            liMotoresExt.append(( motor.alias + "*", "*" + motor.alias ))

        li = self.comboMotores()
        li.extend(liMotoresExt)
        if siOrdenar:
            li = sorted(li, key=operator.itemgetter(0))
        return li

    def comboMotoresMultiPV10(self, minimo=10):  # %#
        listaMotoresExt = MotoresExternos.ListaMotoresExternos(self.ficheroMExternos)
        listaMotoresExt.leer()
        liMotores = []
        for motor in listaMotoresExt.liMotores:
            if motor.multiPV >= minimo:
                liMotores.append(( motor.alias + "*", "*" + motor.alias ))

        for clave, cm in self.dicRivales.iteritems():
            if cm.multiPV >= minimo:
                liMotores.append((cm.nombre, clave))

        li = sorted(liMotores, key=operator.itemgetter(0))
        return li

    def ayudaCambioCompleto(self, cmotor):
        li = []
        listaMotoresExt = MotoresExternos.ListaMotoresExternos(self.ficheroMExternos)
        listaMotoresExt.leer()
        for motor in listaMotoresExt.liMotores:
            li.append(( "*" + motor.alias, motor.alias + " *" ))
        for clave, cm in self.dicRivales.iteritems():
            li.append((clave, cm.nombre))
        li = sorted(li, key=operator.itemgetter(1))
        li.insert(0, cmotor)
        return li

    def estilos(self):

        li = [(x, x) for x in QtGui.QStyleFactory.keys()]
        li.insert(0, self.estilo)
        return li

    def coloresPGNdefecto(self):
        self.color_nag1 = "#0707FF"
        self.color_nag2 = "#FF7F00"
        self.color_nag3 = "#820082"
        self.color_nag4 = "#FF0606"
        self.color_nag5 = "#008500"
        self.color_nag6 = "#ECC70A"

    def graba(self, aplazamiento=None):

        dic = {}
        dic["VERSION"] = self.version
        dic["ID"] = self.id
        dic["JUGADOR"] = self.jugador
        dic["ESTILO"] = self.estilo
        dic["TIEMPOTUTOR"] = self.tiempoTutor

        dic["SIBEEP"] = self.siSuenaBeep
        dic["SISUENANUESTRO"] = self.siSuenaNuestro
        dic["SISUENAJUGADA"] = self.siSuenaJugada
        dic["SISUENARESULTADOS"] = self.siSuenaResultados
        dic["GUARDAR_VARIANTES"] = self.guardarVariantesTutor

        dic["DIRSALVADOS"] = self.dirSalvados
        dic["DIRPGN"] = self.dirPGN
        dic["DIRJS"] = self.dirJS
        dic["TRADUCTOR"] = self.traductor
        dic["SALVAR_FICHERO"] = self.salvarFichero
        dic["SALVAR_GANADOS"] = self.salvarGanados
        dic["SALVAR_PERDIDOS"] = self.salvarPerdidos
        dic["SALVAR_ABANDONADOS"] = self.salvarAbandonados
        dic["SALVAR_CSV"] = self.salvarCSV
        dic["VISTA_TUTOR"] = self.vistaTutor
        dic["EFECTOS_VISUALES"] = self.efectosVisuales
        dic["RAPIDEZMOVPIEZAS"] = self.rapidezMovPiezas
        dic["ATAJOS_RATON"] = self.siAtajosRaton
        dic["SHOW_CANDIDATES"] = self.showCandidates
        dic["ACTIVAR_CAPTURAS"] = self.siActivarCapturas
        dic["ACTIVAR_INFORMACION"] = self.siActivarInformacion
        dic["RIVAL"] = self.rival.clave
        dic["TUTOR"] = self.tutor.clave
        dic["TUTOR_DIFPTS"] = self.tutorDifPts
        dic["TUTOR_DIFPORC"] = self.tutorDifPorc
        dic["TUTORACTIVODEFECTO"] = self.tutorActivoPorDefecto
        dic["TUTOR_MULTIPV"] = self.tutorMultiPV

        dic["SINOMPIEZASEN"] = self.siNomPiezasEN

        dic["DBGAMES"] = Util.dirRelativo(self.ficheroDBgames)
        dic["DBGAMESFEN"] = Util.dirRelativo(self.ficheroDBgamesFEN)

        dic["BOOKGUIDE"] = self.ficheroBookGuide

        dic["SIDGT"] = self.siDGT

        dic["FICHEROBMT"] = self.ficheroBMT

        dic["FAMILIA"] = self.familia

        dic["PUNTOSMENU"] = self.puntosMenu
        dic["BOLDMENU"] = self.boldMenu

        dic["PUNTOSTB"] = self.puntosTB
        dic["BOLDTB"] = self.boldTB

        dic["COLOR_NAG1"] = self.color_nag1
        dic["COLOR_NAG2"] = self.color_nag2
        dic["COLOR_NAG3"] = self.color_nag3
        dic["COLOR_NAG4"] = self.color_nag4
        dic["COLOR_NAG5"] = self.color_nag5
        dic["COLOR_NAG6"] = self.color_nag6

        dic["TAMFONTROTULOS"] = self.tamFontRotulos
        dic["ANCHOPGN"] = self.anchoPGN
        dic["PUNTOSPGN"] = self.puntosPGN
        dic["ALTOFILAPGN"] = self.altoFilaPGN
        dic["FIGURINESPGN"] = self.figurinesPGN

        dic["SHOW_VARIANTES"] = self.showVariantes
        dic["TIPOMATERIAL"] = self.tipoMaterial

        dic["ELO"] = self.elo
        dic["ELONC"] = self.eloNC
        dic["MICHELO"] = self.michelo
        dic["MICHELONC"] = self.micheloNC
        dic["FICS"] = self.fics
        dic["FICSNC"] = self.ficsNC
        dic["FIDE"] = self.fide
        dic["FIDENC"] = self.fideNC
        dic["TRASTEROS"] = self.liTrasteros
        dic["FAVORITOS"] = self.liFavoritos
        dic["PERSONALIDADES"] = self.liPersonalidades

        dic["CENTIPAWNS"] = self.centipawns

        dic["VOICE"] = self.voice

        for clave, rival in self.dicRivales.iteritems():
            dic["RIVAL_%s" % clave] = rival.graba()
        if aplazamiento:
            dic["APLAZAMIENTO"] = Util.dic2txt(aplazamiento)
        Util.guardaDIC(dic, self.fichero)

        self.releeTRA()

    def lee(self):
        self.siAplazada = False

        if not os.path.isfile(self.fichero):
            CajonDesastre.compruebaCambioVersion(self)

        else:
            fbak = self.fichero + ".CP.%d" % NIVELBAK
            if not Util.existeFichero(fbak):
                Util.copiaFichero(self.fichero, fbak)
            dic = Util.recuperaDIC(self.fichero)
            if dic:
                dg = dic.get
                self.id = dic["ID"]
                self.version = dic.get("VERSION", "")
                self.jugador = dic["JUGADOR"]
                self.estilo = dg("ESTILO", "Cleanlooks")
                self.tiempoTutor = dic["TIEMPOTUTOR"]
                if self.tiempoTutor == 0:
                    self.tiempoTutor = 3000

                self.siSuenaBeep = dic["SIBEEP"]
                self.siSuenaJugada = dg("SISUENAJUGADA", False)
                self.siSuenaResultados = dg("SISUENARESULTADOS", False)
                self.siSuenaNuestro = dg("SISUENANUESTRO", False)

                self.efectosVisuales = dg("EFECTOS_VISUALES", True)
                self.rapidezMovPiezas = dg("RAPIDEZMOVPIEZAS", self.rapidezMovPiezas)
                self.siAtajosRaton = dg("ATAJOS_RATON", False)
                self.showCandidates = dg("SHOW_CANDIDATES", False)
                self.siActivarCapturas = dg("ACTIVAR_CAPTURAS", self.siActivarCapturas)
                self.siActivarInformacion = dg("ACTIVAR_INFORMACION", self.siActivarInformacion)
                self.guardarVariantesTutor = dg("GUARDAR_VARIANTES", True)

                self.dirSalvados = dic["DIRSALVADOS"]
                self.dirPGN = dg("DIRPGN", "")
                self.dirJS = dg("DIRJS", "")
                self.traductor = dic["TRADUCTOR"].lower()
                self.salvarFichero = dic["SALVAR_FICHERO"]
                self.salvarGanados = dic["SALVAR_GANADOS"]
                self.salvarPerdidos = dic["SALVAR_PERDIDOS"]
                self.salvarAbandonados = dg("SALVAR_ABANDONADOS", False)
                self.salvarCSV = dg("SALVAR_CSV", "")
                self.vistaTutor = dg("VISTA_TUTOR", kTutorH)
                self.rival = self.buscaRival(dic["RIVAL"], self.rivalInicial)
                self.tutor = self.buscaTutor(dic["TUTOR"], self.tutorInicial)

                self.siNomPiezasEN = dg("SINOMPIEZASEN", self.siNomPiezasEN)

                self.tutorDifPts = dg("TUTOR_DIFPTS", 0)
                self.tutorDifPorc = dg("TUTOR_DIFPORC", 0)
                self.tutorActivoPorDefecto = dg("TUTORACTIVODEFECTO", True)
                self.tutorMultiPV = dg("TUTOR_MULTIPV", "MX")

                fich = dg("DBGAMES", self.ficheroDBgames)
                if os.path.isfile(fich):
                    self.ficheroDBgames = fich
                fich = dg("DBGAMESFEN", self.ficheroDBgamesFEN)
                if os.path.isfile(fich):
                    self.ficheroDBgamesFEN = fich
                fich = dg("BOOKGUIDE", self.ficheroBookGuide)
                if os.path.isfile(fich):
                    self.ficheroBookGuide = fich

                self.elo = dg("ELO", 0)
                self.eloNC = dg("ELONC", 1600)
                self.michelo = dg("MICHELO", self.michelo)
                self.micheloNC = dg("MICHELONC", self.micheloNC)
                self.fics = dg("FICS", self.fics)
                self.ficsNC = dg("FICSNC", self.ficsNC)
                self.fide = dg("FIDE", self.fide)
                self.fideNC = dg("FIDENC", self.fideNC)

                self.siDGT = dg("SIDGT", False)

                self.familia = dg("FAMILIA", self.familia)

                self.puntosMenu = dg("PUNTOSMENU", self.puntosMenu)
                self.boldMenu = dg("BOLDMENU", self.boldMenu)

                self.puntosTB = dg("PUNTOSTB", self.puntosTB)
                self.boldTB = dg("BOLDTB", self.boldTB)

                self.color_nag1 = dg("COLOR_NAG1", self.color_nag1)
                self.color_nag2 = dg("COLOR_NAG2", self.color_nag2)
                self.color_nag3 = dg("COLOR_NAG3", self.color_nag3)
                self.color_nag4 = dg("COLOR_NAG4", self.color_nag4)
                self.color_nag5 = dg("COLOR_NAG5", self.color_nag5)
                self.color_nag6 = dg("COLOR_NAG6", self.color_nag6)
                self.tamFontRotulos = dg("TAMFONTROTULOS", self.tamFontRotulos)
                self.anchoPGN = dg("ANCHOPGN", self.anchoPGN)
                self.puntosPGN = dg("PUNTOSPGN", self.puntosPGN)
                self.altoFilaPGN = dg("ALTOFILAPGN", self.altoFilaPGN)
                self.figurinesPGN = dg("FIGURINESPGN", False)
                self.showVariantes = dg("SHOW_VARIANTES", False)
                self.tipoMaterial = dg("TIPOMATERIAL", self.tipoMaterial)

                self.ficheroBMT = dg("FICHEROBMT", self.ficheroBMT)

                self.liTrasteros = dg("TRASTEROS", [])
                self.liFavoritos = dg("FAVORITOS", [])
                self.liPersonalidades = dg("PERSONALIDADES", [])

                self.centipawns = dg("CENTIPAWNS", self.centipawns)

                self.voice = dg("VOICE", self.voice)

                for k in dic.keys():
                    if k.startswith("RIVAL_"):
                        claveK = k[6:]
                        for clave, rival in self.dicRivales.iteritems():
                            if rival.clave == claveK:
                                rival.lee(dic[k])
                if "APLAZAMIENTO" in dic:
                    self.siAplazada = True
                    try:
                        self.aplazamiento = Util.txt2dic(dic["APLAZAMIENTO"])
                    except:
                        self.aplazamiento = None
                        self.siAplazada = False
                    self.graba()

        self.dicTrad = {'english': "en", 'español': "es", 'francais': "fr",
                        'deutsch': "de", 'portuguese': "pt", 'russian': "ru",
                        "italiano": "it", "azeri": "az", "català": "ca",
                        "vietnamese": "vi", "swedish": "sv"}

        # Si viene de la instalacion
        for k, v in self.dicTrad.iteritems():
            if os.path.isfile(v + '.pon'):
                self.traductor = v
                self.graba()
                os.remove(v + '.pon')
        # Versiones antiguas
        if self.traductor in self.dicTrad:
            self.traductor = self.dicTrad[self.traductor]

        self.releeTRA()

        TrListas.ponPiecesLNG(self.siNomPiezasEN or self.traductor == "en")

        self.setVoice()

    def releeTRA(self):
        Traducir.install(self.traductor)

    def eloActivo(self, siModoCompetitivo):
        return self.elo if siModoCompetitivo else self.eloNC

    def miceloActivo(self, siModoCompetitivo):
        return self.michelo if siModoCompetitivo else self.micheloNC

    def ficsActivo(self, siModoCompetitivo):
        return self.fics if siModoCompetitivo else self.ficsNC

    def fideActivo(self, siModoCompetitivo):
        return self.fide if siModoCompetitivo else self.fideNC

    def ponEloActivo(self, elo, siModoCompetitivo):
        if siModoCompetitivo:
            self.elo = elo
        else:
            self.eloNC = elo

    def ponMiceloActivo(self, elo, siModoCompetitivo):
        if siModoCompetitivo:
            self.michelo = elo
        else:
            self.micheloNC = elo

    def ponFicsActivo(self, elo, siModoCompetitivo):
        if siModoCompetitivo:
            self.fics = elo
        else:
            self.ficsNC = elo

    def ponFideActivo(self, elo, siModoCompetitivo):
        if siModoCompetitivo:
            self.fide = elo
        else:
            self.fideNC = elo

    def listaTraducciones(self):
        li = []
        dlang = "Locale"
        for uno in Util.listdir(dlang):
            fini = os.path.join(dlang, uno, "lang.ini")
            if os.path.isfile(fini):
                try:
                    dic = Util.iniBase8dic(fini)
                    if "NAME" in dic:
                        li.append((uno, dic["NAME"], dic.get( "%", "100")))
                except:
                    pass
        li = sorted(li, key=lambda lng: lng[0])
        return li

    def listaMotoresInternos(self):
        li = [v for k, v in self.dicRivales.iteritems()]
        li = sorted(li, key=lambda cm: cm.nombre)
        return li

    def listaMotoresExternos(self):
        listaMotoresExt = MotoresExternos.ListaMotoresExternos(self.ficheroMExternos)
        listaMotoresExt.leer()
        li = sorted(listaMotoresExt.liMotores, key=lambda cm: cm.alias)
        return li

    def listaMotores(self):
        li = []
        for k, v in self.dicRivales.iteritems():
            li.append(( v.nombre, v.autor, v.url ))
        li = sorted(li, key=operator.itemgetter(0))
        return li

    def listaMotoresCompleta(self):
        li = self.listaMotores()
        li.append(( "Greko 7.1", "Vladimir Medvedev", "http://greko.110mb.com/index.html"))
        li = sorted(li, key=operator.itemgetter(0))
        return li

    def ficheroTemporal(self, extension):
        dirTmp = os.path.join(self.carpeta, "tmp")
        return Util.ficheroTemporal(dirTmp, extension)

    def limpiaTemporal(self):
        try:
            dirTmp = os.path.join(self.carpeta, "tmp")
            for f in Util.listdir(dirTmp):
                Util.borraFichero(os.path.join(dirTmp, f))
        except:
            pass

    def leeVariables(self, nomVar):
        db = Util.DicSQL(self.ficheroVariables)
        resp = db[nomVar]
        db.close()
        return resp if resp else {}

    def escVariables(self, nomVar, dicValores):
        db = Util.DicSQL(self.ficheroVariables)
        db[nomVar] = dicValores
        db.close()

    def leeConfTableros(self):
        db = Util.DicSQL(self.ficheroConfTableros)
        self.dicConfTableros = db.asDictionary()
        db.close()

    def cambiaConfTablero(self, confTablero):
        xid = confTablero._id
        if xid:
            db = Util.DicSQL(self.ficheroConfTableros)
            self.dicConfTableros[xid] = db[xid] = confTablero.graba()
            db.close()
            self.leeConfTableros()

    def confTablero(self, xid, tamDef, padre="BASE"):
        if xid == "BASE":
            ct = BaseConfig.ConfigTablero(xid, tamDef)
        else:
            ct = BaseConfig.ConfigTablero(xid, tamDef, padre=padre)
            ct.anchoPieza(tamDef)

        if xid in self.dicConfTableros:
            ct.lee(self.dicConfTableros[xid])
        else:
            db = Util.DicSQL(self.ficheroConfTableros)
            self.dicConfTableros[xid] = db[xid] = ct.graba()
            db.close()

        ct._anchoPiezaDef = tamDef

        return ct

    def listVoices(self):
        base = "Voice"
        li = [x for x in os.listdir(base) if os.path.isdir(os.path.join(base,x))]
        lista = [(_("Disabled"), "")]

        for cp in li:
            ini = os.path.join(base,cp,"config.ini")
            if os.path.isfile(ini):
                with codecs.open(ini, "r", "utf-8") as f:
                    for linea in f:
                        if linea.startswith("VOICE"):
                            lista.append( (linea.split("=")[1].strip(), cp) )
        return lista

    def dicMotoresFixedElo(self):
        return Engines.dicMotoresFixedElo()

        # ~ if __name__ == "__main__":
        #~ os.chdir( ".." )
        #~ conf = Configuracion()
        #~ prilk( conf.listaMotores() )

        #~ for g in conf.grupos.liGrupos:
        #~ p rint g.nombre
        #~ for cm in g.liRivales:
        # p rint "     ", cm.elo, "-", cm.nombre, "-", cm.autor, "-", cm.url
