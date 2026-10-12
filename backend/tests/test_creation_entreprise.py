"""Créer une auto-entreprise depuis rafals (RM-CREATION-AUTO-ENTREPRISE.md ; lot 7.1). Le guichet de l'État est simulé
(conftest : FauxGuichet) : aucune vraie entreprise n'est créée."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app import config, reglages
from app.modeles.creation import DossierCreation, PieceDossier
from app.modeles.fichiers import Fichier
from app.modeles.metiers import Metier
from app.services import creation_entreprise as service
from app.services import pdf_pieces
from tests.test_prestataires import fabrique_prestataire, metiers  # noqa: F401 (fixtures)
from tests.test_prestataires import id_commune

PDF = b"%PDF-1.4 zztest papier d'essai"
# Le plus petit JPG lisible : début, bloc « SOF » (hauteur 300, largeur 400, 3 couleurs), fin
JPG = b"\xff\xd8" + b"\xff\xc0\x00\x11\x08" + (300).to_bytes(2, "big") + (400).to_bytes(2, "big") + b"\x03" + bytes(9) + b"\xff\xd9"
SECU = "198033306312352"  # clé juste : 97 − (1980333063123 modulo 97) = 52
SIRET_RECU = "91234567800017"
URL = "/api/moi/creation-entreprise"


def aujourd_hui():
    return datetime.now(reglages.FUSEAU_AFFICHAGE).date()


def vous(client, **modifs) -> dict:
    """Karim Youssef BENALI, né le 14/03/1998 à Bordeaux, célibataire, 12 rue des Lilas à Mérignac."""
    return {
        "civilite": "monsieur", "nom_naissance": "Benali", "prenoms": "Karim, Youssef", "naissance_le": "1998-03-14",
        "naissance_commune_id": id_commune(client, "33000", "Bordeaux"), "nationalite": "francaise",
        "situation_famille": "celibataire", "numero_secu": "1 98 03 33 063 123 52", "adresse_rue": "12 rue des Lilas",
        "commune_id": id_commune(client, "33700", "Mérignac"), "code_postal": "33700",
        "mail": "karim.zztest@example.com", "telephone": "06 12 34 56 78",
    } | modifs


def activite(metier_id: int, **modifs) -> dict:
    return {
        "metier_id": metier_id, "description": "Dépannage et installation de plomberie chez les particuliers",
        "debut_le": (aujourd_hui() + timedelta(days=10)).isoformat(), "lieu_travail": "chez_clients",
        "nom_commercial": "ZZTEST Benali Plomberie", "activite_en_meme_temps": "salarie",
    } | modifs


CHOIX = {"periodicite": "trimestre", "impot_avec_cotisations": False, "acre_demandee": True, "adresse_non_publique": True}
PARENTS = {"pere_nom": "BENALI Ahmed", "mere_nom": "HADDAD Samira"}


def deposer(compte, sorte: str, contenu: bytes = PDF, type_mime: str = "application/pdf"):
    return compte.client.post(f"{URL}/pieces/{sorte}", files={"fichier": (f"{sorte}.pdf", contenu, type_mime)})


def dossier_pret(compte, client, metier_id: int) -> dict:
    """Karim, plombier : les 4 premières étapes faites, il ne reste qu'à envoyer."""
    assert compte.client.post(URL).status_code == 201
    for etape, donnees in (("vous", vous(client)), ("activite", activite(metier_id)), ("choix", CHOIX), ("parents", PARENTS)):
        reponse = compte.client.post(f"{URL}/{etape}", json=donnees)
        assert reponse.status_code == 200, reponse.text
    assert deposer(compte, "identite", JPG, "image/jpeg").status_code == 200
    reponse = deposer(compte, "diplome")
    assert reponse.status_code == 200, reponse.text
    return reponse.json()["dossier"]


def envoyer(compte):
    return compte.client.post(f"{URL}/envoi", json={"certifie": True, "pouvoir": True})


def actualiser(compte) -> dict:
    return compte.client.post(f"{URL}/actualiser").json()["dossier"]


def en_base(base: Session, compte) -> DossierCreation:
    base.expire_all()
    return base.scalar(select(DossierCreation).where(DossierCreation.compte_id == compte.id).order_by(DossierCreation.id.desc()))


# ---------- Le parcours complet ----------


def test_karim_cree_son_auto_entreprise(fabrique_compte, client, metiers, faux_guichet, base: Session, mails_envoyes) -> None:  # noqa: F811
    karim = fabrique_compte()
    depart = karim.client.get(URL).json()
    pret = dossier_pret(karim, client, metiers["Plombier"])
    envoye = envoyer(karim)
    depot = next(a["donnees"] for a in faux_guichet.appels if a["chemin"] == "/api/formalities")
    identifiant = en_base(base, karim).guichet_id
    pouvoir_lu = karim.client.get(f"{URL}/pouvoir").json()["texte"]
    pouvoir_pdf = karim.client.get(f"{URL}/pieces/pouvoir").content
    en_examen = actualiser(karim)
    modification_refusee = karim.client.post(f"{URL}/choix", json=CHOIX)
    faux_guichet.valider(identifiant, SIRET_RECU)
    accepte = actualiser(karim)

    assert depart == {"peut_commencer": True, "raison": None, "a_un_profil": False, "dossier": None}
    assert pret["statut"] == "brouillon" and pret["metier_reglemente"] is True
    assert [p["sorte"] for p in pret["pieces"]] == ["identite", "diplome"] and not any(pret["manque"].values())
    assert envoye.status_code == 200 and envoye.json()["dossier"]["statut"] == "envoye"
    # Ce que le guichet a reçu : une création de micro-entreprise, les 4 papiers en PDF, puis la signature
    contenu = depot["content"]
    assert depot["typeFormalite"] == "C" and depot["typePersonne"] == "P" and depot["diffusionINSEE"] == "N"
    assert contenu["natureCreation"]["microEntreprise"] is True
    entrepreneur = contenu["personnePhysique"]["identite"]["entrepreneur"]
    assert entrepreneur["descriptionEntrepreneur"] | {"nom": "BENALI", "prenoms": ["Karim", "Youssef"], "numeroSecu": SECU,
                                                      "codeInseeGeographique": "33063"} == entrepreneur["descriptionEntrepreneur"]
    assert entrepreneur["regimeMicroSocial"] == {"optionMicroSocial": True, "periodiciteVersement": "T"}
    assert contenu["personnePhysique"]["etablissementPrincipal"]["activites"][0]["formeExercice"] == "ARTISANALE_REGLEMENTEE"
    assert sorted(p["typeDocument"] for p in contenu["piecesJointes"]) == ["PJ_11", "PJ_17", "PJ_31", "PJ_51"]
    assert all(p["documentBase64"].startswith("JVBERi") for p in contenu["piecesJointes"])  # « %PDF » : la photo JPG aussi
    assert any(a["chemin"] == "/api/signatures" for a in faux_guichet.appels)
    assert "donne pouvoir à rafals" in pouvoir_lu and pouvoir_pdf.startswith(b"%PDF")
    assert any(m["a"] == "karim.zztest@example.com" and "envoyé" in m["sujet"] for m in mails_envoyes)
    # Envoyé : plus rien ne se modifie
    assert en_examen["statut"] == "en_examen" and modification_refusee.status_code == 400
    # Accepté : le SIRET est gardé (pas encore de profil), les données sensibles et les papiers sont effacés
    assert accepte["statut"] == "accepte" and accepte["siret_recu"] == SIRET_RECU and accepte["numero_secu"] is None
    assert all(p["efface"] for p in accepte["pieces"])
    dossier = en_base(base, karim)
    assert dossier.sensible_efface_le is not None and dossier.pere_nom is None and dossier.nom_naissance == "BENALI"
    assert base.scalar(select(Fichier.id).where(Fichier.depose_par_id == karim.id)) is None
    assert karim.client.get(f"{URL}/pieces/identite").status_code == 404
    assert any("Votre auto-entreprise est créée" in m["sujet"] and SIRET_RECU in m["texte"] for m in mails_envoyes)


def test_le_siret_recu_va_dans_le_profil(fabrique_prestataire, client, metiers, faux_guichet, base: Session) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    dossier_pret(karim, client, metiers["Plombier"])
    envoyer(karim)
    faux_guichet.valider(en_base(base, karim).guichet_id, SIRET_RECU)
    service.suivre(base, datetime.now(UTC))  # la tâche de fond, sans que Karim clique
    base.commit()
    profil = karim.client.get("/api/moi/prestataire").json()
    situation = karim.client.get(URL).json()

    assert profil["siret"] == SIRET_RECU and profil["siret_statut"] == "verifie"
    assert karim.client.get("/api/moi/prestataire/demarches").json()["periodicite"] == "trimestre"  # les rappels partent tout seuls
    # Une entreprise existe : on n'en recrée pas
    assert situation["peut_commencer"] is False and SIRET_RECU in situation["raison"]
    assert karim.client.post(URL).status_code == 400


# ---------- « J'ai déjà une entreprise » (demande de Raphael du 04/10/2026) ----------


def test_deja_une_entreprise_le_siret_suffit(fabrique_compte, fabrique_prestataire, repertoire_de_l_etat) -> None:  # noqa: F811
    paul = fabrique_prestataire()
    repertoire_de_l_etat["reponse"] = [{"siren": "443061841", "nom_complet": "ZZTEST ESSAI", "siege": {"siret": "44306184100047", "etat_administratif": "A"}}]
    faux = paul.client.post("/api/moi/prestataire/siret", json={"siret": "123"})
    ajoute = paul.client.post("/api/moi/prestataire/siret", json={"siret": "443 061 841 00047"})
    encore = paul.client.post("/api/moi/prestataire/siret", json={"siret": "44306184100047"})
    sans_profil = fabrique_compte().client.post("/api/moi/prestataire/siret", json={"siret": "44306184100047"})

    assert faux.status_code == 400 and "14 chiffres" in faux.json()["detail"]
    assert ajoute.status_code == 200 and ajoute.json()["peut_commencer"] is False and "44306184100047" in ajoute.json()["raison"]
    assert paul.client.get("/api/moi/prestataire").json()["siret_statut"] == "verifie"
    assert encore.status_code == 400 and "déjà un SIRET" in encore.json()["detail"]
    assert sans_profil.status_code == 404  # l'écran l'emmène créer son profil
    assert paul.client.post(URL).status_code == 400 and paul.client.get(URL).json()["dossier"] is None


def test_ancienne_entreprise_encore_ouverte_on_ne_recree_pas(fabrique_compte, client, metiers, repertoire_de_l_etat) -> None:  # noqa: F811
    karim = fabrique_compte()
    karim.client.post(URL)
    repertoire_de_l_etat["reponse"] = [{"siren": "443061841", "etat_administratif": "A"}]
    ouverte = karim.client.post(f"{URL}/activite", json=activite(metiers["Plombier"], ancien_siren="443 061 841"))
    repertoire_de_l_etat["reponse"] = [{"siren": "443061841", "etat_administratif": "C"}]
    fermee = karim.client.post(f"{URL}/activite", json=activite(metiers["Plombier"], ancien_siren="443061841"))

    assert ouverte.status_code == 400 and "existe encore" in ouverte.json()["detail"]
    assert fermee.status_code == 200 and fermee.json()["dossier"]["ancien_siren"] == "443061841"


# ---------- Les contrôles ----------


@pytest.mark.parametrize(("numero", "valide"), [
    (SECU, True), ("198033306312385", False), ("19803330631238", False), ("1980333063123AB", False),
    ("198032A00412366", True),  # né en Corse : 2A compte pour 19
])
def test_numero_de_securite_sociale(numero: str, valide: bool) -> None:
    assert service.numero_secu_valide(numero) is valide


def test_les_reponses_sont_controlees(fabrique_compte, client, metiers, base: Session) -> None:  # noqa: F811
    karim = fabrique_compte()
    sans_dossier = karim.client.post(f"{URL}/choix", json=CHOIX)
    karim.client.post(URL)
    infirmier = base.scalar(select(Metier.id).where(Metier.code == "infirmier"))
    refus = {
        "numéro de sécurité": karim.client.post(f"{URL}/vous", json=vous(client, numero_secu="1 98 03 33 063 123 85")),
        "site de l'État": karim.client.post(f"{URL}/vous", json=vous(client, situation_famille="marie", conjoint_travaille=True)),
        "33700": karim.client.post(f"{URL}/vous", json=vous(client, code_postal="33000")),
        "ville de naissance": karim.client.post(f"{URL}/vous", json=vous(client, naissance_commune_id=None)),
        "métier": karim.client.post(f"{URL}/activite", json=activite(infirmier)),
        "date de début": karim.client.post(f"{URL}/activite", json=activite(metiers["Plombier"], debut_le="2026-01-01")),
        "caractères": karim.client.post(f"{URL}/activite", json=activite(metiers["Plombier"], description="Court")),
        "local": karim.client.post(f"{URL}/activite", json=activite(metiers["Plombier"], lieu_travail="local")),
        "trimestre": karim.client.post(f"{URL}/choix", json=CHOIX | {"periodicite": "semaine"}),
        "n'est pas demandé": deposer(karim, "bail"),
        "n'est pas accepté": deposer(karim, "identite", b"\x89PNG zztest", "image/png"),
    }
    marie = karim.client.post(f"{URL}/vous", json=vous(client, situation_famille="marie", naissance_commune_id=None, naissance_pays="Maroc",
                                                      nationalite="autre"))
    incomplet = envoyer(karim)

    assert sans_dossier.status_code == 404
    for mot, reponse in refus.items():
        assert reponse.status_code == 400 and mot in reponse.json()["detail"], (mot, reponse.text)
    # Né à l'étranger et de nationalité étrangère : le titre de séjour est demandé en plus
    assert marie.status_code == 200 and [p["sorte"] for p in marie.json()["dossier"]["pieces"]] == ["identite", "titre_sejour"]
    assert incomplet.status_code == 400 and "Il manque" in incomplet.json()["detail"] and "la pièce d'identité" in incomplet.json()["detail"]
    assert karim.client.post(f"{URL}/effacer").json()["dossier"] is None  # il efface lui-même son brouillon


def test_il_faut_cocher_les_deux_cases_et_etre_connecte(fabrique_compte, client, metiers) -> None:  # noqa: F811
    karim = fabrique_compte()
    dossier_pret(karim, client, metiers["Plombier"])
    sans_pouvoir = karim.client.post(f"{URL}/envoi", json={"certifie": True, "pouvoir": False})

    assert sans_pouvoir.status_code == 400 and "deux cases" in sans_pouvoir.json()["detail"]
    assert client.get(URL).status_code == 401 and client.post(URL).status_code == 401
    regles = client.get("/api/creation-entreprise/metiers").json()  # ouvert à tous
    assert metiers["Plombier"] in regles["reglementes"] and metiers["Plombier"] not in regles["renvoyes"]


def test_a_17_ans_l_autorisation_des_parents_est_demandee(fabrique_compte, client) -> None:
    lucas = fabrique_compte(age=17)
    lucas.client.post(URL)
    naissance = f"{aujourd_hui().year - 17}-01-01"
    reponse = lucas.client.post(f"{URL}/vous", json=vous(client, naissance_le=naissance))
    trop_jeune = lucas.client.post(f"{URL}/vous", json=vous(client, naissance_le=f"{aujourd_hui().year - 14}-06-01"))

    assert [p["sorte"] for p in reponse.json()["dossier"]["pieces"]] == ["identite", "autorisation_parents"]
    assert trop_jeune.status_code == 400 and "16 ans" in trop_jeune.json()["detail"]


def test_photo_jpg_rangee_dans_un_pdf() -> None:
    pdf = pdf_pieces.jpeg_en_pdf(JPG)
    assert pdf.startswith(b"%PDF-1.4") and b"/DCTDecode" in pdf and b"/Width 400 /Height 300" in pdf and JPG in pdf
    assert pdf_pieces.texte_en_pdf("Pouvoir", ["Je soussigné Karim BENALI, né à Mérignac."]).startswith(b"%PDF-1.4")


# ---------- Corrections, refus, pannes ----------


def test_un_papier_a_refaire_puis_correction(fabrique_compte, client, metiers, faux_guichet, base: Session, mails_envoyes) -> None:  # noqa: F811
    karim = fabrique_compte()
    dossier_pret(karim, client, metiers["Plombier"])
    envoyer(karim)
    identifiant = en_base(base, karim).guichet_id
    pas_demande = karim.client.post(f"{URL}/correction")
    faux_guichet.demander_correction(identifiant, "La pièce d'identité est illisible.", "PJ_11")
    a_corriger = actualiser(karim)
    trop_tot = karim.client.post(f"{URL}/correction")
    deposer(karim, "identite")
    # Rappel 3 jours avant la date limite, une seule fois (le guichet attend toujours la correction)
    limite = en_base(base, karim).corriger_avant_le
    moment = datetime(limite.year, limite.month, limite.day, 9, tzinfo=reglages.FUSEAU_AFFICHAGE) - timedelta(days=2)
    rappels = [service.suivre(base, moment)["rappels"], service.suivre(base, moment)["rappels"]]
    base.commit()
    corrige = karim.client.post(f"{URL}/correction")

    assert pas_demande.status_code == 400
    assert a_corriger["statut"] == "a_corriger" and a_corriger["motif"] == "La pièce d'identité est illisible."
    assert a_corriger["corriger_avant_le"] == (aujourd_hui() + reglages.CREATION_DELAI_CORRECTION).isoformat()
    assert {p["sorte"] for p in a_corriger["pieces"] if p["a_refaire"]} == {"identite"}
    assert trop_tot.status_code == 400 and "la pièce d'identité" in trop_tot.json()["detail"]
    assert rappels == [1, 0]
    assert corrige.status_code == 200 and corrige.json()["dossier"]["statut"] == "en_examen" and corrige.json()["dossier"]["motif"] is None
    assert [a["methode"] for a in faux_guichet.appels if a["chemin"] == f"/api/formalities/{identifiant}" and a["methode"] == "PUT"] == ["PUT"]
    assert faux_guichet.dossiers[identifiant]["status"] == "VALIDATION_PENDING"  # renvoyé puis signé de nouveau
    assert any("correction est demandée" in m["sujet"] and "illisible" in m["texte"] for m in mails_envoyes)


@pytest.mark.parametrize(("geste", "statut", "mot"), [("rejeter", "refuse", "refusé"), ("expirer", "ferme", "fermé")])
def test_dossier_refuse_ou_ferme_les_donnees_sensibles_sont_effacees(geste, statut, mot, fabrique_compte, client, metiers,  # noqa: F811
                                                                    faux_guichet, base: Session, mails_envoyes) -> None:
    karim = fabrique_compte()
    dossier_pret(karim, client, metiers["Plombier"])
    envoyer(karim)
    identifiant = en_base(base, karim).guichet_id
    if geste == "rejeter":
        faux_guichet.rejeter(identifiant, "Activité incompatible avec le régime micro.")
    else:
        faux_guichet.expirer(identifiant)
    fini = actualiser(karim)
    recommence = karim.client.post(URL)

    assert fini["statut"] == statut and fini["numero_secu"] is None and all(p["efface"] for p in fini["pieces"])
    assert base.scalar(select(Fichier.id).where(Fichier.depose_par_id == karim.id)) is None
    assert any(mot in m["sujet"] for m in mails_envoyes)
    # Il peut recommencer un dossier neuf ; l'ancien reste dans la base
    assert recommence.status_code == 201 and recommence.json()["dossier"]["statut"] == "brouillon"
    assert base.scalar(select(func.count()).select_from(DossierCreation).where(DossierCreation.compte_id == karim.id)) == 2


def test_guichet_en_panne_le_dossier_reste_un_brouillon(fabrique_compte, client, metiers, faux_guichet, base: Session) -> None:  # noqa: F811
    karim = fabrique_compte()
    dossier_pret(karim, client, metiers["Plombier"])
    faux_guichet.panne = True
    panne = envoyer(karim)
    apres_panne = en_base(base, karim)
    restes = base.scalars(select(PieceDossier.sorte).where(PieceDossier.dossier_id == apres_panne.id)).all()
    faux_guichet.panne = False
    envoye = envoyer(karim)
    faux_guichet.panne = True
    pendant = actualiser(karim)  # panne pendant le suivi : rien ne casse, rien ne change

    assert panne.status_code == 503 and "ne répond pas" in panne.json()["detail"]
    assert apres_panne.statut == "brouillon" and apres_panne.guichet_id is None and sorted(restes) == ["diplome", "identite"]
    assert envoye.status_code == 200 and pendant["statut"] == "envoye"
    assert service.suivre(base, datetime.now(UTC))["erreurs"] >= 1


def test_mode_demonstration_rien_n_est_envoye_a_l_etat(fabrique_prestataire, client, metiers, faux_guichet, monkeypatch) -> None:  # noqa: F811
    monkeypatch.setattr(config, "INPI_IDENTIFIANT", "")  # pas de compte INPI : comme sur le PC de Raphael aujourd'hui
    karim = fabrique_prestataire()
    pret = dossier_pret(karim, client, metiers["Plombier"])
    envoye = envoyer(karim).json()["dossier"]
    accepte = actualiser(karim)

    assert pret["demonstration"] is True and envoye["statut"] == "envoye" and envoye["guichet_numero"] == "DÉMONSTRATION"
    assert faux_guichet.appels == []
    assert accepte["statut"] == "accepte" and accepte["siret_recu"] == reglages.CREATION_SIRET_DEMONSTRATION
    assert karim.client.get("/api/moi/prestataire").json()["siret"] is None  # le faux SIRET ne va jamais dans le profil


def test_brouillon_abandonne_depuis_30_jours_efface(fabrique_compte, client, metiers, base: Session) -> None:  # noqa: F811
    karim, julie = fabrique_compte(), fabrique_compte()
    dossier_pret(karim, client, metiers["Plombier"])
    dossier_pret(julie, client, metiers["Plombier"])
    base.execute(text("UPDATE dossier_creation SET modifie_le = now() - interval '31 days' WHERE compte_id = :id"), {"id": karim.id})
    base.commit()
    bilan = service.suivre(base, datetime.now(UTC))
    base.commit()

    assert bilan["brouillons_effaces"] >= 1
    assert en_base(base, karim) is None and base.scalar(select(Fichier.id).where(Fichier.depose_par_id == karim.id)) is None
    assert en_base(base, julie).statut == "brouillon"  # modifié aujourd'hui : gardé
