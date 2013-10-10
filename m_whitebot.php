<?php
/*
 * @name: whitebot
 * @desc: Integra la funcionalidad de whitebot en coot
 * @ver: 1.0
 * @author: MRX
 * @id: whitebot
 * @key: key

 */
class key{
    private $timehandlerid;
    private $hablar=true;
    private $core;
    private $ts;
    private $admins=array("siglar", "White_Master", "Hahc21", "AlanL");
	public function __construct(&$core){
        $this->core = $core;
		$this->timehandlerid = $core->irc->registerTimehandler(20000, $this, "th");
		$core->registerCommand("admin", "whitebot", "Avisa a los administradores disponibles.");
		$core->registerCommand("hablar", "whitebot", "Habilita o deshabilita el habla del bot. Sintaxis: hablar <si/no>",5);
	}
	
	public function hablar(&$irc, &$data, &$core){
		if(!isset($data->messageex[1])){return 0;}
		switch($data->messageex[1]){
			case "si":
			case "yes":
			case "y":
			case "s":
				$this->hablar = true;
				$irc->message(SMARTIRC_TYPE_CHANNEL, $data->channel, "¡De vuelta a la acción! ;3");
				break;
			case "no":
			case "n":
				$this->hablar = false;
				$irc->message(SMARTIRC_TYPE_CHANNEL, $data->channel, "Me quedaré callado :(");
			
		}
	}
	public function admin(&$irc, &$data, &$core){
		foreach($this->admins as $admin){
			$irc->message(SMARTIRC_TYPE_CHANNEL, $admin, "\002{$data->nick}\002 ha solicitado la ayuda de un administrador en {$data->channel}");
		}
		$irc->message(SMARTIRC_TYPE_CHANNEL, $data->channel, "Se ha enviado un aviso a los administradores disponibles.");
	}
    
    function th(&$irc){
        $fl=file_get_contents("http://es.wikivoyage.org/w/api.php?action=query&list=recentchanges&format=json&rcprop=user|comment|flags|title|timestamp|loginfo");
        $fg=json_decode($fl);
        $s="";
        print_r($fg);
        if(($this->ts != $fg->query->recentchanges[0]->timestamp) && ($this->hablar==true)){
            $this->ts = $fg->query->recentchanges[0]->timestamp;
            switch($fg->query->recentchanges[0]->type){
                case "edit":
                    $s="03".$fg->query->recentchanges[0]->user." ha editado el articulo \00310[[".$fg->query->recentchanges[0]->title."]]\003 con el siguiente comentario: 07".$fg->query->recentchanges[0]->comment;
                    if(@isset($fg->query->recentchanges[0]->minor)){ $s.="11 Esta es una edición menor."; }elseif($fg->query->recentchanges[0]->title=="Wikiviajes:Bugs"){
						$s.=" \00311http://es.wikivoyage.org/w/index.php?title=Wikiviajes:Bugs&diff";
					}
                    break;
                case "new":
                    $s="03".$fg->query->recentchanges[0]->user." ha creado el articulo \00310[[".$fg->query->recentchanges[0]->title."]]\003 con el siguiente comentario: 07".$fg->query->recentchanges[0]->comment;
                    break;
                case "log":
					switch ($fg->query->recentchanges[0]->logtype){
						case "rights":
							if($fg->query->recentchanges[0]->rights->old==""){$old="(ninguno)";}else{$old=$fg->query->recentchanges[0]->rights->old;}
							if($fg->query->recentchanges[0]->rights->new==""){$new="(ninguno)";}else{$new=$fg->query->recentchanges[0]->rights->new;}
							$s="\00303{$fg->query->recentchanges[0]->user}\003 ha cambiado los permisos de \002[[".$fg->query->recentchanges[0]->title."]]\002 de \00304".$old."\003 a \00304".$new\003 con el siguiente comentario: \00307.$fg->query->recentchanges[0]->comment \003";
							break;
						 case "block":
							$s="\00303{$fg->query->recentchanges[0]->user}\003 ha bloqueado a \002[[{$fg->query->recentchanges[0]->title}]]\002. Duración: \002{$fg->query->recentchanges[0]->block->duration}\002. Razón: \00307{$fg->query->recentchanges[0]->comment}";
							break;
						 case "delete":
							$s = "\00303{$fg->query->recentchanges[0]->user}\003 ha borrado \002{$fg->query->recentchanges[0]->title}\002: \00307{$fg->query->recentchanges[0]->comment}\003";
							break;
						
					}
            }
            $irc->send("PRIVMSG #wikivoyage-es :$s");
        }

    }
    
    public function __destruct(){
        $this->core->irc->unregisterTimeid($this->timehandlerid);
    }


}
