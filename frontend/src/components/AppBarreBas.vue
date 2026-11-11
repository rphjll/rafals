<script setup lang="ts">
// Barre du bas, sur téléphone seulement (.doc/ihm/RM-ENTETE-IHM.md), identique à la grande maquette : 6 entrées
// (Accueil, Trouver, Demandes, Messages, Activité, Moi), une icône et un mot court. Sur ordinateur : l'en-tête.
import { useMenu } from '../composables/useMenu'
import AppIcone from './ui/AppIcone.vue'

const { entreesBas } = useMenu()
</script>

<template>
  <div class="basbar">
    <nav aria-label="Menu">
      <RouterLink
        v-for="entree in entreesBas"
        :key="entree.texte"
        :to="entree.vers"
        :class="{ actif: entree.actif }"
        :aria-current="entree.actif ? 'page' : undefined"
      >
        <AppIcone :nom="entree.icone" />{{ entree.court }}
        <span
          v-if="entree.compteur"
          class="badge"
          :aria-label="`${entree.compteur} conversation${entree.compteur > 1 ? 's' : ''} non lue${entree.compteur > 1 ? 's' : ''}`"
        >{{ entree.compteur }}</span>
      </RouterLink>
    </nav>
  </div>
</template>
