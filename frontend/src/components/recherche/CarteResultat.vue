<script setup lang="ts">
// Un prestataire dans une liste (accueil « Près de chez vous », « Trouver ») : la carte « presta » de la grande maquette
// (10/11/2026). Toute la carte mène à sa page publique. Jamais son téléphone, son mail ni la rue de son local (RM-RECHERCHE).
// En bas à droite : le prix de l'heure du métier de la carte (« 45 €/h », schema_v35), sinon le nombre d'abonnés.
import { euros } from '../../outils/prix'
import { type CarteResultat, noteLisible } from '../../outils/recherche'
import AvatarPrestataire from '../prestataire/AvatarPrestataire.vue'
import AppIcone from '../ui/AppIcone.vue'

defineProps<{ resultat: CarteResultat }>()
</script>

<template>
  <RouterLink class="presta" :to="`/prestataires/${resultat.prestataire_id}`">
    <div class="haut">
      <AvatarPrestataire :id="resultat.prestataire_id" :nom="resultat.nom_affiche" :a-une-photo="resultat.a_une_photo" taille="mini" />
      <div>
        <b>{{ resultat.nom_affiche }}</b>
        <span class="doux petit">{{ resultat.principal ? resultat.metier : `Aussi ${resultat.metier.toLowerCase()}` }} · {{ resultat.ville }}, {{ resultat.distance_km }} km</span>
      </div>
    </div>
    <div class="bas">
      <span v-if="resultat.nouveau" class="puce p-att">Nouveau sur rafals</span>
      <span v-else class="etoile">★ {{ noteLisible(resultat.note ?? 0) }} <span class="doux petit">({{ resultat.nombre_avis }} avis)</span></span>
      <span v-if="resultat.prix_centimes" class="prix">{{ euros(resultat.prix_centimes) }}/h</span>
      <span v-else-if="resultat.abonnes" class="doux petit">{{ resultat.abonnes }} abonné{{ resultat.abonnes > 1 ? 's' : '' }}</span>
    </div>
    <span v-if="resultat.siret_verifie" class="puce p-ok" style="align-self: flex-start"><AppIcone nom="bouclier" class="size-4" />SIRET vérifié</span>
    <span v-else class="puce p-neutre" style="align-self: flex-start">Sans SIRET</span>
  </RouterLink>
</template>
