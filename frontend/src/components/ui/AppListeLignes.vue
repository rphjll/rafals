<script setup lang="ts">
// Liste de lignes qui se déplient (« Mon profil » façon Instagram, 21/10/2026) : chaque carte (AppSection) posée
// dedans devient une ligne « picto, titre, résumé, › » ; un clic l'ouvre sur place avec ses boutons habituels.
// « resumes » : la petite phrase sous un titre, ex. { 'Mes informations': 'karim@example.com · 06 12 34 56 78' }.
import { provide, ref, toRef } from 'vue'
import { CLE_LISTE_LIGNES } from '../../outils/profil'

const props = withDefaults(defineProps<{ resumes?: Record<string, string> }>(), { resumes: () => ({}) })
const ouvertes = ref(new Set<string>())

function basculer(cle: string) {
  const s = new Set(ouvertes.value)
  if (s.has(cle)) s.delete(cle)
  else s.add(cle)
  ouvertes.value = s
}
/** Ouvre une ligne depuis ailleurs, ex. une bulle de métier → « Mes métiers » */
function ouvrir(cle: string) {
  ouvertes.value = new Set(ouvertes.value).add(cle)
}
defineExpose({ ouvrir })
provide(CLE_LISTE_LIGNES, { ouvertes, resumes: toRef(props, 'resumes'), basculer })
</script>

<template>
  <div class="flex flex-col divide-y divide-bord">
    <slot />
  </div>
</template>
