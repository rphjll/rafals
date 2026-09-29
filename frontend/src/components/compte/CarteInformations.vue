<script setup lang="ts">
// Mon compte › Mes informations (.doc/ihm/RM-COMPTE-IHM.md) : lecture, puis modification de prénom, nom, téléphone.
import { ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte, type CompteVisible } from '../../composables/useCompte'
import { useMessage } from '../../composables/useMessage'
import { age, formaterDate } from '../../outils/dates'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppSection from '../ui/AppSection.vue'

const props = defineProps<{ compte: CompteVisible }>()
const { chargerCompte, renvoyerLienVerification } = useCompte()
const { afficherMessage } = useMessage()

const enModification = ref(false)
const prenom = ref('')
const nom = ref('')
const telephone = ref('')
const erreur = ref('')
const envoiEnCours = ref(false)

function modifier() {
  prenom.value = props.compte.prenom
  nom.value = props.compte.nom
  telephone.value = props.compte.telephone ?? ''
  erreur.value = ''
  enModification.value = true
}

async function enregistrer() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    const reponse = await appelerServeur<{ message: string }>('/api/moi/informations', {
      prenom: prenom.value,
      nom: nom.value,
      telephone: telephone.value,
    })
    await chargerCompte()
    enModification.value = false
    afficherMessage(reponse.message)
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}

async function renvoyerLien() {
  try {
    afficherMessage(await renvoyerLienVerification(props.compte.email))
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <AppSection v-if="enModification" titre="Modifier mes informations">
    <form class="flex flex-col gap-3.5" @submit.prevent="enregistrer">
      <div class="grid gap-3 sm:grid-cols-2">
        <AppChamp v-model="prenom" etiquette="Prénom" obligatoire autocomplete="given-name" />
        <AppChamp v-model="nom" etiquette="Nom" obligatoire autocomplete="family-name" />
      </div>
      <AppChamp v-model="telephone" etiquette="Téléphone" obligatoire type="tel" autocomplete="tel" inputmode="tel" />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap gap-2">
        <AppBouton type="submit" :occupe="envoiEnCours">Enregistrer</AppBouton>
        <AppBouton variante="secondaire" @click="enModification = false">Annuler</AppBouton>
      </div>
    </form>
  </AppSection>

  <AppSection v-else titre="Mes informations">
    <template #action>
      <AppBouton variante="secondaire" @click="modifier">Modifier</AppBouton>
    </template>
    <dl class="grid grid-cols-[auto_1fr] gap-x-[18px] gap-y-2 text-[14.5px]">
      <dt class="text-texte-doux">Nom</dt>
      <dd class="font-medium">{{ compte.prenom }} {{ compte.nom }}</dd>
      <dt class="text-texte-doux">Adresse mail</dt>
      <dd class="flex flex-wrap items-center gap-2 font-medium">
        {{ compte.email }}
        <AppBadge v-if="compte.email_verifie" etat="ok">vérifiée</AppBadge>
        <template v-else>
          <AppBadge etat="attente">pas encore vérifiée</AppBadge>
          <AppBouton variante="secondaire" @click="renvoyerLien">Renvoyer le lien</AppBouton>
        </template>
      </dd>
      <dt class="text-texte-doux">Téléphone</dt>
      <dd class="font-medium">{{ compte.telephone }}</dd>
      <template v-if="compte.date_naissance">
        <dt class="text-texte-doux">Date de naissance</dt>
        <dd class="font-medium">{{ formaterDate(compte.date_naissance) }} ({{ age(compte.date_naissance) }} ans)</dd>
      </template>
    </dl>
    <p class="text-[13px] text-texte-doux">Changer d'adresse mail : bientôt disponible.</p>
  </AppSection>
</template>
