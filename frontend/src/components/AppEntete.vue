<script setup lang="ts">
// En-tête commun à toutes les pages (.doc/ihm/RM-ENTETE-IHM.md).
// Sous 768 px de large, le menu se replie derrière le bouton ☰.
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const menuOuvert = ref(false)
const route = useRoute()
watch(() => route.fullPath, () => (menuOuvert.value = false))

const liens = [
  { vers: '/trouver', texte: 'Trouver un prestataire' },
  { vers: '/proposer', texte: 'Proposer mes services' },
  { vers: '/rendez-vous', texte: 'Mes rendez-vous' },
  { vers: '/compte', texte: 'Mon compte' },
]
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
      </nav>
    </div>
  </header>
</template>
