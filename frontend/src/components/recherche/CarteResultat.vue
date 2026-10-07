<script setup lang="ts">
// Un prestataire dans « Trouver un prestataire » (.doc/ihm/RM-TROUVER-IHM.md) : rangée d'un service, [Voir tout] ou
// résultats d'une recherche. Un clic ouvre sa page publique. Jamais son téléphone, son mail ni la rue de son local (RM-RECHERCHE).
import { type CarteResultat, adressePhotoTravail, noteLisible } from '../../outils/recherche'
import AvatarPrestataire from '../prestataire/AvatarPrestataire.vue'
import AppBadge from '../ui/AppBadge.vue'

defineProps<{ resultat: CarteResultat }>()
</script>

<template>
  <RouterLink
    :to="`/prestataires/${resultat.prestataire_id}`"
    class="carte relative flex h-full min-w-0 flex-col overflow-hidden hover:ring-2 hover:ring-primaire"
  >
    <span
      class="absolute top-0 right-0 rounded-bl-[14px] px-3 py-1 text-[12.5px] font-extrabold"
      :class="resultat.siret_verifie ? 'bg-ok-doux text-ok' : 'bg-fond text-texte-doux'"
    >
      {{ resultat.siret_verifie ? 'SIRET vérifié' : 'Particulier' }}
    </span>
    <span class="flex items-center gap-3 px-4 pt-8 pb-3">
      <AvatarPrestataire :id="resultat.prestataire_id" :nom="resultat.nom_affiche" :a-une-photo="resultat.a_une_photo" />
      <span class="flex min-w-0 flex-col leading-snug">
        <b class="text-[17px] font-black break-words">{{ resultat.nom_affiche }}</b>
        <span class="text-[13.5px] font-extrabold">{{ resultat.principal ? resultat.metier : `aussi ${resultat.metier.toLowerCase()}` }}</span>
        <span class="text-[13.5px] text-texte-doux">{{ resultat.ville }} · à {{ resultat.distance_km }} km</span>
      </span>
    </span>
    <!-- Les 2 premières photos de son travail, côte à côte (une seule : toute la largeur) -->
    <span v-if="resultat.photos.length" class="grid h-28 gap-[3px]" :class="resultat.photos.length > 1 ? 'grid-cols-2' : ''">
      <img
        v-for="rang in resultat.photos"
        :key="rang"
        :src="adressePhotoTravail(resultat.prestataire_id, rang)"
        alt=""
        loading="lazy"
        class="size-full min-h-0 object-cover"
      />
    </span>
    <span v-else class="bg-fond px-4 py-2.5 text-center text-[12.5px] font-bold text-texte-doux">Pas encore de photos</span>
    <span class="mt-auto flex items-center px-4 pt-3 pb-3.5">
      <AppBadge v-if="resultat.nouveau" etat="attente">Nouveau sur rafals</AppBadge>
      <span v-else class="tabular-nums">
        <b class="text-accent">★ {{ noteLisible(resultat.note ?? 0) }}/5</b>
        <span class="text-[13.5px] text-texte-doux"> ({{ resultat.nombre_avis }} avis)</span>
      </span>
    </span>
  </RouterLink>
</template>
