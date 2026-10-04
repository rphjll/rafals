<script setup lang="ts">
// Un prestataire dans les résultats de recherche (.doc/ihm/RM-TROUVER-IHM.md) ; un clic ouvre sa page publique.
// Jamais son téléphone, son mail ni la rue de son local (RM-RECHERCHE).
import { type CarteResultat, aPartirDe, noteLisible, pluriel } from '../../outils/recherche'
import AvatarPrestataire from '../prestataire/AvatarPrestataire.vue'
import AppBadge from '../ui/AppBadge.vue'

defineProps<{ resultat: CarteResultat; metier: string }>()
</script>

<template>
  <RouterLink
    :to="`/prestataires/${resultat.prestataire_id}`"
    class="grid grid-cols-[auto_1fr] items-center gap-x-4 gap-y-3 rounded-rafals border border-bord bg-surface p-4 hover:border-primaire hover:bg-primaire-doux sm:grid-cols-[auto_1fr_auto] sm:p-5"
  >
    <AvatarPrestataire :id="resultat.prestataire_id" :nom="resultat.nom_affiche" :a-une-photo="resultat.a_une_photo" />
    <div class="flex min-w-0 flex-col gap-1.5">
      <div class="flex flex-wrap items-center gap-x-3 gap-y-1">
        <h3 class="text-[19px] font-bold">{{ resultat.nom_affiche }}</h3>
        <AppBadge v-if="resultat.nouveau" etat="attente">Nouveau sur rafals</AppBadge>
        <span v-else class="tabular-nums">
          <b class="text-accent">★ {{ noteLisible(resultat.note ?? 0) }}</b>
          <span class="text-texte-doux"> ({{ resultat.nombre_avis }} avis)</span>
        </span>
      </div>
      <p class="text-texte-doux">
        {{ resultat.principal ? metier : `aussi ${metier.toLowerCase()}` }} · {{ resultat.ville }} · à {{ resultat.distance_km }} km
      </p>
      <div v-if="resultat.vient_chez_vous || resultat.carte_possible" class="flex flex-wrap gap-1.5">
        <AppBadge v-if="resultat.vient_chez_vous" etat="ok">vient chez vous</AppBadge>
        <AppBadge v-if="resultat.carte_possible">carte acceptée</AppBadge>
      </div>
    </div>
    <div class="col-start-2 flex flex-col text-texte-doux sm:col-start-3 sm:items-end sm:text-right">
      <b class="font-titre text-[22px] leading-tight text-primaire tabular-nums">{{ aPartirDe(resultat) }}</b>
      <span>{{ pluriel(resultat.nombre_annonces, 'annonce') }} · voir la fiche ›</span>
    </div>
  </RouterLink>
</template>
