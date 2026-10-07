// Les fonctions rangées dans « Mon activité » (.doc/ihm/RM-MON-ACTIVITE-IHM.md) : la page en fait des tuiles, et le
// sous-menu (useMenu) reprend celles qui ont leur propre page. Liste validée par Raphael le 07/10/2026 ;
// « Messages » et « Mon profil » n'y sont pas : ce sont des onglets à part.

export type GroupeActivite = 'clients' | 'gerer' | 'connaitre' | 'demarches'

/** Qui voit la tuile : tout le monde, seulement un prestataire, ou seulement un compte sans profil de prestataire */
type Pour = 'tous' | 'prestataire' | 'client'

export interface FonctionActivite {
  cle: string
  groupe: GroupeActivite
  texte: string
  detail: string
  /** Tracé dans outils/pictos.ts */
  picto: string
  pour: Pour
  /** Page ouverte par la tuile ; sans page : fonction pas encore construite, tuile « bientôt » */
  vers?: string | ((prestataireId: number) => string)
  /** Reprise dans le sous-menu affiché sur les pages du groupe */
  sousMenu?: boolean
}

export const GROUPES_ACTIVITE: { cle: GroupeActivite; titre: string; titreClient?: string }[] = [
  { cle: 'clients', titre: 'Trouver des clients' },
  { cle: 'gerer', titre: 'Gérer mon activité', titreClient: 'Mes services' },
  { cle: 'connaitre', titre: 'Me faire connaître' },
  { cle: 'demarches', titre: 'Mes démarches' },
]

export const FONCTIONS_ACTIVITE: FonctionActivite[] = [
  { cle: 'demandes-pres', groupe: 'clients', texte: 'Demandes près de chez moi', detail: 'Les clients qui cherchent mon métier', picto: 'repere', pour: 'prestataire', vers: '/demandes-pres-de-chez-moi', sousMenu: true },
  { cle: 'alertes', groupe: 'clients', texte: 'Alertes', detail: 'Un mail à chaque nouvelle demande', picto: 'cloche', pour: 'prestataire' },
  { cle: 'mise-en-avant', groupe: 'clients', texte: 'Être mis en avant', detail: 'Apparaître en premier dans les résultats', picto: 'evenements', pour: 'prestataire' },

  { cle: 'mes-demandes', groupe: 'gerer', texte: 'Mes demandes', detail: 'Ce que j’ai publié, et les réponses', picto: 'liste', pour: 'tous', vers: '/mes-demandes', sousMenu: true },
  { cle: 'agenda', groupe: 'gerer', texte: 'Mon agenda', detail: 'Mes horaires et mes jours fermés', picto: 'menu-reservations', pour: 'prestataire', vers: '/mon-agenda', sousMenu: true },
  { cle: 'rendez-vous', groupe: 'gerer', texte: 'Rendez-vous', detail: 'À venir et passés', picto: 'horloge', pour: 'tous', vers: '/rendez-vous', sousMenu: true },
  { cle: 'devis', groupe: 'gerer', texte: 'Devis', detail: 'Demandes de devis et devis envoyés', picto: 'document', pour: 'tous', vers: '/devis', sousMenu: true },
  { cle: 'factures', groupe: 'gerer', texte: 'Factures', detail: 'Toutes mes factures en PDF', picto: 'euro', pour: 'tous', vers: '/factures', sousMenu: true },
  { cle: 'paiements-prestataire', groupe: 'gerer', texte: 'Paiements', detail: 'Ce que j’ai encaissé, par carte et en espèces', picto: 'carte-bancaire', pour: 'prestataire', vers: '/mon-agenda?onglet=paiements' },
  { cle: 'paiements-client', groupe: 'gerer', texte: 'Paiements', detail: 'Ce que j’ai payé par carte', picto: 'carte-bancaire', pour: 'client', vers: '/compte' },
  { cle: 'clients', groupe: 'gerer', texte: 'Mes clients', detail: 'Les personnes pour qui j’ai déjà travaillé', picto: 'services-personne', pour: 'prestataire' },
  { cle: 'avis-client', groupe: 'gerer', texte: 'Mes avis', detail: 'À donner après un rendez-vous passé', picto: 'evenements', pour: 'client', vers: '/rendez-vous?onglet=passes' },

  { cle: 'avis-prestataire', groupe: 'connaitre', texte: 'Mes avis', detail: 'Ce que mes clients disent de moi', picto: 'evenements', pour: 'prestataire', vers: (id) => `/prestataires/${id}` },
  { cle: 'carte-visite', groupe: 'connaitre', texte: 'Ma carte de visite', detail: 'À imprimer, avec un carré à scanner', picto: 'carte-bancaire', pour: 'prestataire' },
  { cle: 'site', groupe: 'connaitre', texte: 'Mon site', detail: 'Une page à mon nom, visible sur Google', picto: 'numerique-bureau', pour: 'prestataire' },

  { cle: 'urssaf', groupe: 'demarches', texte: 'Déclarer à l’URSSAF', detail: 'Mes déclarations et leurs rappels', picto: 'banque', pour: 'prestataire', vers: '/demarches', sousMenu: true },
  { cle: 'auto-entreprise', groupe: 'demarches', texte: 'Mon auto-entreprise', detail: 'La créer et suivre mon dossier', picto: 'drapeau', pour: 'prestataire', vers: '/creer-mon-auto-entreprise' },
]

/** Les fonctions que ce compte voit (prestataireId : null pour un compte sans profil de prestataire) */
export function fonctionsPour(prestataireId: number | null): FonctionActivite[] {
  return FONCTIONS_ACTIVITE.filter((f) => f.pour === 'tous' || (f.pour === 'prestataire') === (prestataireId !== null))
}

/** L'adresse ouverte par une fonction, ou null si elle n'est pas encore construite */
export function adresseDe(fonction: FonctionActivite, prestataireId: number | null): string | null {
  if (typeof fonction.vers === 'function') return prestataireId === null ? null : fonction.vers(prestataireId)
  return fonction.vers ?? null
}
