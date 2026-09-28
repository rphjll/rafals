<script setup lang="ts">
// En-tête commun à toutes les pages (.doc/ihm/RM-ENTETE-IHM.md).
// Sous 768 px de large, le menu se replie derrière le bouton ☰.
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { messageErreur } from '../api'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import AppBouton from './ui/AppBouton.vue'

const menuOuvert = ref(false)
const route = useRoute()
const routeur = useRouter()
const { compte, chargementFait, seDeconnecter } = useCompte()
const { afficherMessage } = useMessage()
watch(() => route.fullPath, () => (menuOuvert.value = false))

const liens = computed(() => [
  { vers: '/trouver', texte: 'Trouver un prestataire' },
  { vers: '/proposer', texte: 'Proposer mes services' },
  { vers: '/rendez-vous', texte: 'Mes rendez-vous' },
  { vers: '/compte', texte: 'Mon compte' },
  // Visible seulement des administrateurs (lot 1.4)
  ...(compte.value?.est_administrateur ? [{ vers: '/administration', texte: 'Administration' }] : []),
])

async function deconnexion() {
  try {
    await seDeconnecter()
    afficherMessage('Vous êtes déconnecté.')
    routeur.push('/')
  } catch (erreur) {
    afficherMessage(messageErreur(erreur), 'erreur')
  }
}
</script>

<template>
  <header class="sticky top-[env(safe-area-inset-top,0px)] z-10 border-b border-bord bg-surface px-4">
    <div class="relative mx-auto flex h-[60px] max-w-[1080px] items-center gap-4">
      <RouterLink to="/" class="font-titre text-2xl font-bold tracking-tight text-primaire" aria-label="Accueil rafals">
        rafals<span class="text-accent">.</span>
      </RouterLink>
      <button
        type="button"
        class="ml-auto h-[38px] w-[42px] rounded-rafals border border-bord text-xl text-texte md:hidden"
        :aria-expanded="menuOuvert"
        aria-controls="menu-principal"
        :aria-label="menuOuvert ? 'Fermer le menu' : 'Ouvrir le menu'"
        @click="menuOuvert = !menuOuvert"
      >
        ☰
      </button>
      <nav
        id="menu-principal"
        class="absolute top-[60px] right-[-16px] left-[-16px] flex-col border-b border-bord bg-surface px-4 pt-2 pb-3.5 md:static md:ml-auto md:flex md:flex-row md:items-center md:gap-1 md:border-0 md:p-0"
        :class="menuOuvert ? 'flex' : 'hidden'"
      >
        <RouterLink
          v-for="lien in liens"
          :key="lien.vers"
          :to="lien.vers"
          class="rounded-rafals px-2.5 py-2.5 font-medium text-texte-doux hover:bg-primaire-doux hover:text-primaire md:py-2"
          active-class="bg-primaire-doux text-primaire"
        >
          {{ lien.texte }}
        </RouterLink>
        <!-- Tant qu'on ne sait pas si quelqu'un est connecté, on n'affiche rien (évite un clignotement) -->
        <div v-if="chargementFait" class="flex flex-wrap items-center gap-2 pt-2 md:pt-0 md:pl-2">
          <template v-if="compte">
            <span class="px-1 font-semibold">{{ compte.prenom }}</span>
            <AppBouton variante="secondaire" @click="deconnexion">Se déconnecter</AppBouton>
          </template>
          <AppBouton v-else @click="routeur.push('/connexion')">Se connecter</AppBouton>
        </div>
      </nav>
    </div>
  </header>
</template>
