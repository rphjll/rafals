<script setup lang="ts">
// Mon compte › Mon adresse (.doc/ihm/RM-COMPTE-IHM.md ; RM-CLIENTS.md) : une seule adresse, ajoutée, modifiée ou effacée.
// Le code postal vient de la ville choisie ; une liste apparaît seulement si la ville en a plusieurs (ex. Marseille).
import { computed, onMounted, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import type { CommuneVisible } from '../../outils/prestataires'
import AppChoixCommune from '../AppChoixCommune.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppSection from '../ui/AppSection.vue'
import AppSelection from '../ui/AppSelection.vue'

interface Adresse {
  ligne: string
  complement: string | null
  code_postal: string
  commune: CommuneVisible
}

const { afficherMessage } = useMessage()
const adresse = ref<Adresse | null>(null)
const chargee = ref(false)
const enModification = ref(false)
const ligne = ref('')
const complement = ref('')
const commune = ref<CommuneVisible | null>(null)
const codePostal = ref('')
const erreur = ref('')
const envoiEnCours = ref(false)

onMounted(async () => {
  try {
    adresse.value = await appelerServeur<Adresse | null>('/api/moi/adresse')
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    chargee.value = true
  }
})

const codesPostaux = computed(() => commune.value?.codes_postaux ?? [])
// Ville changée : on garde le code postal s'il est à elle, sinon on prend son seul code, sinon on laisse choisir
watch(commune, (nouvelle) => {
  const codes = nouvelle?.codes_postaux ?? []
  if (!codes.includes(codePostal.value)) codePostal.value = codes.length === 1 ? (codes[0] ?? '') : ''
})
// La liste déroulante travaille avec des numéros : 0 = premier code postal de la ville
const rangCodePostal = computed({
  get: () => (codesPostaux.value.includes(codePostal.value) ? codesPostaux.value.indexOf(codePostal.value) : null),
  set: (rang) => (codePostal.value = rang === null ? '' : (codesPostaux.value[rang] ?? '')),
})

function ouvrir() {
  ligne.value = adresse.value?.ligne ?? ''
  complement.value = adresse.value?.complement ?? ''
  commune.value = adresse.value?.commune ?? null
  codePostal.value = adresse.value?.code_postal ?? ''
  erreur.value = ''
  enModification.value = true
}

async function enregistrer() {
  erreur.value = ''
  if (!commune.value) {
    erreur.value = 'Choisissez la ville.'
    return
  }
  if (!codePostal.value) {
    erreur.value = 'Choisissez le code postal.'
    return
  }
  envoiEnCours.value = true
  try {
    adresse.value = await appelerServeur<Adresse>('/api/moi/adresse', {
      ligne: ligne.value,
      complement: complement.value.trim() || null,
      commune_id: commune.value.id,
      code_postal: codePostal.value,
    })
    enModification.value = false
    afficherMessage('Adresse enregistrée.')
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}

async function effacer() {
  try {
    afficherMessage((await appelerServeur<{ message: string }>('/api/moi/adresse/effacer', {})).message)
    adresse.value = null
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <AppSection v-if="chargee" titre="Mon adresse">
    <form v-if="enModification" class="flex flex-col gap-3.5" @submit.prevent="enregistrer">
      <AppChamp v-model="ligne" etiquette="Numéro et rue" obligatoire autocomplete="address-line1" placeholder="ex. 8 allée des Pins" />
      <AppChamp v-model="complement" etiquette="Complément" autocomplete="address-line2" placeholder="Bâtiment, étage, code…" />
      <AppChoixCommune v-model="commune" obligatoire />
      <AppSelection
        v-if="codesPostaux.length > 1"
        v-model="rangCodePostal"
        etiquette="Code postal"
        obligatoire
        :options="codesPostaux.map((code, rang) => ({ valeur: rang, texte: code }))"
      />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap gap-2">
        <AppBouton type="submit" :occupe="envoiEnCours">Enregistrer</AppBouton>
        <AppBouton variante="secondaire" @click="enModification = false">Annuler</AppBouton>
      </div>
    </form>

    <template v-else-if="adresse">
      <p class="font-medium">
        {{ adresse.ligne }}<br />
        <template v-if="adresse.complement">{{ adresse.complement }}<br /></template>
        {{ adresse.code_postal }} {{ adresse.commune.nom }}
      </p>
      <div class="flex flex-wrap gap-2">
        <AppBouton variante="secondaire" @click="ouvrir">Modifier</AppBouton>
        <AppBouton variante="danger" @click="effacer">Effacer mon adresse</AppBouton>
      </div>
    </template>

    <template v-else>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <p class="text-[13.5px] text-texte-doux">
        Aucune adresse enregistrée : elle vous sera demandée quand vous réserverez un service à domicile.
      </p>
      <div><AppBouton variante="secondaire" @click="ouvrir">Ajouter mon adresse</AppBouton></div>
    </template>
  </AppSection>
</template>
