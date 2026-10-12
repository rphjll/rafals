<script setup lang="ts">
// Mes demandes (.doc/ihm/RM-DEMANDES-IHM.md ; RM-DEMANDES.md) : les demandes que j'ai publiées, avec leur état ;
// modifier (tant que personne n'a répondu), fermer, prolonger, rouvrir. On publie depuis l'accueil.
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import CarteDemande from '../components/demandes/CarteDemande.vue'
import FenetreModifierDemande from '../components/demandes/FenetreModifierDemande.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppFenetre from '../components/ui/AppFenetre.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { formaterDateHeure } from '../outils/dates'
import { badgeDemande, type MaDemande } from '../outils/demandes'

const routeur = useRouter()
const { compte, chargementFait } = useCompte()
const { afficherMessage } = useMessage()
const demandes = ref<MaDemande[] | null>(null)
const erreur = ref('')
const aFermer = ref<MaDemande | null>(null)
const aModifier = ref<MaDemande | null>(null)

async function charger() {
  if (!compte.value) return
  try {
    demandes.value = await appelerServeur<MaDemande[]>('/api/moi/demandes')
    erreur.value = ''
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
watch(compte, charger)

async function agir(demande: MaDemande, action: 'fermer' | 'prolonger' | 'rouvrir', reussite: string) {
  try {
    await appelerServeur(`/api/demandes/${demande.id}/${action}`, {})
    afficherMessage(reussite)
    await charger()
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur') // ex. « Le rendez-vous de cette demande est toujours prévu… »
  }
  aFermer.value = null
}
</script>

<template>
  <div class="mx-auto flex max-w-[760px] flex-col gap-5">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-[clamp(28px,4.5vw,40px)] font-black">Mes demandes</h1>
      <AppBouton variante="accent" @click="routeur.push('/')">Publier une demande</AppBouton>
    </div>
    <template v-if="chargementFait && !compte">
      <AppAlerte etat="neutre">Connectez-vous pour voir vos demandes.</AppAlerte>
      <div><AppBouton @click="routeur.push('/connexion')">Se connecter</AppBouton></div>
    </template>
    <AppAlerte v-else-if="erreur">{{ erreur }}</AppAlerte>
    <div v-else-if="demandes?.length" class="flex flex-col gap-4">
      <CarteDemande v-for="demande in demandes" :key="demande.id" :demande="demande">
        <AppBadge :etat="badgeDemande(demande).etat">{{ badgeDemande(demande).texte }}</AppBadge>
        <template v-if="demande.statut === 'ouverte'">
          <span class="self-center text-[13px] text-texte-doux">Ouverte jusqu'au {{ formaterDateHeure(demande.expire_le) }}.</span>
          <AppBouton v-if="!demande.nombre_reponses" variante="secondaire" @click="aModifier = demande">Modifier…</AppBouton>
          <AppBouton
            v-else
            variante="verrouille"
            raison-verrou="Un prestataire a déjà répondu : pour changer cette demande, fermez-la et publiez-en une autre."
          >
            Modifier
          </AppBouton>
          <AppBouton variante="secondaire" @click="agir(demande, 'prolonger', 'Demande prolongée de 30 jours.')">Prolonger de 30 jours</AppBouton>
          <AppBouton variante="danger" @click="aFermer = demande">Fermer ma demande…</AppBouton>
        </template>
        <AppBouton v-else-if="demande.statut === 'expiree'" variante="secondaire" @click="agir(demande, 'prolonger', 'Demande rouverte pour 30 jours.')">
          Rouvrir pour 30 jours
        </AppBouton>
        <template v-else-if="demande.statut === 'pourvue'">
          <AppBouton variante="secondaire" @click="routeur.push('/rendez-vous')">Voir le rendez-vous</AppBouton>
          <AppBouton variante="secondaire" @click="agir(demande, 'rouvrir', 'Demande rouverte pour 30 jours.')">Rouvrir (rendez-vous annulé)</AppBouton>
        </template>
      </CarteDemande>
    </div>
    <p v-else-if="demandes" class="rounded-carte border-2 border-dashed border-bord p-5 text-texte-doux">
      Aucune demande pour l'instant. Publiez-en une depuis l'accueil : les prestataires proches vous répondent.
    </p>

    <FenetreModifierDemande :demande="aModifier" @fermer="aModifier = null" @modifiee="(aModifier = null), charger()" />
    <AppFenetre :ouverte="aFermer !== null" :titre="`Fermer « ${aFermer?.titre} » ?`" @fermer="aFermer = null">
      Les prestataires ne la verront plus et ne pourront plus y répondre. Elle reste dans « Mes demandes ».
      <template #pied>
        <AppBouton variante="danger" @click="aFermer && agir(aFermer, 'fermer', 'Demande fermée.')">Fermer ma demande</AppBouton>
        <AppBouton variante="secondaire" @click="aFermer = null">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
