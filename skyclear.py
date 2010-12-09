#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# skyclear.py
#

#####
## LICENCE
###

#                LICENCE PUBLIQUE RIEN À BRANLER
#                      Version 1, Mars 2009
#
# Copyright (C) 2010 Olivier DOSSMANN
#  <blankoworld@wanadoo.fr>
# 
# La copie et la distribution de copies exactes de cette licence sont
# autorisées, et toute modification est permise à condition de changer
# le nom de la licence. 
#
#         CONDITIONS DE COPIE, DISTRIBUTON ET MODIFICATION
#               DE LA LICENCE PUBLIQUE RIEN À BRANLER
#
#  0. Faites ce que vous voulez, j’en ai RIEN À BRANLER.

from BeautifulSoup import BeautifulSoup
import re #pour les recompilations de chaines
import random #pour les nombres aleatoires
import datetime #pour la gestion du temps
import codecs #pour la gestion de l'encodage des caracteres
import MySQLdb #et si on utilisait une base de donnees ?
import os #pour la creation de dossier
import urllib2 #lecture de pages internet
import urllib #chargement de fichiers

#####
## REQUIS
###

# - python-mysqldb

#####
## VARIABLES
###

##Creation des dossiers necessaires pour enregistrer les fichiers images
### ./images/ est conseille pour stocker ici meme les images et ensuite
### les copier sur le blog
adresse_dossier_imgs_dotclear = "/srv/www/blog/images/" #adresse du dossier contenant les images dotclear
nom_dossier_imgs_skyblog = "skyblog" #nom du dossier pour les images skyblog
dossier_images = adresse_dossier_imgs_dotclear + nom_dossier_imgs_skyblog + "/"

##Pseudonyme (a modifier)
pseudo = "pseudo101" #mettre ici le pseudo qui permet d'acceder a skyblog
pseudo_dotclear = "meilleurPseudo" #mettre ici le pseudo qui apparait dans dotclear
hote = "localhost"
portacces = 3306
utilisateur = "blanko"
mot2passe = "monMot2passe"
base2donnees = "blankoworld"

#####
## DEBUT
###

if not os.path.exists(adresse_dossier_imgs_dotclear): os.mkdir(adresse_dossier_imgs_dotclear)
if not os.path.exists(dossier_images): os.mkdir(dossier_images)

##Fonction ContientUn ne semble pas fonctionner comme je l'aimerais
def contientUn(seq, un_ens):
	"""Verifie si la sequence seq contient UN des elements de un_ens."""
	for c in seq:
		if c in un_ens: return True
	return False

##Remplacement des mois par leur equivalent numerique
def remplacement_mois(texte):
	"""Retourne le numero du mois donnee sous forme textuel
	Sinon retourne 0 si le texte donne n'est pas un mois"""
	mois = {
		"janvier" : "01",
		"février" : "02",
		"mars" : "03",
		"avril" : "04",
		"mai" : "05",
		"juin" : "06",
		"juillet" : "07",
		"août" : "08",
		"septembre" : "09",
		"octobre" : "10",
		"novembre" : "11",
		"décembre" : "12"
	}
	rx = re.compile('|'.join(map(re.escape, mois)))
	def traduit_une(correspondance):
		return mois[correspondance.group(0)]
	return rx.sub(traduit_une, texte)

##Encoder donnees unicode vers html
from htmlentitydefs import codepoint2name
def remplace_html(exc):
	if isinstance(exc, (UnicodeEncodeError, UnicodeTranslateError)):
		s = [ u'&%s;' % codepoint2name[ord(c)]
			for c in exc.object[exc.start:exc.end] ]
		return ''.join(s), exc.end
	else:
		raise TypeError("Impossible de traiter %s" % exc.__name__)
codecs.register_error('remplace_html', remplace_html)

def encode_pour_html(donnees_unicode, encodage = 'ascii'):
	return donnees_unicode.encode(encodage, 'remplace_html')

num_article = 0 #on commence la numerotation des articles a partir de 0

##On construit les adresses URL
adresse = "http://" + pseudo + ".skyblog.com/"
fichier = "1.html"
url = adresse + fichier

##Recuperation de la page internet 1.html
page=urllib2.urlopen(url)
html=page.read()
page.close()
	
soup = BeautifulSoup(html) #parsage par BeautifulSoup

derniere_page = int(soup.findAll('link', rel="last")[0]['href'].split('/')[-1].split('.')[0]) #recherche de la derniere page
premiere_page = 1 #numero de la premiere page
#derniere_page = 3 #numero de la derniere page [MANUEL]

for i in range(derniere_page)[premiere_page - 1:]:
	
	fichier = str(i + 1) + ".html" #fichier a lire
	url = adresse + fichier
	print url + ":"
	
	## FICHIERS: Seulement si vous avez recupere les fichiers .html d'une autre maniere
	#doc = open(fichier).read() #ouverture du fichier dans une variable
	#open(fichier).close() #fermeture du fichier

	## URLS: Seulement si vous voulez recuperer directement les pages et les traiter
	page = urllib2.urlopen(url)
	doc = page.read()
	page.close()
	
	soup = BeautifulSoup(doc) #parsage par BeautifulSoup
	
	articles = soup.findAll('div', attrs={"class" : "article"}) #recherche des articles

	nbre_articles = len(articles) #calcul du nombre d'articles
	
	#traitement pour chaque article de la page
	for i in range(len(articles)):
		num_article = num_article + 1 #le numero d'article (au total)

		##Initialisation de toutes les variables
		id = ""
		titre = ""
		num_contenu_img = ""
		#image_positionh = ""
		#image_positionv = ""
		image = ""
		image_src = ""
		image_alt = ""
		existe_image = bool(0)
		position_image = ""
		image_estenbas = bool(0)
		image_vertical = ""
		div = ""
		paragraphes = ""
		texte = ""
		enqueue = ""
		date = ""
		tab_date = ""
		jour = ""
		mois_txt = ""
		mois = ""
		annee = ""
		secondes = ""
		heure = ""
		date_creation = ""
		maintenant = ""
		date_modif = ""
		image_estenbas_txt = ""
		contenu = ""
		style_img = ""
		image_txt = ""
		contenu = ""
		adresse_img = ""
		image_nom = ""
		
		##Informations diverses sur l'article
		id = articles[i]['id'][2:] #identifiant de l'article chez skyblog
		titre =  articles[i].h2.string.encode("utf-8") #Titres de l'article
		num_contenu_img = "".join(["container-",id])
		image =  articles[i].find('img')
		if image != None:
			#Attributs de l'image
			image_src = image['src'] #Image de l'article (lien)
			image_alt = image['alt'] #Texte alternatif a l'image
			existe_image = bool(1)

			#Position de l'image
			position_image = image.findPrevious('div')['class']
			if position_image.split(' ')[-1] == "after":
				image_estenbas = bool(1)
				image_estenbas_txt = "bas"
			else:
				image_estenbas = bool(0)
				image_estenbas_txt = "haut"

			#Recherche du nom de l'image et enregistrement de son adresse
			adresse_img = image_src
			image_nom = image_src.split('/')[-1]

			image_vertical = position_image.split(' ')[1]
			if image_vertical == "center":
				style_img = "text-align: center"
				image_txt = "<p style=\"" + style_img + "\"><img src=\"/./images/" + nom_dossier_imgs_skyblog + "/" + image_nom + "\" alt=\"" + image_alt + "\" /></p>"
			elif image_vertical == "right":
				style_img = "float: right; margin: 5px"
				image_txt = "<img src=\"/./images/" + nom_dossier_imgs_skyblog + "/" + image_nom + "\" alt=\"" + image_alt + "\" style=\"" + style_img + ";\"/>"
			else:
				style_img = "float: left; margin: 5px"
				image_txt = "<img src=\"/./images/" + nom_dossier_imgs_skyblog + "/" + image_nom + "\" alt=\"" + image_alt + "\" style=\"" + style_img + ";\"/>"
			
			#Enregistrement de l'image
			urllib.urlretrieve(adresse_img, dossier_images + image_nom)

		##Contenu de l'article
		paragraphes = articles[i].find('div', attrs={'class' : "text-container"})
		for j in range(len(paragraphes.contents)):
			texte = texte + str(paragraphes.contents[j])

		##Recuperer la date du billet !
		enqueue = articles[i].find('div', attrs={'class' : "created_on"}) #paragraphe created_on
		date = enqueue.contents[2] #phrase seule : poste le 09 mai 2005 21:15
		tab_date = date.split(' ') #on decoupe selon les espaces
		jour = tab_date[3] #le jour du mois
		mois_txt = tab_date[4].encode("utf-8") #le mois en mode texte (mai, juin, etc.)
		mois = remplacement_mois(mois_txt)
		annee = tab_date[5]
		secondes = random.randint(10,59) #on genere un nombre de secondes aleatoires
		heure = tab_date[6][0:5] + ":" + str(secondes)
		date_creation = ''.join([annee,"-",mois,"-",jour," ",heure])
		maintenant = datetime.datetime.now()
		date_modif = maintenant.strftime("%Y-%m-%d %H:%M:%S")

		##Creation du contenu
		if existe_image:
			if image_estenbas:
				contenu += ''.join([texte, image_txt.encode("utf-8")])
			else:
				contenu += ''.join([image_txt.encode("utf-8"), texte])
			contenu += ''.join("<div style=\"clear:both;\">&nbsp;</div>")
		else:
			contenu += texte

		##Encodage unicode vers html
		contenu = encode_pour_html(contenu.decode("utf-8"))
		contenu = contenu.replace("'", "''")
		titre = encode_pour_html(titre.decode("utf-8"))
		titre = titre.replace("'", "''")

		##Connexion a la base de donnees
		connexion = MySQLdb.connect(host = hote, port = portacces, user = utilisateur, passwd = mot2passe, db = base2donnees)
		curseur = connexion.cursor() #mise en place du curseur

		try:
			sql = "INSERT INTO `dc_post` (`user_id`, `cat_id`, `post_dt`, `post_creadt`, `post_upddt`, `post_titre`, `post_titre_url`, `post_content`, `post_pub`, `post_selected`, `post_open_comment`, `post_open_tb`, `nb_comment`, `nb_trackback`, `post_lang`) VALUES ('" + pseudo_dotclear + "', 1, '" + date_creation + "', '" + date_creation + "', '" + date_modif + "', '" + titre + "', '" + str(num_article) + "', '" + contenu + "', 1, 0, 1, 1, 0, 0, 'fr');"
#			print "Requete SQL:" + str(sql)
			curseur.execute(sql)
			print "Requête éxécutée avec succès"
		finally:
			connexion.close()

