<script setup lang="ts">
// Sous-menu de « Mon activité » (.doc/ihm/RM-ENTETE-IHM.md) : affiché sur ses pages (Rendez-vous, Devis, Mon agenda…).
// Il est posé sous l'en-tête, au-dessus de la page : les pages elles-mêmes ne changent pas.
import { useMenu } from '../composables/useMenu'

const { sousMenu, estSur } = useMenu()
</script>

<template>
  <nav v-if="sousMenu.length" class="border-b border-bord bg-surface px-4" aria-label="Pages du groupe">
    <div class="mx-auto flex max-w-[1080px] gap-1.5 overflow-x-auto">
      <RouterLink
        v-for="lien in sousMenu"
        :key="lien.vers"
        :to="lien.vers"
        class="-mb-px flex min-h-[42px] shrink-0 items-center border-b-[3px] px-3 font-semibold hover:text-primaire"
        :class="estSur(lien.vers) ? 'border-primaire text-primaire' : 'border-transparent text-texte-doux'"
        :aria-current="estSur(lien.vers) ? 'page' : undefined"
      >
        {{ lien.texte }}
      </RouterLink>
    </div>
  </nav>
</template>
