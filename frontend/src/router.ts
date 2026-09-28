import { createRouter, createWebHistory } from 'vue-router'
import AccueilPage from './pages/AccueilPage.vue'
import AdministrationPage from './pages/AdministrationPage.vue'
import ComptePage from './pages/ComptePage.vue'
import BientotPage from './pages/BientotPage.vue'
import CataloguePage from './pages/CataloguePage.vue'
import ConnexionPage from './pages/ConnexionPage.vue'
import InscriptionPage from './pages/InscriptionPage.vue'
import MotDePasseOubliePage from './pages/MotDePasseOubliePage.vue'
import NouveauMotDePassePage from './pages/NouveauMotDePassePage.vue'
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
    { path: '/trouver', name: 'trouver', ...bientot('Trouver un prestataire', 'avec la recherche (niveau 4)') },
    { path: '/proposer', name: 'proposer', ...bientot('Proposer mes services', 'au lot 2.5') },
    { path: '/rendez-vous', name: 'rendez-vous', ...bientot('Mes rendez-vous', 'avec les rendez-vous (niveau 4)') },
    { path: '/compte', name: 'compte', component: ComptePage },
    { path: '/administration', name: 'administration', component: AdministrationPage },
    { path: '/:chemin(.*)*', name: 'introuvable', ...bientot('Page introuvable', '') },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
