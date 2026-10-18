import { createRouter, createWebHistory } from 'vue-router'
import AccueilPage from './pages/AccueilPage.vue'
import AdministrationPage from './pages/AdministrationPage.vue'
import AgendaPage from './pages/AgendaPage.vue'
import AlertesPage from './pages/AlertesPage.vue'
import AvisClientPage from './pages/AvisClientPage.vue'
import ClientPage from './pages/ClientPage.vue'
import BientotPage from './pages/BientotPage.vue'
import CataloguePage from './pages/CataloguePage.vue'
import CreerAutoEntreprisePage from './pages/CreerAutoEntreprisePage.vue'
import GuideAutoEntreprisePage from './pages/GuideAutoEntreprisePage.vue'
import DemandesPresPage from './pages/DemandesPresPage.vue'
import DemarchesPage from './pages/DemarchesPage.vue'
import DevisPage from './pages/DevisPage.vue'
import FacturesPage from './pages/FacturesPage.vue'
import ConnexionPage from './pages/ConnexionPage.vue'
import InscriptionPage from './pages/InscriptionPage.vue'
import MesClientsPage from './pages/MesClientsPage.vue'
import MesAvisRecusPage from './pages/MesAvisRecusPage.vue'
import MesDemandesPage from './pages/MesDemandesPage.vue'
import MessagesPage from './pages/MessagesPage.vue'
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
    { path: '/clients/:id(\\d+)/avis', name: 'avis-client', component: AvisClientPage },
    { path: '/alertes', name: 'alertes', component: AlertesPage },
    { path: '/mes-avis-recus', name: 'mes-avis-recus', component: MesAvisRecusPage },
    { path: '/clients/:id(\\d+)', name: 'client', component: ClientPage },
    { path: '/mes-demandes', name: 'mes-demandes', component: MesDemandesPage },
    { path: '/demandes-pres-de-chez-moi', name: 'demandes-pres', component: DemandesPresPage },
    // « Mon profil » réunit les anciennes pages « Mon profil » (/proposer) et « Mon compte » (/compte) depuis le 07/10/2026.
    // Les anciens liens y arrivent avec leurs réglages (ex. /proposer?siret=91234567800017, retour de Stripe).
    { path: '/profil', name: 'profil', component: ProfilPage },
    // Thème clair ou sombre (17/10/2026), ouverte depuis la liste sous le prénom
    { path: '/parametres', name: 'parametres', component: ParametresPage },
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
  scrollBehavior: () => ({ top: 0 }),
})
