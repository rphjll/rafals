<script setup lang="ts">
// Mes abonnements (.doc/ihm/RM-ABONNEMENTS-IHM.md ; RM-ABONNEMENTS.md), ouverte depuis la liste sous le prénom :
// les prestataires suivis, le plus récent d'abord. [Rendre muet] coupe toutes les notifications de ce prestataire
// (les 3 cases, elles, sont dans « Paramètres » pour tous les abonnements : demande de Raphael du 21/10/2026) ;
// [Se désabonner] retire la carte.
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../api'
import AvatarPrestataire from '../components/prestataire/AvatarPrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppIcone from '../components/ui/AppIcone.vue'
import { useMessage } from '../composables/useMessage'
import { type AbonnementVisible, cheminAbonnement } from '../outils/abonnements'
import { noteLisible } from '../outils/recherche'

const { afficherMessage } = useMessage()
const abonnements = ref<AbonnementVisible[] | null>(null)
const erreur = ref('')

onMounted(async () => {
  try {
    abonnements.value = await appelerServeur<AbonnementVisible[]>('/api/moi/abonnements')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})

// Effet immédiat à l'écran ; en cas d'échec, le bouton revient comme avant
async function changerMuet(a: AbonnementVisible) {
  const voulu = !a.muet
  a.muet = voulu
  try {
    a.muet = (await appelerServeur<{ muet: boolean }>(`/api/moi/abonnements/${a.prestataire_id}/muet`, { muet: voulu })).muet
    afficherMessage(voulu ? `${a.nom_affiche} est en muet : plus aucune notification.` : `Notifications de ${a.nom_affiche} réactivées.`)
  } catch (e) {
    a.muet = !voulu
    afficherMessage(messageErreur(e), 'erreur')
  }
}

async function desabonner(a: AbonnementVisible) {
  try {
    await appelerServeur(cheminAbonnement(a.prestataire_id, true), {})
    abonnements.value = (abonnements.value ?? []).filter((x) => x.prestataire_id !== a.prestataire_id)
    afficherMessage(`Vous ne suivez plus ${a.nom_affiche}`)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <div class="page">
    <div class="tete">
      <h1>Mes abonnements</h1>
      <p>Les prestataires que vous suivez. Vous êtes prévenu quand ils ont un créneau libre.</p>
    </div>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div v-if="abonnements?.length" class="liste">
      <div v-for="a in abonnements" :key="a.prestataire_id" class="ligne" :class="a.visible ? '' : 'opacity-70'">
        <AvatarPrestataire :id="a.prestataire_id" :nom="a.nom_affiche" :a-une-photo="a.a_une_photo" taille="mini" />
        <div class="txt">
          <b>{{ a.nom_affiche }}</b>
          <span>
            {{ a.metier }} · {{ a.ville }}<template v-if="a.nombre_avis"> · ★ {{ noteLisible(a.note ?? 0) }}</template><template v-if="!a.visible"> · profil en pause</template><template v-if="a.muet"> · muet</template>
          </span>
        </div>
        <span class="fin">
          <button type="button" class="btn btn-2 btn-petit" :aria-pressed="a.muet" @click="changerMuet(a)">{{ a.muet ? 'Réactiver' : 'Rendre muet' }}</button>
          <button type="button" class="btn btn-2 btn-petit cache-tel" @click="desabonner(a)">Se désabonner</button>
          <RouterLink v-if="a.visible" class="btn btn-2 btn-petit" :to="`/prestataires/${a.prestataire_id}`" :aria-label="`Voir ${a.nom_affiche}`"><AppIcone nom="suite" /></RouterLink>
        </span>
      </div>
    </div>
    <div v-else-if="abonnements" class="carte vide">
      <h3>Vous ne suivez personne</h3>
      <p style="margin-top: 6px">Sur la page d’un prestataire, touchez « S’abonner ».</p>
      <RouterLink class="btn btn-1" to="/trouver" style="margin-top: 14px">Trouver un prestataire</RouterLink>
    </div>
    <p class="doux petit">Ce que vous recevez se règle dans <RouterLink to="/parametres#abonnements" class="lien">Paramètres</RouterLink>.</p>
  </div>
</template>
