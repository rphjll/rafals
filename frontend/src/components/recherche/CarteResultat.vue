<script setup lang="ts">
// Un prestataire dans les résultats de recherche (.doc/ihm/RM-TROUVER-IHM.md) : une petite carte en hauteur, la photo
// de profil en haut ; un clic ouvre sa page publique. Jamais son téléphone, son mail ni la rue de son local (RM-RECHERCHE).
import { type CarteResultat, aPartirDe, noteLisible } from '../../outils/recherche'
import AvatarPrestataire from '../prestataire/AvatarPrestataire.vue'
import AppBadge from '../ui/AppBadge.vue'

defineProps<{ resultat: CarteResultat; metier: string }>()
</script>

<template>
  <RouterLink
    :to="`/prestataires/${resultat.prestataire_id}`"
    class="carte flex h-full min-w-0 flex-col items-center gap-2 px-3 py-5 text-center hover:ring-2 hover:ring-primaire"
  >
    <AvatarPrestataire :id="resultat.prestataire_id" :nom="resultat.nom_affiche" :a-une-photo="resultat.a_une_photo" taille="moyenne" />
    <h3 class="text-[17px] leading-tight font-bold break-words">{{ resultat.nom_affiche }}</h3>
    <AppBadge v-if="resultat.nouveau" etat="attente">Nouveau sur rafals</AppBadge>
    <span v-else class="tabular-nums">
      <b class="text-accent">★ {{ noteLisible(resultat.note ?? 0) }}</b>
      <span class="text-[13.5px] text-texte-doux"> · {{ resultat.nombre_avis }} avis</span>
    </span>
    <p class="text-[13.5px] text-texte-doux">
      {{ resultat.principal ? metier : `aussi ${metier.toLowerCase()}` }}<br />{{ resultat.ville }} · à {{ resultat.distance_km }} km
    </p>
    <div v-if="resultat.vient_chez_vous || resultat.carte_possible" class="flex flex-wrap justify-center gap-1.5">
      <AppBadge v-if="resultat.vient_chez_vous" etat="ok">vient chez vous</AppBadge>
      <AppBadge v-if="resultat.carte_possible">carte acceptée</AppBadge>
    </div>
    <b class="mt-auto pt-1 text-primaire tabular-nums">{{ aPartirDe(resultat) }}</b>
  </RouterLink>
</template>
