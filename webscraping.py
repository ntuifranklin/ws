import os
"""
needed_libs = ["requests","lxml","bs4","csv"]
for lib in needed_libs:
  try:
    import lib
  except ImportError:
    print ("Trying to Install required module: ", lib, "\n")
    os.system("python3 -m pip install " + lib)
"""
import sys
import subprocess
import requests
from lxml import html
from bs4 import BeautifulSoup
import csv
import time
import random
import urllib


# sauter des etape en parametrant la recherche en meme temps
# en fait quand tu va sur le site kff.org, puis tu tappe hello dans la barre de recherche,
# le site te renvoi a la route 'search' avec parametre s=hello
# donc si je tappe Health Care IT Policy, dans la barre de recherche du site,
# la site me renvoi plutot a la page https://www.kff.org/search/?s=Health+Care+IT+Policy
# donc on va utiliser le liens directe pour faire facile
mot_tapper_au_terminal = ""
mot_cle_par_defaut = "Health Care IT Policy"
mot_tapper_au_terminal = input("\nEnter keywords to search for : ")
if len(mot_tapper_au_terminal) == 0 or mot_tapper_au_terminal == "":
   mot_tapper_au_terminal = mot_cle_par_defaut
mot_cle = mot_tapper_au_terminal.replace(" ","+")
lien_directe = "https://www.kff.org/search/?s=" + mot_cle

page_brute = requests.get(lien_directe)

sauce = BeautifulSoup(page_brute.content, 'html5lib')

# impression des donnes prise sur la page d'acceuil dans la variable lien_directe
#print(sauce.prettify())

# recuperation de la page sous forme de long chaine de character
# structurer sous forme d'abre genealogique
arbre_page = html.fromstring(page_brute.content)
# on va attendre un peu afin de ne pas detecter les logiciels anti-scraping du site
secondes_aleatoire = random.randrange(2,4,1) # entre 2 et 4 secondes par pas de 1
time.sleep(secondes_aleatoire)

# on va lister tout les liens contenu dans la page.
# le liens se trouve sous forme <a href='liens_vers_la_page'>description_du_liens</a>
# mais ces liens sont encapsuler dans la balise <article></article>
# donc on va chercher tout les anchor tags representer par <a></a> se trouvant dans les article tags
# (balises <article></article>)
# en fait chaque resultat de la barre de recherche se presente sous code html brutte ci dessous :
# commentaire multi-ligne ci dessous
"""
   ... debut de la page sous forme html 
   ... corps de la page sous forme html
   ... resultat ressemble a ceci
   ...
   ...
   <article>
       ... bla bla bla
       <a href='liens_vers_article'>titre de l'article</a>
   </article>
"""
# determiner le nombre de resultats pour savoir combien de page de 10 on aura a visiter
# le nombre de resultat se trouve dans un div class total-results-wrapper en suite p class byline bold
donnees_resultat_totale = sauce.find("div",{"class":"total-results-wrapper"}).find_all("p",class_="byline bold")


print(donnees_resultat_totale)
nombre_de_resultats = 0
for d in donnees_resultat_totale:
   rtext = d.getText()  # Si cette ligne genere les erreurs, essai d.get_text(). les noms des fonctions changent dependant de la version dy python ou de beautifulsoup
   a = rtext.split(":")
   nombre_de_resultats = a[len(a)-1]
   # on enleve l'espace
   nombre_de_resultats = nombre_de_resultats.replace(" ","")
   # on enleve la virgule
   nombre_de_resultats = nombre_de_resultats.replace(",","")
   nombre_entier = int(nombre_de_resultats)
   nombre_de_resultats = int(nombre_de_resultats)
   # print(d.getText())
print("The number of search results is : ", nombre_entier)



"""
Generate a list of numbers from 1 to the number of results that will be shuffled and randomized
to prevent anti scraping detection
"""
list_des_numeros_de_pages = list(range(1,(nombre_de_resultats+1)))

"""
IMPORTANT : https://www.kff.org/search/?s=Covid&paged=4&s=Covid&fs=search
    Attributes needed : 
        - Published date
        - Title of article
        - Link to te article
        - First name and last name of author
        - Email of author
"""


# ceci contiendra les lignes qu'on va afficher dans le csv
data_rows = []
liste_des_liens_de_recherche = []
lien_de_base = "https://www.kff.org/search/?s="

#print("List of Pages to visit for the search")
l = len(list_des_numeros_de_pages)
assert l > 0, "The length of the array should be greater than 0"
while l > 0:
 # page aleatoire
 if l > 0:
  assert l > 0, "The length of the array should be greater than 0" 
  f = len(list_des_numeros_de_pages)
  assert f > 0
  page_no = random.randrange(f)
  assert page_no in range(l), "The page number should be valid"
  value = list_des_numeros_de_pages[page_no]
  #print(value)
  q = str(value)
  #print(q)
  dizaine = q[0]
  even = lien_de_base + mot_cle + "&paged=" + dizaine + "&s=" + mot_tapper_au_terminal + "&fs=search"
  odd = lien_de_base + mot_cle + "&paged=" + dizaine + "&fs=search" + "&s=" + mot_tapper_au_terminal
  if nombre_de_resultats > 9:
      if even in liste_des_liens_de_recherche or odd in liste_des_liens_de_recherche:
          continue
      else:
          if value % 2 == 0:
              liens_dynamique = even
          else:
              liens_dynamique = odd

  else:
      liens_dynamique = lien_de_base + mot_cle
  #print(liens_dynamique)
  list_des_numeros_de_pages.pop(page_no)
  liste_des_liens_de_recherche.append(liens_dynamique)
  l = len(list_des_numeros_de_pages)
  # page_brute = requests.get(lien_directe)
page_directe = []
fichier = "les_liens.csv"
#print(liste_des_liens_de_recherche)
for lien_article in liste_des_liens_de_recherche:
 #print(lien_article)
 # on tente pour voir si la page n'est pas un 404 error page
 
 with urllib.request.urlopen(lien_article) as page:
   une_page = requests.get(lien_article)
   secondes_aleatoire = random.randrange(1, 3, 1)  # entre 1 et 3 secondes par pas de 1
   time.sleep(secondes_aleatoire)
   sauce_brute = BeautifulSoup(une_page.content, 'html5lib')
   les_articles = sauce_brute.find("section", \
   {"class": "search-results-wrapper"}).findAll("article")
   try:
     f = None
     f = open(fichier, "a")
     if f is not None and len(les_articles) > 0:
     
       for un_article in les_articles:
         les_h5 = un_article.find_all("h5")
         for un_h5 in les_h5:
           anchors = un_h5.find_all("a")
           for one_anchor in anchors:
           # print("\n#####  Resultat no ", i + 1, " de la recherche #####")
           #page_directe.append(one_anchor)
            f.write(str(one_anchor))
            f.write(str("\n"))
           #print(one_anchor)
           # print("#################################################\n\n")
       f.close()
     else:
      continue
   except IOError as e:
    continue
  
   secondes_aleatoire = random.randrange(3, 5)  # entre 1 et 3 secondes par pas de 1
   time.sleep(secondes_aleatoire)


print("Fichier creer avec success.")
 
# On va essayer de verifier si le fichier 
# creer pour sauvegarder les liens a une poids superieure a zero
poids = int(os.stat(fichier).st_size)
page_directe = []
if poids > 0:
 # maintenant on ouvre le fichier et on ouvre chaque page contenu dans ce fichier
 try:
  f = None
  f = open(fichier, "r") # mode lecture
  if f is not None:
   page_directe = f.readlines()
   f.close()
   longeur_tableau = len(page_directe)
   if longeur_tableau > 0:
    print("Tableau charger ")
     
   f.close()
 except IOError as e:
   # erreur, peine perdu
   print("Something happened")

# voyons voir
if len(page_directe) > 0:
 ff = None
 ff = open("data.csv","w")
 if ff is not None:
  ff.write("")
  for ligne in page_directe:
    ff.write(ligne)
    ff.write("\n")
   

