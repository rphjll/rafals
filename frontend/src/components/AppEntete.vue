<script setup lang="ts">
// En-tête commun (.doc/ihm/RM-ENTETE-IHM.md), identique à la grande maquette depuis le 10/11/2026 : logo, les entrées
// (Accueil, Trouver, Demandes, Messages, Mon activité), puis le bouton du compte (rond + prénom) et sa liste.
// Sous 760 px de large, les entrées et le compte passent dans la barre du bas (AppBarreBas, entrée « Moi »).
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { messageErreur } from '../api'
import { useCompte } from '../composables/useCompte'
import { useInstallation } from '../composables/useInstallation'
import { useMenu } from '../composables/useMenu'
import { useMessage } from '../composables/useMessage'
import { useNonLus } from '../composables/useNonLus'
import { useRetour } from '../composables/useRetour'
import AppBouton from './ui/AppBouton.vue'
import AppFenetre from './ui/AppFenetre.vue'
import AppIcone from './ui/AppIcone.vue'
import AppInitiales from './ui/AppInitiales.vue'
import FenetreRetour from './retours/FenetreRetour.vue'

const menuOuvert = ref(false)
const zoneCompte = ref<HTMLElement | null>(null)
const route = useRoute()
const routeur = useRouter()
const { compte, chargementFait, seDeconnecter } = useCompte()
const { entrees: liens } = useMenu()
const { afficherMessage } = useMessage()
const { actualiserNonLus } = useNonLus()
watch(compte, actualiserNonLus, { immediate: true })
watch(
  () => route.fullPath,
  () => (menuOuvert.value = false),
)
// « Un problème ? Une idée ? » (lot 13.1) : la même fenêtre s'ouvre d'ici et de la page « Moi » (téléphone)
const { retourOuvert } = useRetour()
// [Installer rafals] (RM-APPLICATION) : un clic installe (Android, ordinateur) ou explique les deux gestes (iPhone)
const { facon: faconInstaller, installer } = useInstallation()
const gestesApple = ref(false)
async function installerRafals() {
  menuOuvert.value = false
  if (faconInstaller.value === 'apple') gestesApple.value = true
  else if (await installer()) afficherMessage('rafals est installé sur cet appareil.')
}

// Un clic ou une tabulation hors de la liste du compte la referme
function sortieCompte(evenement: FocusEvent) {
  if (!zoneCompte.value?.contains(evenement.relatedTarget as Node | null)) menuOuvert.value = false
}

async function deconnexion() {
  menuOuvert.value = false
  try {
    await seDeconnecter()
    afficherMessage('Vous êtes déconnecté.')
    routeur.push('/connexion')
  } catch (erreur) {
    afficherMessage(messageErreur(erreur), 'erreur')
  }
}
</script>

<template>
  <header class="entete">
    <div class="entete-in">
      <RouterLink to="/" class="logo" aria-label="Accueil rafals">rafals<b>.</b></RouterLink>
      <nav class="nav" aria-label="Menu principal">
        <RouterLink v-for="lien in liens" :key="lien.vers" :to="lien.vers" :class="{ actif: lien.actif }" :aria-current="lien.actif ? 'page' : undefined">
          <AppIcone :nom="lien.icone" />{{ lien.texte }}
          <span
            v-if="lien.compteur"
            class="badge"
            :aria-label="`${lien.compteur} conversation${lien.compteur > 1 ? 's' : ''} non lue${lien.compteur > 1 ? 's' : ''}`"
          >{{ lien.compteur }}</span>
        </RouterLink>
      </nav>
      <!-- Tant qu'on ne sait pas si quelqu'un est connecté, on n'affiche rien (évite un clignotement) -->
      <div v-if="chargementFait" ref="zoneCompte" class="compte" @focusout="sortieCompte" @keydown.esc="menuOuvert = false">
        <template v-if="compte">
          <button type="button" class="compte-btn" :aria-expanded="menuOuvert" aria-controls="menu-compte" @click="menuOuvert = !menuOuvert">
            <AppInitiales :nom="compte.prenom" />{{ compte.prenom }}
          </button>
          <div v-if="menuOuvert" id="menu-compte" class="menu">
            <RouterLink to="/profil"><AppIcone nom="moi" />Mon profil</RouterLink>
            <RouterLink to="/mes-abonnements"><AppIcone nom="coeur" />Mes abonnements</RouterLink>
            <RouterLink to="/parametres"><AppIcone nom="reglages" />Paramètres</RouterLink>
            <!-- Visible seulement des administrateurs (lot 1.4) -->
            <RouterLink v-if="compte.est_administrateur" to="/administration"><AppIcone nom="bouclier" />Administration</RouterLink>
            <button type="button" @click="(menuOuvert = false), (retourOuvert = true)"><AppIcone nom="messages" />Un problème ? Une idée ?</button>
            <button v-if="faconInstaller" type="button" @click="installerRafals"><AppIcone nom="telecharger" />Installer rafals</button>
            <hr />
            <button type="button" @click="deconnexion"><AppIcone nom="sortir" />Se déconnecter</button>
          </div>
        </template>
        <RouterLink v-else class="btn btn-1 btn-petit" to="/connexion">Se connecter</RouterLink>
      </div>
    </div>
    <FenetreRetour :ouverte="retourOuvert" @fermer="retourOuvert = false" />
    <AppFenetre :ouverte="gestesApple" titre="Installer rafals sur votre iPhone" @fermer="gestesApple = false">
      <ol class="flex list-decimal flex-col gap-2 pl-5 text-texte">
        <li>En bas de l'écran de Safari, touchez le bouton <b>Partager</b> (un carré avec une flèche vers le haut).</li>
        <li>Faites défiler, puis touchez <b>« Sur l'écran d'accueil »</b>.</li>
        <li>Touchez <b>Ajouter</b> : l'icône rafals apparaît à côté de vos autres applications.</li>
      </ol>
      <template #pied>
        <AppBouton @click="gestesApple = false">J'ai compris</AppBouton>
      </template>
    </AppFenetre>
  </header>
</template>
