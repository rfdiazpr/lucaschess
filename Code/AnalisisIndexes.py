import Code.VarGen as VarGen
import Code.SAK as SAK

def calc_formula(cual, cp, mrm):  # , limit=200.0):
    f = open("./IntFiles/Formulas/%s.formula" % cual, "rb")
    formula = f.read()
    f.close()
    piew = pieb = 0
    mat = 0.0
    matw = matb = 0.0
    dmat = {"k": 3.0, "q": 9.9, "r": 5.5, "b": 3.5, "n": 3.1, "p": 1.0}
    for k, v in cp.casillas.iteritems():
        if v:
            m = dmat[v.lower()]
            mat += m
            if v.isupper():
                piew += 1
                matw += m
            else:
                pieb += 1
                matb += m
    sak = SAK.sak
    sak.setFEN(cp.fen())
    mov = len(sak.getMoves())
    base = mrm.liMultiPV[0].puntosABS()
    siBlancas = cp.siBlancas

    gmo34 = gmo68 = gmo100 = 0
    for rm in mrm.liMultiPV:
        dif = abs(rm.puntosABS() - base)
        if dif < 34:
            gmo34 += 1
        elif dif < 68:
            gmo68 += 1
        elif dif < 101:
            gmo100 += 1
    gmo = float(gmo34) + float(gmo68) ** 0.8 + float(gmo100) ** 0.5
    plm = (cp.jugadas - 1) * 2
    if not siBlancas:
        plm += 1

    li = (  ("xpiec", piew if siBlancas else pieb),
            ("xpie", piew + pieb),
            ("xmov", mov),
            ("xeval", base if siBlancas else -base),
            ("xstm", +1 if siBlancas else -1),
            ("xplm", plm),
    )
    for k, v in li:
        if k in formula:
            formula = formula.replace(k, "%d.0" % v)
    li = (  ("xgmo", gmo),
            ("xmat", mat),
            ("xpow", matw if siBlancas else matb),
    )
    for k, v in li:
        if k in formula:
            formula = formula.replace(k, "%f" % v)
    if "xcompl" in formula:
        formula = formula.replace("xcompl", "%f" % calc_formula("complexity", cp, mrm))
    try:
        x = float(eval(formula))
        # if x < 0.0:
        # x = -x
        # if x > limit:
        # x = limit
        return x
    except:
        return 0.0

def lb_levels(x):
    if x < 0:
        txt = _("Extremely low")
    elif x < 5.0:
        txt = _("Very low")
    elif x < 15.0:
        txt = _("Low")
    elif x < 35.0:
        txt = _("Moderate")
    elif x < 55.0:
        txt = _("High")
    elif x < 85.0:
        txt = _("Very high")
    else:
        txt = _("Extreme")
    return txt

def txt_levels(x):
    return "%s (%.02f%%)" % (lb_levels(x), x)

def txt_formula(titulo, funcion, cp, mrm):
    x = funcion(cp, mrm)
    return "%s: %s" % (titulo, txt_levels(x))

def tp_formula(titulo, funcion, cp, mrm):
    x = funcion(cp, mrm)
    return titulo, x, lb_levels(x)

def calc_complexity(cp, mrm):
    return calc_formula("complexity", cp, mrm)

def get_complexity(cp, mrm):
    return txt_formula(_("Complexity"), calc_complexity, cp, mrm)

def tp_complexity(cp, mrm):
    return tp_formula(_("Complexity"), calc_complexity, cp, mrm)

def calc_winprobability(cp, mrm):
    return calc_formula("winprobability", cp, mrm)  # , limit=100.0)

def get_winprobability(cp, mrm):
    return txt_formula(_("Win probability"), calc_winprobability, cp, mrm)

def tp_winprobability(cp, mrm):
    return tp_formula(_("Win probability"), calc_winprobability, cp, mrm)

def calc_narrowness(cp, mrm):
    return calc_formula("narrowness", cp, mrm)

def get_narrowness(cp, mrm):
    return txt_formula(_("Narrowness"), calc_narrowness, cp, mrm)

def tp_narrowness(cp, mrm):
    return tp_formula(_("Narrowness"), calc_narrowness, cp, mrm)

def calc_efficientmobility(cp, mrm):
    x = calc_formula("efficientmobility", cp, mrm)
    return x

def get_efficientmobility(cp, mrm):
    return txt_formula(_("Efficient mobility"), calc_efficientmobility, cp, mrm)

def tp_efficientmobility(cp, mrm):
    return tp_formula(_("Efficient mobility"), calc_efficientmobility, cp, mrm)

def calc_piecesactivity(cp, mrm):
    return calc_formula("piecesactivity", cp, mrm)

def get_piecesactivity(cp, mrm):
    return txt_formula(_("Pieces activity"), calc_piecesactivity, cp, mrm)

def tp_piecesactivity(cp, mrm):
    return tp_formula(_("Pieces activity"), calc_piecesactivity, cp, mrm)

def calc_exchangetendency(cp, mrm):
    return calc_formula("simplification", cp, mrm)

def get_exchangetendency(cp, mrm):
    return txt_formula(_("Exchange tendency"), calc_exchangetendency, cp, mrm)

def tp_exchangetendency(cp, mrm):
    return tp_formula(_("Exchange tendency"), calc_exchangetendency, cp, mrm)

def calc_positionalpressure(cp, mrm):
    return calc_formula("positionalpressure", cp, mrm)

def get_positionalpressure(cp, mrm):
    return txt_formula(_("Positional pressure"), calc_positionalpressure, cp, mrm)

def tp_positionalpressure(cp, mrm):
    return tp_formula(_("Positional pressure"), calc_positionalpressure, cp, mrm)

def calc_materialasymmetry(cp, mrm):
    return calc_formula("materialasymmetry", cp, mrm)

def get_materialasymmetry(cp, mrm):
    return txt_formula(_("Material asymmetry"), calc_materialasymmetry, cp, mrm)

def tp_materialasymmetry(cp, mrm):
    return tp_formula(_("Material asymmetry"), calc_materialasymmetry, cp, mrm)

# #=========================================================================================

def calc_gamestage(cp, mrm):
    return calc_formula("gamestage", cp, mrm)

def get_gamestage(cp, mrm):
    xgst = calc_gamestage(cp, mrm)
    if xgst >= 50:
        gst = 1
    elif 50 > xgst >= 40:
        gst = 2
    elif 40 > xgst >= 10:
        gst = 3
    elif 10 > xgst >= 5:
        gst = 4
    else:
        gst = 5
    dic = {1: _("Opening"),
           2: _("Transition to middlegame"),
           3: _("Middlegame"),
           4: _("Transition to endgame"),
           5: _("Endgame")}
    return dic[gst]

def tp_gamestage(cp, mrm):
    return _("Game stage"), calc_gamestage(cp, mrm), get_gamestage(cp, mrm)

def genIndexes(partida):
    average = {True: 0, False: 0}
    domination = {True: 0, False: 0}
    complexity = {True: 0.0, False: 0.0}
    narrowness = {True: 0.0, False: 0.0}
    efficientmobility = {True: 0.0, False: 0.0}
    piecesactivity = {True: 0.0, False: 0.0}
    exchangetendency = {True: 0.0, False: 0.0}
    n = {True: 0, False: 0}
    for jg in partida.liJugadas:
        if hasattr(jg, "analisis"):
            if jg.analisis:
                mrm, pos = jg.analisis
                siB = jg.siBlancas()
                pts = mrm.liMultiPV[pos].puntosABS()
                if pts > 100:
                    domination[siB] += 1
                elif pts < -100:
                    domination[not siB] += 1
                average[siB] += mrm.liMultiPV[0].puntosABS() - pts
                if not hasattr(jg, "complexity"):
                    cp = jg.posicionBase
                    jg.complexity = calc_complexity(cp, mrm)
                    jg.winprobability = calc_winprobability(cp, mrm)
                    jg.narrowness = calc_narrowness(cp, mrm)
                    jg.efficientmobility = calc_efficientmobility(cp, mrm)
                    jg.piecesactivity = calc_piecesactivity(cp, mrm)
                    jg.exchangetendency = calc_exchangetendency(cp, mrm)
                complexity[siB] += jg.complexity
                narrowness[siB] += jg.narrowness
                efficientmobility[siB] += jg.efficientmobility
                piecesactivity[siB] += jg.piecesactivity
                n[siB] += 1
                exchangetendency[siB] += jg.exchangetendency

    t = n[True] + n[False]
    for x in (True, False):
        b1 = n[x]
        if b1:
            average[x] = average[x] * 1.0 / b1
            complexity[x] = complexity[x] * 1.0 / b1
            narrowness[x] = narrowness[x] * 1.0 / b1
            efficientmobility[x] = efficientmobility[x] * 1.0 / b1
            piecesactivity[x] = piecesactivity[x] * 1.0 / b1
            exchangetendency[x] = exchangetendency[x] * 1.0 / b1
        if t:
            domination[x] = domination[x] * 100.0 / t
    complexityT = (complexity[True] + complexity[False]) / 2.0
    narrownessT = (narrowness[True] + narrowness[False]) / 2.0
    efficientmobilityT = (efficientmobility[True] + efficientmobility[False]) / 2.0
    piecesactivityT = (piecesactivity[True] + piecesactivity[False]) / 2.0
    exchangetendencyT = (exchangetendency[True] + exchangetendency[False]) / 2.0

    if not VarGen.configuracion.centipawns:
        average[True] /= 100.0
        average[False] /= 100.0
    averageT = (average[True] + average[False]) / 2.0

    cw = _("White")
    cb = _("Black")
    ct = _("Total")
    cpt = " " + _("pts")
    xac = txt_levels

    inicio = '<tr><td align="center">%s</td>'
    resto = '<td align="center">%s</td><td align="center">%s</td><td align="center">%s</td></tr>'
    plantillaD = inicio + resto % ("%.02f%%", "%.02f%%", "-")
    plantillaL = inicio + resto % ("%.02f%s", "%.02f%s", "%.02f%s")
    plantillaC = inicio + resto % ("%s", "%s", "%s")
    # plantillaP = inicio + resto%("%.02f%%", "%.02f%%", "%.02f%%")

    cab = (plantillaC % ( _("Result of analysis"), cw, cb, ct )).replace("<td", "<th")
    txt = plantillaL % (_("Average lost scores"), average[True], cpt, average[False], cpt, averageT, cpt)
    txt += plantillaD % (_("Domination"), domination[True], domination[False])
    txt += plantillaC % (_("Complexity"), xac(complexity[True]), xac(complexity[False]), xac(complexityT))
    txt += plantillaC % (
        _("Efficient mobility"), xac(efficientmobility[True]), xac(efficientmobility[False]), xac(efficientmobilityT) )
    txt += plantillaC % ( _("Narrowness"), xac(narrowness[True]), xac(narrowness[False]), xac(narrownessT) )
    txt += plantillaC % (
        _("Pieces activity"), xac(piecesactivity[True]), xac(piecesactivity[False]), xac(piecesactivityT) )
    txt += plantillaC % (
        _("Exchange tendency"), xac(exchangetendency[True]), xac(exchangetendency[False]), xac(exchangetendencyT) )

    txtHTML = '<table border="1" cellpadding="5" cellspacing="1" >%s%s</table>' % (cab, txt)
    # Analisis.csv_formula(partida)
    # QTUtil2.mensaje( gestor.pantalla, "Created michele.csv" )

    plantillaD = "%s:\n" + cw + "= %.02f%s " + cb + "= %.02f%s\n"
    plantillaL = "%s:\n" + cw + "= %.02f%s " + cb + "= %.02f%s " + ct + "= %.02f%s\n"
    plantillaC = "%s:\n" + cw + "= %s " + cb + "= %s " + ct + "= %s\n"
    # plantillaP = "%s:\n" + cw +"= %.02f%% " + cb + "= %.02f%% "+ ct + "= %.02f%%\n"

    txt = "%s:\n" % _("Result of analysis")
    txt += plantillaL % (_("Average lost scores"), average[True], cpt,
                         average[False], cpt,
                         averageT, cpt)
    txt += plantillaD % (_("Domination"), domination[True], "%", domination[False], "%")
    txt += plantillaC % (_("Complexity"), xac(complexity[True]),
                         xac(complexity[False]),
                         xac(complexityT))
    txt += plantillaC % ( _("Narrowness"), xac(narrowness[True]), xac(narrowness[False]), xac(narrownessT) )
    txt += plantillaC % (_("Efficient mobility"), xac(efficientmobility[True]), xac(efficientmobility[False]),
                         xac(efficientmobilityT) )
    txt += plantillaC % (
        _("Pieces activity"), xac(piecesactivity[True]), xac(piecesactivity[False]), xac(piecesactivityT) )
    txt += plantillaC % (
        _("Exchange tendency"), xac(exchangetendency[True]), xac(exchangetendency[False]), xac(exchangetendencyT) )
    txtRAW = txt

    # if QTUtil2.pregunta(gestor.pantalla, "%s\n\n\n%s" % (txt, _("Add this text to the last move analyzed?") )):

    # jg = partida.jugada(nUlt)
    # if jg.comentario:
    # jg.comentario += " " + txt
    # else:
    # jg.comentario = txt

    # Html.grafAnalisis(partida)
    return txtHTML, txtRAW
