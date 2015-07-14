# -*- coding: utf-8 -*-
from pycobot.pycobot import BaseModel
from peewee.peewee import CharField, IntegerField
import json
import urllib.request
import _thread
import time


class recentchanges:
    def __init__(self, core, client):
        try:
            MonitorWiki2.create_table()
        except:
            pass

        core.addCommandHandler("addwiki", self, cpriv=3,
        chelp="Añade una wiki al monitoreo. Sintaxis: addwiki <canal> <wiki>")
        core.addCommandHandler("delwiki", self, cpriv=3,
        chelp="Elimina una wiki del monitoreo. Sintaxis:"
            " delwiki <canal> <wiki>")
        core.addCommandHandler("listwikis", self, cpriv=1,
        chelp="Lista las wikis que se están monitoreando.")

        core.addCommandHandler("monitoreo", self, cpriv=5,
        chelp="Activa o desactiva el monitoreo. Sintaxis: monitoreo <on/off>")

        #core.addTimeHandler(1, self, "monitor")
        self.monitoreoc = True
        self.lts = {}

        self.wikis = MonitorWiki2.select()
        self.activwikis = {}
        self.bot = core

        core.addHandler("welcome", self, "addstuff")

    def addstuff(self, client, ev):
        for wiki in self.wikis:
            self.activwikis[wiki.wiki] = True
            _thread.start_new_thread(self.monitorow, (self.bot, client, wiki))

    def listwikis(self, bot, cli, ev):
        wikis = MonitorWiki2.select()
        for wiki in wikis:
            cli.privmsg(ev.target, "\2{0} - {1}".format(wiki.wid, wiki.wiki))

    def addwiki(self, bot, cli, ev):
        if not len(ev.splitd) > 1:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros")
        c = MonitorWiki2.get(MonitorWiki2.wiki == ev.splitd[1])
        if c is False:
            ch = []
            ch.append(ev.splitd[0])
            MonitorWiki2.create(wiki=ev.splitd[1], chans=json.dumps(ch))
            self.activwikis[ev.splitd[1]] = True
            c = MonitorWiki2.get(MonitorWiki2.wiki == ev.splitd[1])
            _thread.start_new_thread(self.monitorow, (bot, cli, c))
            cli.privmsg(ev.target, "Se ha empezado a monitorear"
                    " \2{0}\2 en \2{1}".format(ev.splitd[1], ev.splitd[0]))
        else:
            for chan in c.chans:
                if chan == ev.splitd[0]:
                    cli.privmsg(ev.target, "\00304Error\003: Ya se está monito"
                        "reando esa wiki!")
                    return 1
            chans = json.loads(c.chans)
            chans.append(ev.splitd[0])
            c.chans = json.dumps(chans)
            c.save()
            cli.privmsg(ev.target, "Se ha empezado a monitorear"
                    " \2{0}\2 en \2{1}".format(ev.splitd[1], ev.splitd[0]))

    def delwiki(self, bot, cli, ev):
        if not len(ev.splitd) > 1:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parametros")
        c = MonitorWiki2.get(MonitorWiki2.wiki == ev.splitd[1])
        chans = json.loads(c.chans)
        if c is not False and chans == [ev.splitd[0]]:
            c.delete_instance()
            cli.privmsg(ev.target, "Se ha dejado de monitorear"
                    " \2{0}".format(ev.splitd[1]))
            del self.activwikis[ev.splitd[1]]
        else:
            for a, chan in enumerate(c.chans):
                if chan == ev.splitd[0]:
                    del chans[a]
                    c.chans = json.dumps(chans)
                    c.save()
                    cli.privmsg(ev.target, "Se ha dejado de monitorear"
                    " \2{0}\2 en \2{1}".format(ev.splitd[1], ev.splitd[0]))
                    return 1
            cli.privmsg(ev.target, "\00304Error\003: Esa wiki no se está monit"
            "oreando!")
            return 0
        self.wikis = MonitorWiki2.select()

    def monitoreo(self, bot, cli, ev):
        if len(ev.splitd) == 0:
            cli.privmsg(ev.target, "\00304Error\003: Faltan parámetros")

        if ev.splitd[0] == "on" or ev.splitd[0] == "si":
            self.monitoreoc = True
        elif ev.splitd[0] == "off" or ev.splitd[0] == "no":
            self.monitoreoc = False
        self.wikis = MonitorWiki2.select()

    #def monitor(self, bot, cli):
    #    for wiki in self.wikis:
    #        _thread.start_new_thread(self.monitorow, (bot, cli, wiki))

    def monitorow(self, bot, cli, wiki):
        try:
            self.monitoro(bot, cli, wiki)
        except:
            # print(k)
            self.monitoro(bot, cli, wiki)

    def monitoro(self, bot, cli, wiki):
        while self.activwikis[wiki.wiki]:
            if bot.is_loaded("recentchanges") is False:
                continue  # anti-crash?
            time.sleep(0.1)
            if self.monitoreoc is False:
                continue
            r = urllib.request.urlopen("http://{0}/w/api.php?action=query&list"
                "=recentchanges&rcprop=user|comment|flags|title|t"
                "imestamp|loginfo|ids|sizes&rctype=log|edit|new&rcshow=!bot&rawcontinue="
                    .format(wiki.wiki))
            jr = json.loads(r.read().decode('utf-8'))
            log = jr['query']['recentchanges'][0]
            log2 = jr['query']['recentchanges'][1]
            log3 = jr['query']['recentchanges'][2]
            try:
                self.lts[wiki.wiki]
            except:
                self.lts[wiki.wiki] = log['timestamp']
                continue

            if log['timestamp'] != self.lts[wiki.wiki]:
                if self.lts[wiki.wiki] == log2['timestamp']:
                    self.proclog(wiki, log, cli)
                else:
                    if self.lts[wiki.wiki] != log3['timestamp']:
                        self.proclog(wiki, log3, cli)
                    self.proclog(wiki, log2, cli)
                    self.proclog(wiki, log, cli)

    def proclog(self, wiki, log, cli):
        resp = "\00306{0}\003:".format(wiki.wiki)
        self.lts[wiki.wiki] = log['timestamp']
        if log['type'] == "edit":
            resp += " \2{0}\2 ha editado ".format(log['user'])
            resp += "\00310{0}\003 ".format(log['title'])
            elen = log['newlen'] - log['oldlen']
            if elen < 0:
                mlen = "\00304(" + str(elen) + ")\003"
            else:
                mlen = "\00303(+" + str(elen) + ")\003"
            resp += mlen + " - "
            resp += "\00302https://{0}/?diff={1}&oldid={2}\003".format(
                        wiki.wiki, log['revid'], log['old_revid'])
            if log['comment'] != "":
                resp += " \00314({0})\003".format(
                        log['comment'])
        elif log['type'] == "new":
            resp += " \2{0}\2 ha creado ".format(log['user'])
            resp += "\00310{0}\003 ".format(log['title'])
            resp += "\00302https://{0}/?diff={1}\003".format(
                        wiki.wiki, log['revid'])
            if log['comment'] != "":
                resp += " \00314({0})\003".format(
                        log['comment'])
        elif log['type'] == "log":
            if log['logtype'] == "newusers" and log['logaction'] == "create":
                resp += " \2{0}\2 ha creado una ".format(log['user'])
                resp += "cuenta de usuario. \00314(Bloquear: \00302"
                resp += "https://{0}/wiki/Special:Bl".format(wiki.wiki)
                resp += "ockip/{0} \00314)".format(log['user'])
            elif log['logtype'] == "block" and log['logaction'] == "block":
                resp += " \00304[Bloqueo]\003: \2{0}\2 ha sido" \
                                                        .format(log['title'])
                resp += " bloqueado por \00310{0}\003".format(log['user'])
                resp += " durante \00304({0})\003".format(
                                                    log['block']['duration'])
                resp += " \00314{0}\003".format(log['comment'])
            elif log['logtype'] == "block" and log['logaction'] == "unblock":
                resp += " \00303[Desbloqueo]\003: \2{0}\2 ha sido" \
                                                        .format(log['title'])
                resp += " desbloqueado por \00310{0}\003".format(log['user'])
                resp += " \00314({0})\003".format(log['comment'])
            elif log['logtype'] == "block" and log['logaction'] == "reblock":
                resp += " \00304[Bloqueo]\003: el bloqueo de \2{0}\2 ha sido" \
                                                        .format(log['title'])
                resp += " modificado por \00310{0}\003".format(log['user'])
                resp += " duración: \00304({0})\003".format(
                                                    log['block']['duration'])
                resp += " \00314{0}\003".format(log['comment'])
            elif log['logtype'] == "move" and log['logaction'] == "move_redir" \
              or log['logaction'] == "move":
                resp += " \00312[Traslado]\003: \2{0}\2 ha trasladado" \
                                                        .format(log['user'])
                resp += " \00303{0}\003 a ".format(log['title'])
                resp += "\00303{0}\003".format(
                                                    log['move']['new_title'])
                if log['comment'] != "":
                    resp += " \00314({0})\003".format(log['comment'])

            elif log['logtype'] == "protect" and (log['logaction'] == "protect"
              or log['logaction'] == "modify" or log['logaction'] ==
              "move_prot"):
                resp += " \00306[Protección]\003: \2{0}\2 ha protegido" \
                                                        .format(log['user'])
                resp += " \00310{0}\003:".format(log['title'])
                resp += " \00314{0}\003".format(log['0'])
                if log['comment'] != "":
                    resp += " \00314({0})\003".format(log['comment'])
            elif log['logtype'] == "protect" and log['logaction'] == \
              "unprotect":
                resp += " \00306[Desprotección]\003: \2{0}\2 ha desprotegido" \
                                                        .format(log['user'])
                resp += " \00310{0}\003:".format(log['title'])
                if log['comment'] != "":
                    resp += " \00314({0})\003".format(log['comment'])
            elif log['logtype'] == "delete" and log['logaction'] == "delete":
                resp += " \00304[Borrado]\003: \2{0}\2 ha borrado" \
                                                        .format(log['user'])
                resp += " \00310{0}\003:".format(log['title'])
                if log['comment'] != "":
                    resp += " \00314({0})\003".format(log['comment'])
            elif log['logtype'] == "delete" and log['logaction'] == "restore":
                resp += " \00304[Borrado]\003: \2{0}\2 ha restaurado" \
                                                        .format(log['user'])
                resp += " \00310{0}\003:".format(log['title'])
                if log['comment'] != "":
                    resp += " \00314{0}\003".format(log['comment'])
            elif log['logtype'] == "rights" and log['logaction'] == "rights":
                resp += " \00312[Permisos]\003: \2{0}\2 ha cambiado los permi" \
                                                        .format(log['user'])
                resp += " sos de \00310{0}\003".format(log['title'])
                if log['rights']['old'] == "":
                    p1 = "(ninguno)"
                else:
                    p1 = log['rights']['old']
                if log['rights']['new'] == "":
                    p2 = "(ninguno)"
                else:
                    p2 = log['rights']['new']
                resp += " de \2{0}\2 a \2{1}\2".format(p1, p2)
                if log['comment'] != "":
                    resp += " \00314({0})\003".format(log['comment'])
            else:
                return 1
        else:
            return 1
        chans = json.loads(wiki.chans)
        for chan in chans:
            cli.privmsg(chan, resp)


class MonitorWiki2(BaseModel):
    wid = IntegerField(primary_key=True)
    wiki = CharField()
    chans = CharField()
