<script setup lang="ts">
// Fenêtre « Modifier ma demande » de « Mes demandes » (.doc/ihm/RM-DEMANDES-IHM.md ; RM-DEMANDES.md) : titre,
// description, pour quand, budget. Possible tant qu'aucun prestataire n'a répondu ; le métier, l'adresse et les photos
// ne se changent pas ici (fermer la demande et en publier une autre).
import { computed, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { aujourdhuiIso } from '../../outils/dates'
import { type MaDemande, QUAND } from '../../outils/demandes'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSelection from '../ui/AppSelection.vue'
import AppZoneTexte from '../ui/AppZoneTexte.vue'

const props = defineProps<{ demande: MaDemande | null }>()
const emit = defineEmits<{ fermer: []; modifiee: [] }>()
const { afficherMessage } = useMessage()

const OPTIONS_QUAND = QUAND.map((q, rang) => ({ valeur: rang, texte: q.texte }))
const titre = ref('')
const description = ref('')
const quand = ref<number | null>(0)
const jour = ref('')
const budget = ref('')
const erreur = ref('')
const occupe = ref(false)
const jourPrecis = computed(() => quand.value !== null && QUAND[quand.value].valeur === 'jour_precis')

watch(
  () => props.demande,
  (d) => {
    if (!d) return
    erreur.value = ''
    titre.value = d.titre
    description.value = d.description
    quand.value = QUAND.findIndex((q) => q.valeur === d.quand)
    jour.value = d.jour ?? ''
    budget.value = d.budget_centimes ? String(d.budget_centimes / 100).replace('.', ',') : ''
  },
)

async function enregistrer() {
  const d = props.demande
  if (!d || quand.value === null) return
  erreur.value = ''
  const euros = Number(budget.value.replace(',', '.'))
  if (budget.value.trim() && (!Number.isFinite(euros) || euros <= 0)) {
    erreur.value = 'Le budget est un montant en euros (ex. 40), ou rien.'
    return
  }
  occupe.value = true
  try {
    await appelerServeur(
      `/api/demandes/${d.id}`,
      {
        metier_id: d.metier_id,
        titre: titre.value,
        description: description.value,
        quand: QUAND[quand.value].valeur,
        jour: jourPrecis.value && jour.value ? jour.value : null,
        lieu: d.lieu,
        budget_centimes: budget.value.trim() ? Math.round(euros * 100) : null,
        adresse_ligne: d.adresse_ligne,
        adresse_complement: d.adresse_complement,
        code_postal: d.code_postal,
        latitude: d.latitude,
        longitude: d.longitude,
      },
      'PUT',
    )
    afficherMessage('Demande modifiée.')
    emit('modifiee')
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Un prestataire a déjà répondu : fermez cette demande et publiez-en une autre… »
  } finally {
    occupe.value = false
  }
}
</script>

<template>
  <AppFenetre :ouverte="demande !== null" titre="Modifier ma demande" @fermer="emit('fermer')">
    <div v-if="demande" class="flex flex-col gap-3 text-texte">
      <p class="text-[14px] text-texte-doux">
        {{ demande.metier }} · {{ demande.ville }}. Pour changer le métier, l'adresse ou les photos, fermez cette demande et publiez-en une autre.
      </p>
      <AppChamp v-model="titre" etiquette="Titre" obligatoire maxlength="80" />
      <AppZoneTexte v-model="description" etiquette="Décrivez votre besoin" obligatoire :maximum="1000" aide="Au moins 20 caractères, sans téléphone ni mail." />
      <AppSelection v-model="quand" etiquette="Pour quand ?" :options="OPTIONS_QUAND" obligatoire />
      <AppChamp v-if="jourPrecis" v-model="jour" etiquette="Quel jour ?" type="date" obligatoire :min="aujourdhuiIso()" />
      <AppChamp v-model="budget" etiquette="Budget en euros (facultatif)" inputmode="decimal" placeholder="ex. 40" />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton :occupe="occupe" @click="enregistrer">Enregistrer</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
