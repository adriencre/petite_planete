class_name Dialogue
extends Resource
## Une conversation avec un habitant de l'ombre (on lui parle avec E, antenne éteinte).
## Les répliques s'affichent en mots de lumière (LueurSpeech) : rien antenne allumée,
## des bribes à batterie basse, la phrase entière dans le noir.
## L'habitant choisit la première conversation dont les conditions sont remplies.

@export var id: StringName ## identifiant unique (mémorisé quand elle a été entendue en entier)
@export_multiline var lines: PackedStringArray = []
## Pour chaque réplique : identifiant dans la section « Paroles » du carnet (vide = pas recopiée).
@export var paroles: Array[StringName] = []
@export var requires: Array[StringName] = [] ## flags de boucle nécessaires (ex. &"bascule")
@export var forbids: Array[StringName] = [] ## flags qui l'empêchent
@export var once := false ## une fois entendue en entier, on passe à la suivante
@export var sets_flag: StringName ## flag posé quand elle a été entendue en entier (indice, suite…)


func available() -> bool:
	for f in requires:
		if not Loop.has_flag(f):
			return false
	for f in forbids:
		if Loop.has_flag(f):
			return false
	return not (once and heard())


func heard() -> bool:
	return Loop.has_flag(StringName("dlg_" + id))
