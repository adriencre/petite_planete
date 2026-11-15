class_name JournalPage
extends Resource
## Une page du journal de la Gardienne (gardienne des lanternes des Semeurs).
## Chaque page raconte un peu et donne un indice. Voir SCENARIO.md.

@export var number := 1 ## ordre dans le carnet
@export var place := "" ## où on la trouve (pour s'y retrouver dans l'éditeur)
@export_multiline var text := ""
@export var luminous := false ## écrite à la peinture lumineuse : lisible seulement dans le noir
