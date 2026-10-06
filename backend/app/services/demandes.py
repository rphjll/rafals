"""Demandes publiées par les clients : publier (avec l'adresse et des photos), lister sur l'accueil, modifier, fermer,
prolonger, expirer. Les réponses, propositions et négociations viennent dans la suite du lot 8.3.
Règles : .doc/regles-metier/RM-DEMANDES.md (validé par Raphael le 04/10/2026 ; accueil et adresse : 05/10/2026).
Tout le monde lit les demandes ouvertes ; la rue n'est montrée qu'au client lui-même (puis au prestataire choisi)."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import reglages
from app.modeles.comptes import Compte
from app.modeles.demandes import Demande, PhotoDemandePubliee
from app.modeles.metiers import Metier
from app.modeles.prestataires import Commune
from app.services import avis, droits, fichiers, journal, mails
from app.services.erreurs import ErreurRegle
from app.services.messagerie import COORDONNEES, Photo

QUAND = ("des_que_possible", "sept_jours", "jour_precis", "pas_presse")
LIEUX = ("chez_moi", "chez_prestataire")


@dataclass
class Saisie:
    """Ce que le client écrit. Ex. Jardinier · « Tondre ma pelouse » · « 200 m², terrain plat, prise dehors » ·
    un jour précis, 10/10/2026 · chez moi · 4000 · « 8 Allée des Pins », 33600, commune 33318."""

    metier_id: int
    titre: str
    description: str
    quand: str
    jour: date | None
    lieu: str
    budget_centimes: int | None
    adresse_ligne: str | None
    adresse_complement: str | None
    code_postal: str | None
    code_insee: str | None
    latitude: float | None
    longitude: float | None


# ---------- Contrôles ----------


def _commune(db: Session, saisie: Saisie) -> Commune:
    """La ville de l'adresse : par son code officiel (INSEE), sinon par le code postal (ex. Paris 11e : le service
    d'adresses donne le code de l'arrondissement, que la liste des communes ne connaît pas)."""
    commune = None
    if saisie.code_insee:
        commune = db.scalar(select(Commune).where(Commune.code_insee == saisie.code_insee.strip()))
    if commune is None and saisie.code_postal:
        commune = db.scalar(select(Commune).where(Commune.codes_postaux.contains([saisie.code_postal.strip()]))
                            .order_by(func.length(Commune.nom), Commune.nom))
    if commune is None:
        raise ErreurRegle("Choisissez votre adresse dans la liste proposée.")
    return commune


def _controler(db: Session, saisie: Saisie, maintenant: datetime) -> tuple[Saisie, Commune]:
    metier = db.get(Metier, saisie.metier_id)
    if metier is None or not metier.est_active:
        raise ErreurRegle("Choisissez un métier dans la liste.")
    titre = avis.verifier_texte(db, saisie.titre, reglages.DEMANDE_TITRE[0], "Le titre", reglages.DEMANDE_TITRE[1])
    description = avis.verifier_texte(db, saisie.description, reglages.DEMANDE_DESCRIPTION[0], "La description",
                                      reglages.DEMANDE_DESCRIPTION[1])
    if COORDONNEES.search(f"{titre} {description}"):
        raise ErreurRegle("Ne mettez pas vos coordonnées ici : le prestataire que vous choisirez les recevra.")
    if saisie.quand not in QUAND:
        raise ErreurRegle("Indiquez pour quand : dès que possible, dans les 7 jours, un jour précis ou pas pressé.")
    jour = saisie.jour if saisie.quand == "jour_precis" else None
    if saisie.quand == "jour_precis":
        if jour is None:
            raise ErreurRegle("Indiquez le jour voulu.")
        if jour < maintenant.astimezone(reglages.FUSEAU_AFFICHAGE).date():
            raise ErreurRegle("Le jour voulu est déjà passé.")
    if saisie.lieu not in LIEUX:
        raise ErreurRegle("Indiquez où : chez vous ou chez le prestataire.")
    if saisie.budget_centimes is not None and saisie.budget_centimes <= 0:
        raise ErreurRegle("Le budget doit être un montant positif (ou laissez-le vide).")
    commune = _commune(db, saisie)
    ligne = " ".join((saisie.adresse_ligne or "").split()) or None
    mini, maxi = reglages.ADRESSE_LIGNE_LONGUEUR
    if ligne is not None and not mini <= len(ligne) <= maxi:
        raise ErreurRegle(f"L'adresse doit faire entre {mini} et {maxi} caractères (ex. « 8 allée des Pins »).")
    if saisie.lieu == "chez_moi" and ligne is None:
        raise ErreurRegle("Indiquez votre adresse complète (numéro et rue) : seul le prestataire que vous choisirez la verra.")
    code_postal = (saisie.code_postal or "").strip() or None
    if code_postal is not None and code_postal not in commune.codes_postaux:
        code_postal = commune.codes_postaux[0] if commune.codes_postaux else None
    position = (saisie.latitude, saisie.longitude)
    if None in position or not (-90 <= position[0] <= 90 and -180 <= position[1] <= 180):
        position = (None, None)  # sans position valable : pas de repère sur le plan, la demande reste possible
    propre = Saisie(
        metier_id=metier.id, titre=titre, description=description, quand=saisie.quand, jour=jour, lieu=saisie.lieu,
        budget_centimes=saisie.budget_centimes, adresse_ligne=ligne,
        adresse_complement=(saisie.adresse_complement or "").strip()[:maxi] or None, code_postal=code_postal,
        code_insee=commune.code_insee, latitude=position[0], longitude=position[1],
    )
    return propre, commune


def _fin(saisie: Saisie, depuis: datetime) -> datetime:
    """30 jours après, ou la fin du jour demandé s'il arrive avant. Ex. publiée le 06/10 pour le 10/10 → fin le 10/10 à minuit."""
    fin = depuis + reglages.DEMANDE_DUREE
    if saisie.jour is not None:
        fin_du_jour = datetime.combine(saisie.jour + timedelta(days=1), time(0), tzinfo=reglages.FUSEAU_AFFICHAGE)
        fin = min(fin, fin_du_jour)
    return fin


def nombre_ouvertes(db: Session, client: Compte) -> int:
    return db.scalar(select(func.count()).select_from(Demande).where(
        Demande.client_id == client.id, Demande.statut == "ouverte")) or 0


def _verifier_droit(db: Session, client: Compte, maintenant: datetime) -> None:
    if not droits.peut_reserver_ou_publier(db, client, maintenant):
        raise ErreurRegle("Vérifiez votre adresse mail (et, avant 18 ans, l'accord de vos parents) pour publier une demande.", 403)


def _verifier_place(db: Session, client: Compte) -> None:
    maxi = reglages.DEMANDE_OUVERTES_MAX
    if nombre_ouvertes(db, client) >= maxi:
        raise ErreurRegle(f"Vous avez déjà {maxi} demandes ouvertes : fermez-en une pour publier celle-ci.")


# ---------- Publier, modifier, fermer, prolonger ----------


def publier(db: Session, client: Compte, saisie: Saisie, photos: list[Photo], maintenant: datetime) -> Demande:
    """Ex. Mme Dupont : Jardinier · « Tondre ma pelouse » · samedi 10/10 · chez elle, 8 allée des Pins à Pessac · 40 €."""
    _verifier_droit(db, client, maintenant)
    _verifier_place(db, client)
    propre, commune = _controler(db, saisie, maintenant)
    if len(photos) > reglages.DEMANDE_PHOTOS_MAX:
        raise ErreurRegle(f"Au plus {reglages.DEMANDE_PHOTOS_MAX} photos par demande.")
    for photo in photos:
        fichiers.verifier(photo.contenu, photo.type_mime, types_acceptes=reglages.PHOTO_TYPES_ACCEPTES,
                          taille_max_octets=reglages.PHOTO_TAILLE_MAX_OCTETS)
    demande = Demande(
        client_id=client.id, metier_id=propre.metier_id, commune_id=commune.id, titre=propre.titre,
        description=propre.description, quand=propre.quand, jour=propre.jour, lieu=propre.lieu,
        budget_centimes=propre.budget_centimes, adresse_ligne=propre.adresse_ligne,
        adresse_complement=propre.adresse_complement, code_postal=propre.code_postal, latitude=propre.latitude,
        longitude=propre.longitude, statut="ouverte", statut_change_le=maintenant, cree_le=maintenant,
        expire_le=_fin(propre, maintenant),
    )
    db.add(demande)
    db.flush()
    for ordre, photo in enumerate(photos, start=1):
        fichier = fichiers.enregistrer(db, client, nom_fichier=photo.nom_fichier, type_mime=photo.type_mime,
                                       contenu=photo.contenu, maintenant=maintenant)
        db.add(PhotoDemandePubliee(demande_id=demande.id, fichier_id=fichier.id, ordre=ordre))
    journal.noter(db, auteur_id=client.id, action="publier_demande", table_cible="demande", ligne_id=demande.id,
                  apres={"titre": demande.titre, "metier_id": demande.metier_id, "commune_id": demande.commune_id},
                  maintenant=maintenant)
    db.flush()
    return demande


def ma_demande_ou_404(db: Session, client: Compte, demande_id: int) -> Demande:
    demande = db.get(Demande, demande_id)
    if demande is None or demande.client_id != client.id:
        raise ErreurRegle("Cette demande n'existe pas.", 404)
    return demande


def modifier(db: Session, client: Compte, demande: Demande, saisie: Saisie, maintenant: datetime) -> Demande:
    """Seulement une demande ouverte (suite du lot 8.3 : et tant que personne n'a répondu). Les photos ne changent pas."""
    if demande.statut != "ouverte":
        raise ErreurRegle("Cette demande n'est plus ouverte : publiez-en une nouvelle.")
    propre, commune = _controler(db, saisie, maintenant)
    avant = {"titre": demande.titre, "metier_id": demande.metier_id, "commune_id": demande.commune_id}
    demande.metier_id, demande.commune_id = propre.metier_id, commune.id
    demande.titre, demande.description = propre.titre, propre.description
    demande.quand, demande.jour, demande.lieu = propre.quand, propre.jour, propre.lieu
    demande.budget_centimes = propre.budget_centimes
    demande.adresse_ligne, demande.adresse_complement = propre.adresse_ligne, propre.adresse_complement
    demande.code_postal, demande.latitude, demande.longitude = propre.code_postal, propre.latitude, propre.longitude
    demande.expire_le = _fin(propre, demande.cree_le)
    if demande.expire_le <= maintenant:  # jour changé sur une demande déjà ancienne : elle repart pour 30 jours
        demande.expire_le = _fin(propre, maintenant)
    demande.rappel_envoye_le = None
    journal.noter(db, auteur_id=client.id, action="modifier_demande", table_cible="demande", ligne_id=demande.id, avant=avant,
                  apres={"titre": demande.titre, "metier_id": demande.metier_id, "commune_id": demande.commune_id},
                  maintenant=maintenant)
    db.flush()
    return demande


def fermer(db: Session, client: Compte, demande: Demande, maintenant: datetime) -> Demande:
    """[Fermer ma demande] : le client n'en a plus besoin. Elle reste dans « Mes demandes », jamais effacée."""
    if demande.statut != "ouverte":
        raise ErreurRegle("Cette demande n'est plus ouverte.")
    demande.statut, demande.statut_change_le = "fermee", maintenant
    journal.noter(db, auteur_id=client.id, action="fermer_demande", table_cible="demande", ligne_id=demande.id,
                  maintenant=maintenant)
    db.flush()
    return demande


def prolonger(db: Session, client: Compte, demande: Demande, maintenant: datetime) -> Demande:
    """30 jours de plus pour une demande ouverte ; une demande expirée redevient ouverte (s'il reste de la place).
    Un jour précis déjà passé ne se prolonge pas : il faut le changer."""
    if demande.statut not in ("ouverte", "expiree"):
        raise ErreurRegle("Cette demande ne peut plus être prolongée : publiez-en une nouvelle.")
    aujourd_hui = maintenant.astimezone(reglages.FUSEAU_AFFICHAGE).date()
    if demande.jour is not None and demande.jour < aujourd_hui:
        raise ErreurRegle("Le jour voulu est passé : publiez une nouvelle demande avec un autre jour.")
    if demande.statut == "expiree":
        _verifier_place(db, client)
        demande.statut, demande.statut_change_le = "ouverte", maintenant
    demande.expire_le = maintenant + reglages.DEMANDE_DUREE
    if demande.jour is not None:
        fin_du_jour = datetime.combine(demande.jour + timedelta(days=1), time(0), tzinfo=reglages.FUSEAU_AFFICHAGE)
        demande.expire_le = min(demande.expire_le, fin_du_jour)
    demande.rappel_envoye_le = None
    journal.noter(db, auteur_id=client.id, action="prolonger_demande", table_cible="demande", ligne_id=demande.id,
                  maintenant=maintenant)
    db.flush()
    return demande


# ---------- Lire ----------


def ouvertes(db: Session, maintenant: datetime) -> list[Demande]:
    """Les demandes montrées sur l'accueil, à tout le monde : ouvertes, pas cachées par l'administrateur, pas arrivées
    à leur fin, d'un client toujours inscrit ; la plus récente en haut."""
    return list(db.scalars(
        select(Demande).join(Compte, Compte.id == Demande.client_id).where(
            Demande.statut == "ouverte", Demande.cachee_le.is_(None), Demande.expire_le > maintenant,
            Compte.ferme_le.is_(None),
        ).order_by(Demande.cree_le.desc(), Demande.id.desc()).limit(reglages.DEMANDE_LISTE_MAX)
    ))


def mes_demandes(db: Session, client: Compte) -> list[Demande]:
    return list(db.scalars(select(Demande).where(Demande.client_id == client.id)
                           .order_by(Demande.cree_le.desc(), Demande.id.desc())))


def photos_de(db: Session, demande_id: int) -> list[PhotoDemandePubliee]:
    return list(db.scalars(select(PhotoDemandePubliee).where(PhotoDemandePubliee.demande_id == demande_id)
                           .order_by(PhotoDemandePubliee.ordre)))


def visible_ou_404(db: Session, compte: Compte, demande_id: int, maintenant: datetime) -> Demande:
    """Pour voir les photos : la demande est sur l'accueil, ou c'est la mienne."""
    demande = db.get(Demande, demande_id)
    sur_l_accueil = demande is not None and demande.statut == "ouverte" and demande.cachee_le is None \
        and demande.expire_le > maintenant
    if demande is None or not (sur_l_accueil or demande.client_id == compte.id):
        raise ErreurRegle("Cette demande n'existe pas.", 404)
    return demande


# ---------- Tâche de fond ----------


def traiter(db: Session, maintenant: datetime) -> tuple[int, int]:
    """(demandes expirées, rappels envoyés). 3 jours avant la fin : un mail « prolongez-la si vous cherchez encore ».
    Pas de rappel pour une demande qui dure moins de 3 jours (ex. publiée jeudi pour samedi)."""
    expirees = db.scalars(select(Demande).where(Demande.statut == "ouverte", Demande.expire_le <= maintenant)).all()
    for demande in expirees:
        demande.statut, demande.statut_change_le = "expiree", maintenant
    a_rappeler = db.scalars(select(Demande).where(
        Demande.statut == "ouverte", Demande.rappel_envoye_le.is_(None), Demande.expire_le > maintenant,
        Demande.expire_le <= maintenant + reglages.DEMANDE_RAPPEL_AVANT,
        Demande.cree_le <= Demande.expire_le - reglages.DEMANDE_RAPPEL_AVANT,
    )).all()
    rappels = 0
    for demande in a_rappeler:
        client = db.get_one(Compte, demande.client_id)
        demande.rappel_envoye_le = maintenant
        if client.ferme_le is not None:
            continue
        jours = reglages.DEMANDE_DUREE.days
        mails.envoyer_mail(
            client.email, f"rafals : votre demande « {demande.titre} » se ferme bientôt",
            f"Votre demande « {demande.titre} » se ferme dans {reglages.DEMANDE_RAPPEL_AVANT.days} jours : "
            f"prolongez-la de {jours} jours si vous cherchez encore (rubrique « Mes demandes »).")
        rappels += 1
    db.flush()
    return len(expirees), rappels
