import { createRouter, createWebHistory } from 'vue-router'
import AccueilPage from './pages/AccueilPage.vue'
import BientotPage from './pages/BientotPage.vue'
import CataloguePage from './pages/CataloguePage.vue'

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
    { path: '/trouver', name: 'trouver', ...bientot('Trouver un prestataire', 'avec la recherche (niveau 4)') },
    { path: '/proposer', name: 'proposer', ...bientot('Proposer mes services', 'au lot 2.5') },
    { path: '/rendez-vous', name: 'rendez-vous', ...bientot('Mes rendez-vous', 'avec les rendez-vous (niveau 4)') },
    { path: '/compte', name: 'compte', ...bientot('Mon compte', 'aux lots 1.2 et 1.4') },
    { path: '/:chemin(.*)*', name: 'introuvable', ...bientot('Page introuvable', '') },
  ],
  scrollBehavior: () => ({ top: 0 }),
})
