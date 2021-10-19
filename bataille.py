# Variables globales
import random, os, time, sys
import tkinter as tk
from PIL import ImageTk, Image


COULEURS = ('pic', 'coeur', 'carreau', 'trefle')
VALEURS = { 2: 'Deux', 3: 'Trois', 4: 'Quatre', 5: 'Cinq', 6: 'Six',
7: 'Sept', 8: 'Huit', 9: 'Neuf', 10: 'Dix',
11: 'Valet', 12: 'Dame', 13: 'Roi', 14: 'As' }
CARD_DIR = 'cardimg/' #répertoire des images. Filenames format :<val+couleur>.png , dans le dic {<val+couleur>:FILE}
ICON_IMG_PATH = 'icon.png' #icône de la fenêtre



class Pile :
    def __init__(self) :
        self._storage = []
    def popdestack(self) : #on crée un dépileur pour la pile qui renvoie également la valeur de l'élément dépilé (pour distribuer lors de la distribution)
        if self._storage == [] : #on renvoie none si la pile est vide
            return None
        return(self._storage.pop(0))
    def empile(self, elem) :
        self._storage.insert(0, elem)

    def elems(self) : #méthode "triche" utilisée pour afficher la pile jeucartes plus tard
        return self._storage

    def shufflestack(self) : #méthode 'triche' utilisée pour mélanger la pile jeucartes avant distribution
        random.shuffle(self._storage)


class File : 
    def __init__(self) :
        self._storage = []
    
    def popdequeue(self) : #on crée un defileur pour la file qui renvoie également la valeur de l'élément enlevé de la file (pour que le joueur puisse jouer)
        if self._storage == [] : #on renvoie none si la file est vide
            return None 
        return(self._storage.pop(0))
    
    def queue(self, elem) :
        self._storage.append(elem)
    
    def empty(self) :
        return self._storage == []

    def length(self) : #méthode 'triche' pour déterminer qui a gagné la partie
        return len(self._storage)



class Carte:
    # Attributs :
    #     - couleur : couleur de la carte prise parmis les valeurs de la variable globale COULEURS
    #     - valeur : valeur de la carte prise parmis les clés de la variable globale VALEURS
    # Méthodes :
    #     - __init__(couleur, valeur) : constructeur affectant les paramétres fournis aux attributs
    #     - getters et setters necessaires
    #     - compare(carte2) : renvoie 2 si la carte a une valeur supérieure à celle de carte2, 1 si sa valeur est inférieure et 0 en cas d'égalité
    #     - affiche : affiche la carte (sa couleur et le libelle de sa valeur dans la variable globale VALEURS)
    def __init__(self, couleur, valeur) :
        self._couleur = couleur
        self._valeur = valeur

    def get_val(self) : #sert pour l'affichage des cartes et le jeu
        return self._valeur

    def get_color(self) :
        return self._couleur

    def display(self) :
        print(str(VALEURS[self._valeur]) + ' de ' + self._couleur, end='')

    def compare(self, carte2) :
        if self.get_val() > carte2.get_val() :
            return 2
        if self.get_val() == carte2.get_val() :
            return 0
        if self.get_val() < carte2.get_val() :
            return 1

    def getfilename(self) :
        return str(self._valeur)+'_'+self._couleur+'.jpeg'


class JeuCartes:
    # Le jeu complet de carte
    # Attribut :
    #     -	jeu : pile de cartes 
    # Méthodes :
    #     -	__init__ : constructeur qui rempli le jeu avec 32 cartes classées dans l'ordre des variables globales COULEURS x VALEURS
    #     -	est_vide : Renvoie True si le jeu est vide, False sinon
    #     -   mélange : mélange le jeu de façon aléatoire (voir la méthode random.shuffle()
    #     -	distribue : Renvoie une carte du jeu en l'enlevant de ce jeu
    #     -   affiche : affiche l'ensemble des cartes du jeu (sert surtout pour les tests)
    def __init__(self, COULEUR=COULEURS, VALEURS=VALEURS) :
            self._jeu = Pile()
            for c in COULEURS :
                for v in VALEURS :
                    self._jeu.empile(Carte(c,v))

    def melange(self) :
        self._jeu.shufflestack()

    def distrib(self) :
        return(self._jeu.popdestack())

    def affiche(self) :
        for c in self._jeu.elems() :
            print(VALEURS[c._valeur], c._couleur)

    def filenames(self) :
        return[carte.getfilename() for carte in self._jeu.elems()]


class JeuJoueur:
    # ensemble des cartes d'un joueur vu comme une File (principe FIFO)
    # Attributs :
    #     -	cartes : file de cartes 
    # Méthodes :
    #     -	__init__ : constructeur d'une file vide
    #     -	queuer(carte) ici, addcard: insère une carte en queue de file
    #     -	defiler : Renvoie la carte en tête de file et l’enlève de la file
    #                   Si la file est vide, renvoie None
    #     -	estVide : Renvoie True si la file transmise est une file vide, False sinon
    #     -   affiche : affiche l'ensemble des cartes du joueur
    def __init__(self) :
        self._jeu = File()

    def addcard(self, carte) :
        self._jeu.queue(carte)

    def playcard(self) :
        return self._jeu.popdequeue()

    def isempty(self) :
        return self._jeu.empty()

    def length(self) :
        return self._jeu.length()


class Bataille:
    
    # Jeu de bataille
    # Attributs:
    #     -   nbcartes : nombre de cartes dans le jeu des joueurs (sert à limiter pour les tests)
    #     -	cartesJ1 : pile des cartes du joueur 1 (classe JeuJoueur)  
    #     -	cartesJ2 : pile des cartes du joueur 2 (classe JeuJoueur)  
    #     -	nbtours : entier, nombre de tours de jeu (sert à limiter pour les tests)
    # Méthodes :
    #     -	__init__(nbc,nbt) : constructeur ayant comme paramétres le nombre de cartes à distribuer dans chaque jeu de joueur (nbc)
    #     et le nombre de tours limite de jeu (nbt). Ce constructeur initialise les deux jeux de joueurs (carteJ1 et cartesJ2) en distribuant les cartes à partir
    #     d'un jeu complet de carte (classe JeauCartes) qu'il a d'abord construit et mélangé.
    #     -	jouer : partie jouée (tours de jeux jusqu'à la victoire d'un joueur dans la limite de nbtours et affichage des résultats)
    def __init__(self, nbt = 100000, nbc = 26, CLI=False) :
        assert nbc <= 26 , 'Cannot play with more than 52 cards'
        self._nbc = nbc
        self._nbt = nbt
        self._cartesJ1 = JeuJoueur()
        self._cartesJ2 = JeuJoueur()
        jeu = JeuCartes()
        self._filenames = jeu.filenames()
        self._CLI = CLI
        jeu.melange()
        for _ in range(nbc) :
            self._cartesJ1.addcard(jeu.distrib())
        for _ in range(nbc) :
            self._cartesJ2.addcard(jeu.distrib())
        if self._CLI == False :
            root = tk.Tk()
            blankimg = ImageTk.PhotoImage(Image.open('blank.jpg'))
            root.geometry('1000x1000')
            # root.iconphoto(False, 'icon.jpg')
            statementlabel = tk.Label(root, text='No player has played yet')
            statementlabel.pack(padx='500',pady='900')
            player1label = tk.Label(root, text='Ludwig')
            player1label.pack(padx='100', pady='800')
            player2label = tk.Label(root, text='Carl')
            player2label.pack(padx='800', pady='800')
            c1label = tk.Label(root, image=blankimg)
            c1label.pack(padx='50',pady='200')
            c2label = tk.Label(root, image=blankimg)
            c2label.pack(padx='700',pady='200')
            root.mainloop()

    def getfiledic(self) :
        return {fname:ImageTk.PhotoImage(Image.open(fname)) for fname in self._filenames}


    def jouer(self) :          
        for _ in range(self._nbt) :
            c1 = self._cartesJ1.playcard()
            c2 = self._cartesJ2.playcard()
            if self._CLI :
                c1.display()
                print(' VS ', end='')
                c2.display()
            if c1.compare(c2) == 2 :
                #la carte 1 l'emporte
                self._cartesJ1.addcard(c1)
                self._cartesJ1.addcard(c2)
                if self._CLI :
                    print(' : Player Ludwig wins the round')
            if c1.compare(c2) == 1 :
                #la carte 2 l'emporte
                self._cartesJ2.addcard(c1)
                self._cartesJ2.addcard(c2)
                if self._CLI :
                    print(' : Player Carl wins the round')
            if c1.compare(c2) == 0 :
                #égalité : on sort les deux cartes du jeu, donc on ne fait rien
                if self._CLI :
                    print('Égalité')
                    sys.Exit()

            if self._cartesJ1.isempty() :                
                if self._CLI :
                    print('Égalité')
                    sys.Exit(1)
                return 'Ludwig'

            if self._cartesJ2.isempty() :
                if self._CLI :
                    print('Égalité')
                    sys.Exit(1)
                return 'Carl'

            time.sleep(5)

        if self._cartesJ1.length() > self._cartesJ2.length() :
            if self._CLI :
                    print('Player Ludwig won the round')
                    sys.exit()
            return 'Ludwig'

        if self._cartesJ2.length() > self._cartesJ1.length() :
            if self._CLI :
                    print('Player Carl won this game')
                    sys.exit()
            return 'Carl'

        if self._cartesJ1.length() == self._cartesJ2.length() :
            if self._CLI :
                    print('Égalité')
                    sys.exit()
            return 'Égalité'

def main() :
    game = Bataille(nbt=10, nbc=10, CLI='-cli' in sys.argv)
    rslt = game.jouer()
    print(rslt)

main()

# B=Bataille(2,10) # Va initialiser un jeu de bataille avec 2 cartes distribuées à chaque joueur et pour 10 tours maximum
# B.jouer() # lance le jeu
