<script setup lang="ts">
// Barre du bas, sur téléphone seulement (.doc/ihm/RM-ENTETE-IHM.md) : les entrées principales du menu, avec un
// pictogramme et un mot court. Sur ordinateur, ces mêmes entrées sont dans l'en-tête (AppEntete).
import { useMenu } from '../composables/useMenu'
import AppPicto from './ui/AppPicto.vue'

const { entrees } = useMenu()
</script>

<template>
  <nav
    class="carte fixed right-3 bottom-[calc(12px+env(safe-area-inset-bottom,0px))] left-3 z-10 flex gap-0.5 p-1 md:hidden"
    aria-label="Menu du bas"
  >
    <RouterLink
      v-for="entree in entrees"
      :key="entree.vers"
      :to="entree.vers"
      class="relative flex min-h-[56px] min-w-0 flex-1 flex-col items-center justify-center gap-0.5 rounded-rafals text-[11.5px] font-bold"
      :class="entree.actif ? 'bg-primaire-doux text-primaire' : 'text-texte-doux'"
      :aria-current="entree.actif ? 'page' : undefined"
    >
      <AppPicto :code="entree.picto" :taille="22" />
      <span class="max-w-full truncate">{{ entree.court }}</span>
      <span
        v-if="entree.compteur"
        class="absolute top-1 left-[calc(50%+6px)] rounded-full bg-erreur px-1.5 text-[11px] font-bold text-sur-etat"
        :aria-label="`${entree.compteur} conversation${entree.compteur > 1 ? 's' : ''} non lue${entree.compteur > 1 ? 's' : ''}`"
      >
        {{ entree.compteur }}
      </span>
    </RouterLink>
  </nav>
</template>
