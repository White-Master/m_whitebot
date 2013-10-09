<?php
/*
 * @name: Geolocalizador
 * @desc: Agrega funciones para geolocalizar IPs
 * @ver: 1.0
 * @author: MRX
 * @id: whitebot
 * @key: key

 */
class key{
    private $timehandlerid;
    private $core;
    private $ts;
	public function __construct(&$core){
        $this->core = $core;
		$this->timehandlerid = $core->irc->registerTimehandler(20000, $this, "th");
	}
    
    function th(&$irc){
        $fl=file_get_contents("http://es.wikivoyage.org/w/api.php?action=query&list=recentchanges&format=json&rcprop=user|comment|flags|title|timestamp|loginfo");
        $fg=json_decode($fl);
        $s="";
        //print_r($fg);
        if($this->ts != $fg->query->recentchanges[0]->timestamp){
            $this->ts = $fg->query->recentchanges[0]->timestamp;
            switch($fg->query->recentchanges[0]->type){
                case "edit":
                    $s="03".$fg->query->recentchanges[0]->user." ha 08editado el articulo [[".$fg->query->recentchanges[0]->title."]] con el siguiente comentario: 07".$fg->query->recentchanges[0]->comment;
                    if(@isset($fg->query->recentchanges[0]->minor)){ $s.="11 Esta es una edición menor."; } 
                    break;
                case "new":
                    $s="03".$fg->query->recentchanges[0]->user." ha 03creado el articulo [[".$fg->query->recentchanges[0]->title."]] con el siguiente comentario: 07".$fg->query->recentchanges[0]->comment;
                    break;
                case "log":
                    if($fg->query->recentchanges[0]->logtype=="newusers"){
                        $s="Se ha registrado el usuario [[".$fg->query->recentchanges[0]->title."]]";
                    }elseif($fg->query->recentchanges[0]->logtype=="rights"){
                        if($fg->query->recentchanges[0]->rights->old==""){$old="(ninguno)";}else{$old=$fg->query->recentchanges[0]->rights->old;}
                        if($fg->query->recentchanges[0]->rights->new==""){$new="(ninguno)";}else{$new=$fg->query->recentchanges[0]->rights->new;}
                        $s="Se han cambiado los privilegios de [[".$fg->query->recentchanges[0]->title."]] de ".$old." a ".$new;
                    }
            }
            $irc->send("PRIVMSG #wikivoyage-es :$s");
        }

    }
    
    public function __destruct(){
        $core->irc->unregisterTimeid($this->timehandlerid);
    }

}
