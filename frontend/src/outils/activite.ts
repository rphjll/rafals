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
  { cle: 'alertes', groupe: 'clients', texte: 'Alertes', detail: 'Un mail à chaque nouvelle demande', picto: 'cloche', pour: 'prestataire', vers: '/alertes', sousMenu: true },
  { cle: 'mise-en-avant', groupe: 'clients', texte: 'Être mis en avant', detail: 'Apparaître en premier dans les résultats', picto: 'evenements', pour: 'prestataire' },

  { cle: 'mes-demandes', groupe: 'gerer', texte: 'Mes demandes', detail: 'Ce que j’ai publié, et les réponses', picto: 'liste', pour: 'tous', vers: '/mes-demandes', sousMenu: true },
  { cle: 'mes-avis-recus', groupe: 'gerer', texte: 'Mes avis reçus', detail: 'Ce que les prestataires disent de moi', picto: 'liste', pour: 'tous', vers: '/mes-avis-recus', sousMenu: true },
  // Un seul endroit pour les rendez-vous : le calendrier (la page « Rendez-vous » a été retirée le 07/10/2026)
  { cle: 'agenda-prestataire', groupe: 'gerer', texte: 'Mon agenda', detail: 'Mes rendez-vous, mes horaires, mes jours fermés', picto: 'menu-reservations', pour: 'prestataire', vers: '/mon-agenda', sousMenu: true },
  { cle: 'agenda-client', groupe: 'gerer', texte: 'Mon agenda', detail: 'Le calendrier de mes rendez-vous', picto: 'menu-reservations', pour: 'client', vers: '/mon-agenda', sousMenu: true },
  { cle: 'devis', groupe: 'gerer', texte: 'Devis', detail: 'Demandes de devis et devis envoyés', picto: 'document', pour: 'tous', vers: '/devis', sousMenu: true },
  { cle: 'factures', groupe: 'gerer', texte: 'Factures', detail: 'Toutes mes factures en PDF', picto: 'euro', pour: 'tous', vers: '/factures', sousMenu: true },
  { cle: 'paiements-prestataire', groupe: 'gerer', texte: 'Paiements', detail: 'Ce que j’ai encaissé, par carte et en espèces', picto: 'carte-bancaire', pour: 'prestataire', vers: '/mon-agenda?onglet=paiements' },
  { cle: 'paiements-client', groupe: 'gerer', texte: 'Paiements', detail: 'Ce que j’ai payé par carte', picto: 'carte-bancaire', pour: 'client', vers: '/compte' },
  { cle: 'clients', groupe: 'gerer', texte: 'Mes clients', detail: 'Les personnes pour qui j’ai déjà travaillé', picto: 'services-personne', pour: 'prestataire', vers: '/mes-clients', sousMenu: true },
  { cle: 'avis-client', groupe: 'gerer', texte: 'Mes avis', detail: 'À donner après un rendez-vous passé', picto: 'evenements', pour: 'client', vers: '/mon-agenda' },

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

// ---------- Les chiffres du haut de la page (RM-MON-ACTIVITE.md, lot 10.1) ----------

export interface ChiffresPrestataire {
  demandes_pres: number
  rendez_vous_semaine: number
  devis_en_attente: number
  encaisse_mois_centimes: number
  encaisse_annee_centimes: number
  annee: number
  /** null : il facture déjà la TVA, pas de barre */
  seuil_tva_centimes: number | null
  reste_avant_seuil_centimes: number | null
}

export interface ChiffresClient {
  demandes_en_ligne: number
  conversations_a_lire: number
  rendez_vous_a_venir: number
}

/** Ce que renvoie /api/moi/activite : un seul des deux est rempli */
export interface ActiviteChiffree {
  prestataire: ChiffresPrestataire | null
  client: ChiffresClient | null
}

/** Un chiffre affiché : « 3 » + « demandes près de chez vous », et la page qui le détaille */
export interface ChiffreAffiche {
  valeur: string
  texte: string
  vers: string
}

const accorde = (nombre: number, singulier: string, pluriel: string) => (nombre > 1 ? pluriel : singulier)

/** Les chiffres dans l'ordre de l'écran ; « montant » écrit une somme (« 640,00 € »), « mois » est le mois en cours (« octobre ») */
export function chiffresAffiches(activite: ActiviteChiffree, montant: (centimes: number) => string, mois: string): ChiffreAffiche[] {
  const p = activite.prestataire
  if (p) {
    return [
      { valeur: String(p.demandes_pres), texte: accorde(p.demandes_pres, 'demande près de chez vous', 'demandes près de chez vous'), vers: '/demandes-pres-de-chez-moi' },
      { valeur: String(p.rendez_vous_semaine), texte: 'rendez-vous d’ici dimanche', vers: '/mon-agenda?onglet=rendez-vous' },
      { valeur: String(p.devis_en_attente), texte: 'devis en attente de réponse', vers: '/devis' },
      { valeur: montant(p.encaisse_mois_centimes), texte: `encaissés en ${mois}`, vers: '/mon-agenda?onglet=paiements' },
    ]
  }
  const c = activite.client
  if (!c) return []
  return [
    { valeur: String(c.demandes_en_ligne), texte: accorde(c.demandes_en_ligne, 'demande en ligne', 'demandes en ligne'), vers: '/mes-demandes' },
    { valeur: String(c.conversations_a_lire), texte: accorde(c.conversations_a_lire, 'conversation à lire', 'conversations à lire'), vers: '/messages' },
    { valeur: String(c.rendez_vous_a_venir), texte: 'rendez-vous à venir', vers: '/mon-agenda' },
  ]
}

// ---------- Mes clients (RM-MON-ACTIVITE.md § « Mes clients », lot 10.2) ----------

/** Un client du prestataire, tel que le serveur le renvoie (/api/moi/prestataire/clients) */
export interface ClientDuPrestataire {
  client_id: number
  /** « Julie Martin » tant que les coordonnées sont visibles, sinon « Julie M. » */
  nom: string
  telephone: string | null
  rendez_vous: number
  devis: number
  devis_en_attente: number
  paye_centimes: number
  prochain_rendez_vous: string | null
  dernier_rendez_vous: string | null
  /** faux pour un compte fermé */
  peut_ecrire: boolean
}

/** « 2 rendez-vous · 1 devis (1 en attente) · 85,00 € payés » */
export function resumeClient(client: ClientDuPrestataire, montant: (centimes: number) => string): string {
  const morceaux: string[] = []
  if (client.rendez_vous) morceaux.push(`${client.rendez_vous} rendez-vous`)
  if (client.devis) morceaux.push(`${client.devis} devis${client.devis_en_attente ? ` (${client.devis_en_attente} en attente)` : ''}`)
  morceaux.push(`${montant(client.paye_centimes)} ${client.paye_centimes >= 200 ? 'payés' : 'payé'}`)
  return morceaux.join(' · ')
}

/** Le détail d'un client et son profil (/api/moi/prestataire/clients/12) */
export interface FicheClient extends ClientDuPrestataire {
  /** L'adresse de son dernier rendez-vous chez lui, tant que les coordonnées sont visibles */
  adresse: string | null
  inscrit_le: string
  /** Ses rendez-vous confirmés avec moi, le plus récent d'abord */
  les_rendez_vous: { id: number; debut: string; titre: string; prix_centimes: number | null; a_venir: boolean }[]
  /** Mes devis pour lui, le plus récent d'abord */
  les_devis: { numero: string; total_centimes: number; statut: string; envoye_le: string }[]
  /** Ses demandes encore en ligne */
  demandes: { id: number; titre: string; ville: string }[]
}

const ETATS_DEVIS: Record<string, string> = {
  envoye: 'en attente de réponse',
  autre_date: 'autre date demandée',
  accepte: 'accepté',
  termine: 'travaux terminés',
  paye: 'payé',
  refuse: 'refusé',
  expire: 'expiré',
}

/** « envoye » → « en attente de réponse » ; un état inconnu est montré tel quel, sans les tirets bas */
export function etatDevis(statut: string): string {
  return ETATS_DEVIS[statut] ?? statut.replaceAll('_', ' ')
}
