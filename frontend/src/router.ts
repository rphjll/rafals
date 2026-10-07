import { createRouter, createWebHistory } from 'vue-router'
import AccueilPage from './pages/AccueilPage.vue'
import AdministrationPage from './pages/AdministrationPage.vue'
import AgendaPage from './pages/AgendaPage.vue'
import AnnonceFormulairePage from './pages/AnnonceFormulairePage.vue'
import AnnoncePage from './pages/AnnoncePage.vue'
import ComptePage from './pages/ComptePage.vue'
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
import MesAnnoncesPage from './pages/MesAnnoncesPage.vue'
import MesDemandesPage from './pages/MesDemandesPage.vue'
import MessagesPage from './pages/MessagesPage.vue'
import MonActivitePage from './pages/MonActivitePage.vue'
import MotDePasseOubliePage from './pages/MotDePasseOubliePage.vue'
import NouveauMotDePassePage from './pages/NouveauMotDePassePage.vue'
import PrestatairePage from './pages/PrestatairePage.vue'
import ProposerPage from './pages/ProposerPage.vue'
import RendezVousPage from './pages/RendezVousPage.vue'
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
    { path: '/mes-demandes', name: 'mes-demandes', component: MesDemandesPage },
    { path: '/demandes-pres-de-chez-moi', name: 'demandes-pres', component: DemandesPresPage },
    { path: '/proposer', name: 'proposer', component: ProposerPage },
    { path: '/mes-annonces', name: 'mes-annonces', component: MesAnnoncesPage },
    { path: '/mon-agenda', name: 'mon-agenda', component: AgendaPage },
    { path: '/mes-annonces/nouvelle', name: 'annonce-nouvelle', component: AnnonceFormulairePage },
    { path: '/mes-annonces/:id(\\d+)', name: 'annonce-modifier', component: AnnonceFormulairePage },
    { path: '/annonces/:id(\\d+)', name: 'annonce', component: AnnoncePage },
    { path: '/prestataires/:id(\\d+)', name: 'prestataire', component: PrestatairePage },
    { path: '/rendez-vous', name: 'rendez-vous', component: RendezVousPage },
    { path: '/devis', name: 'devis', component: DevisPage },
    { path: '/factures', name: 'factures', component: FacturesPage },
    { path: '/demarches', name: 'demarches', component: DemarchesPage },
    { path: '/creer-mon-auto-entreprise', name: 'creer-auto-entreprise', component: CreerAutoEntreprisePage },
    { path: '/creer-mon-auto-entreprise/guide', name: 'guide-auto-entreprise', component: GuideAutoEntreprisePage },
    { path: '/compte', name: 'compte', component: ComptePage },
    { path: '/administration', name: 'administration', component: AdministrationPage },
    { path: '/:chemin(.*)*', name: 'introuvable', ...bientot('Page introuvable', '') },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
