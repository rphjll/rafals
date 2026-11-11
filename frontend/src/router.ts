import { createRouter, createWebHistory } from 'vue-router'
import AccueilPage from './pages/AccueilPage.vue'
import AdministrationPage from './pages/AdministrationPage.vue'
import AgendaPage from './pages/AgendaPage.vue'
import AvisClientPage from './pages/AvisClientPage.vue'
import ClientPage from './pages/ClientPage.vue'
import BientotPage from './pages/BientotPage.vue'
import CataloguePage from './pages/CataloguePage.vue'
import CreerAutoEntreprisePage from './pages/CreerAutoEntreprisePage.vue'
import GuideAutoEntreprisePage from './pages/GuideAutoEntreprisePage.vue'
import DemandesPage from './pages/DemandesPage.vue'
import DemarchesPage from './pages/DemarchesPage.vue'
import DevisPage from './pages/DevisPage.vue'
import FacturesPage from './pages/FacturesPage.vue'
import ConnexionPage from './pages/ConnexionPage.vue'
import InscriptionPage from './pages/InscriptionPage.vue'
import MesAbonnementsPage from './pages/MesAbonnementsPage.vue'
import MaCarteVisitePage from './pages/MaCarteVisitePage.vue'
import MesClientsPage from './pages/MesClientsPage.vue'
import MesAvisRecusPage from './pages/MesAvisRecusPage.vue'
import MessagesPage from './pages/MessagesPage.vue'
import MoiPage from './pages/MoiPage.vue'
import NouvelleDemandePage from './pages/NouvelleDemandePage.vue'
import MonActivitePage from './pages/MonActivitePage.vue'
import MotDePasseOubliePage from './pages/MotDePasseOubliePage.vue'
import NouveauMotDePassePage from './pages/NouveauMotDePassePage.vue'
import ParametresPage from './pages/ParametresPage.vue'
import PrestatairePage from './pages/PrestatairePage.vue'
import ProfilPage from './pages/ProfilPage.vue'
import TrouverPage from './pages/TrouverPage.vue'
import VerifierAdressePage from './pages/VerifierAdressePage.vue'

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
    { path: '/factures', name: 'factures', component: FacturesPage },
    { path: '/demarches', name: 'demarches', component: DemarchesPage },
    { path: '/creer-mon-auto-entreprise', name: 'creer-auto-entreprise', component: CreerAutoEntreprisePage },
    { path: '/creer-mon-auto-entreprise/guide', name: 'guide-auto-entreprise', component: GuideAutoEntreprisePage },
    { path: '/administration', name: 'administration', component: AdministrationPage },
    { path: '/:chemin(.*)*', name: 'introuvable', ...bientot('Page introuvable', '') },
  ],
  // Une adresse avec « # » descend à la partie visée (ex. /parametres#abonnements), sinon haut de page
  scrollBehavior: (vers) => (vers.hash ? { el: vers.hash, top: 90, behavior: 'smooth' } : { top: 0 }),
})
