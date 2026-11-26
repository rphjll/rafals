import { createRouter, createWebHistory } from 'vue-router'
// L'accueil est chargé tout de suite ; les autres pages seulement quand on y va (chargement « à la demande »,
// 25/11/2026) : avant, les 30 pages et leurs 180 fichiers partaient tous à l'ouverture du site.
import AccueilPage from './pages/AccueilPage.vue'
const AdministrationPage = () => import('./pages/AdministrationPage.vue')
const AgendaPage = () => import('./pages/AgendaPage.vue')
const AvisClientPage = () => import('./pages/AvisClientPage.vue')
const ClientPage = () => import('./pages/ClientPage.vue')
const BientotPage = () => import('./pages/BientotPage.vue')
const CataloguePage = () => import('./pages/CataloguePage.vue')
const CreerAutoEntreprisePage = () => import('./pages/CreerAutoEntreprisePage.vue')
const GuideAutoEntreprisePage = () => import('./pages/GuideAutoEntreprisePage.vue')
const DemandesPage = () => import('./pages/DemandesPage.vue')
const DemarchesPage = () => import('./pages/DemarchesPage.vue')
const DevisPage = () => import('./pages/DevisPage.vue')
const ConnexionPage = () => import('./pages/ConnexionPage.vue')
const InscriptionPage = () => import('./pages/InscriptionPage.vue')
const MesAbonnementsPage = () => import('./pages/MesAbonnementsPage.vue')
const MaCarteVisitePage = () => import('./pages/MaCarteVisitePage.vue')
const MesClientsPage = () => import('./pages/MesClientsPage.vue')
const MesAvisRecusPage = () => import('./pages/MesAvisRecusPage.vue')
const MessagesPage = () => import('./pages/MessagesPage.vue')
const MoiPage = () => import('./pages/MoiPage.vue')
const NouvelleDemandePage = () => import('./pages/NouvelleDemandePage.vue')
const MonActivitePage = () => import('./pages/MonActivitePage.vue')
const MotDePasseOubliePage = () => import('./pages/MotDePasseOubliePage.vue')
const NouveauMotDePassePage = () => import('./pages/NouveauMotDePassePage.vue')
const ParametresPage = () => import('./pages/ParametresPage.vue')
const PrestatairePage = () => import('./pages/PrestatairePage.vue')
const ProfilPage = () => import('./pages/ProfilPage.vue')
const TrouverPage = () => import('./pages/TrouverPage.vue')
const VerifierAdressePage = () => import('./pages/VerifierAdressePage.vue')

// Les entrées du menu pas encore construites mènent à « Bientôt disponible » :
// un clic produit toujours quelque chose de visible (CONVENTIONS-IHM).
const bientot = (titre: string, arrivee: string) => ({
  component: BientotPage,
  props: { titre, arrivee },
})

export const routeur = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'accueil', component: AccueilPage },
    { path: '/catalogue', name: 'catalogue', component: CataloguePage },
    { path: '/inscription', name: 'inscription', component: InscriptionPage },
    { path: '/connexion', name: 'connexion', component: ConnexionPage },
    { path: '/mot-de-passe-oublie', name: 'mot-de-passe-oublie', component: MotDePasseOubliePage },
    // Adresses des liens envoyés par mail (voir backend/app/services/comptes.py)
    { path: '/verifier-adresse', name: 'verifier-adresse', component: VerifierAdressePage },
    { path: '/nouveau-mot-de-passe', name: 'nouveau-mot-de-passe', component: NouveauMotDePassePage },
    { path: '/trouver', name: 'trouver', component: TrouverPage },
    { path: '/messages', name: 'messages', component: MessagesPage },
    { path: '/messages/:id(\\d+)', name: 'conversation', component: MessagesPage },
    { path: '/mon-activite', name: 'mon-activite', component: MonActivitePage },
    { path: '/mes-clients', name: 'mes-clients', component: MesClientsPage },
    { path: '/ma-carte-de-visite', name: 'ma-carte-de-visite', component: MaCarteVisitePage },
    { path: '/mes-abonnements', name: 'mes-abonnements', component: MesAbonnementsPage },
    { path: '/clients/:id(\\d+)/avis', name: 'avis-client', component: AvisClientPage },
    { path: '/alertes', redirect: '/parametres#notifications' }, // ancienne page, déplacée dans Paramètres le 21/10/2026
    { path: '/mes-avis-recus', name: 'mes-avis-recus', component: MesAvisRecusPage },
    { path: '/clients/:id(\\d+)', name: 'client', component: ClientPage },
    // Onglet « Demandes » (lot 14.2) ; les 2 anciennes pages y mènent (liens des mails et des notifications)
    { path: '/demandes', name: 'demandes', component: DemandesPage },
    { path: '/demandes/nouvelle', name: 'nouvelle-demande', component: NouvelleDemandePage },
    { path: '/mes-demandes', redirect: { path: '/demandes', query: { onglet: 'miennes' } } },
    { path: '/demandes-pres-de-chez-moi', redirect: '/demandes' },
    // « Mon profil » réunit les anciennes pages « Mon profil » (/proposer) et « Mon compte » (/compte) depuis le 07/10/2026.
    // Les anciens liens y arrivent avec leurs réglages (ex. /proposer?siret=91234567800017, retour de Stripe).
    { path: '/profil', name: 'profil', component: ProfilPage },
    // Thème clair ou sombre (17/10/2026), ouverte depuis la liste sous le prénom
    { path: '/parametres', name: 'parametres', component: ParametresPage },
    // « Moi » : la page du compte de la barre du bas, sur téléphone (grande maquette, 10/11/2026)
    { path: '/moi', name: 'moi', component: MoiPage },
    { path: '/proposer', redirect: (vers) => ({ path: '/profil', query: { ...vers.query, proposer: '1' } }) },
    { path: '/compte', redirect: (vers) => ({ path: '/profil', query: vers.query }) },
    { path: '/mon-agenda', name: 'mon-agenda', component: AgendaPage },
    { path: '/prestataires/:id(\\d+)', name: 'prestataire', component: PrestatairePage },
    // L'ancienne page « Mes rendez-vous » est devenue le calendrier du client, dans « Mon agenda » (07/10/2026).
    // Les anciens liens et le retour du paiement par carte (?rdv=12&paiement=fait) y arrivent avec leurs réglages.
    { path: '/rendez-vous', redirect: (vers) => ({ path: '/mon-agenda', query: { ...vers.query, onglet: undefined, calendrier: 'client' } }) },
    { path: '/devis', name: 'devis', component: DevisPage },
    // « Mes factures » est l'onglet « Factures » de « Devis et factures » depuis le 25/11/2026 (demande de Raphael)
    { path: '/factures', redirect: { path: '/devis', query: { onglet: 'factures' } } },
    { path: '/demarches', name: 'demarches', component: DemarchesPage },
    { path: '/creer-mon-auto-entreprise', name: 'creer-auto-entreprise', component: CreerAutoEntreprisePage },
    { path: '/creer-mon-auto-entreprise/guide', name: 'guide-auto-entreprise', component: GuideAutoEntreprisePage },
    { path: '/administration', name: 'administration', component: AdministrationPage },
    { path: '/:chemin(.*)*', name: 'introuvable', ...bientot('Page introuvable', '') },
  ],
  // Une adresse avec « # » descend à la partie visée (ex. /parametres#abonnements).
  // Bouton « retour » du navigateur : on retrouve l'endroit où on était.
  // Même page, seul le réglage change (ex. /profil → /profil?onglet=activite, un clic sur un onglet) : on ne bouge pas.
  // Sinon (une autre page) : haut de page.
  scrollBehavior: (vers, depuis, positionGardee) => {
    if (vers.hash) return { el: vers.hash, top: 90, behavior: 'smooth' }
    if (positionGardee) return positionGardee
    if (vers.path === depuis.path) return false
    return { top: 0 }
  },
})
