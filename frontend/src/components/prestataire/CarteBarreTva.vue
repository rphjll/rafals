<script setup lang="ts">
// Mon activité › « Encaissé en 2026 » et la barre de la TVA (.doc/ihm/RM-MON-ACTIVITE-IHM.md ; RM-MON-ACTIVITE.md).
// La barre compte ce qui est passé par rafals + ce que le prestataire a encaissé ailleurs. Barre pleine : la TVA
// s'active toute seule (demande de Raphael du 17/10/2026) ; il n'y a plus de case « Je facture la TVA ».
import { computed, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import type { ChiffresPrestataire, EncaisseAilleurs } from '../../outils/activite'
import { jourCourt } from '../../outils/agenda'
import { aujourdhuiIso } from '../../outils/dates'
import { montant } from '../../outils/paiements'
import { versCentimes } from '../../outils/prix'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppIcone from '../ui/AppIcone.vue'

const props = defineProps<{ chiffres: ChiffresPrestataire }>()
const emit = defineEmits<{ maj: [] }>()
const { afficherMessage } = useMessage()

const total = computed(() => props.chiffres.encaisse_annee_centimes + props.chiffres.ailleurs_annee_centimes)
// La barre : seulement tant que la TVA n'est pas activée
const barre = computed(() => {
  const seuil = props.chiffres.seuil_tva_centimes
  if (seuil === null || props.chiffres.reste_avant_seuil_centimes === null) return null
  return { seuil: montant(seuil), reste: montant(props.chiffres.reste_avant_seuil_centimes), pourcent: Math.min(100, Math.round((total.value / seuil) * 100)) }
})

// Les montants encaissés ailleurs cette année, relus avec les chiffres
const ailleurs = ref<EncaisseAilleurs[]>([])
async function charger() {
  try {
    ailleurs.value = await appelerServeur<EncaisseAilleurs[]>('/api/moi/prestataire/encaisse-ailleurs')
  } catch {
    ailleurs.value = [] // serveur injoignable : la barre suffit
  }
}
watch(() => props.chiffres, charger, { immediate: true })

// [Ajouter ce que j'ai encaissé ailleurs]
const aujourdhui = aujourdhuiIso()
const fenetre = ref(false)
const somme = ref('')
const jour = ref(aujourdhui)
const erreur = ref('')
const envoiEnCours = ref(false)

function ouvrir() {
  somme.value = ''
  jour.value = aujourdhui
  erreur.value = ''
  fenetre.value = true
}

async function ajouter() {
  const centimes = versCentimes(somme.value)
  if (centimes === null || centimes <= 0) {
    erreur.value = 'Indiquez un montant plus grand que 0 €, par exemple 2000 ou 45,50.'
    return
  }
  erreur.value = ''
  envoiEnCours.value = true
  try {
    const ajout = await appelerServeur<{ tva_activee: boolean }>('/api/moi/prestataire/encaisse-ailleurs', {
      montant_centimes: centimes,
      encaisse_le: jour.value,
    })
    fenetre.value = false
    emit('maj')
    afficherMessage(ajout.tva_activee ? 'Barre pleine : votre TVA est activée pour vos prochains devis et factures.' : `${montant(centimes)} ajoutés.`)
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}

async function retirer(ligne: EncaisseAilleurs) {
  try {
    // Le serveur dit si la TVA s'est désactivée (erreur de saisie retirée, décision de Raphael du 09/11/2026)
    const reponse = await appelerServeur<{ message: string }>(`/api/moi/prestataire/encaisse-ailleurs/${ligne.id}/retirer`, {})
    afficherMessage(reponse.message)
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <!-- Comme la carte « Encaissé en 2026 » de la grande maquette -->
  <section class="carte tva p-[18px]">
    <div class="tva-haut">
      <h2>Encaissé en {{ chiffres.annee }}</h2>
      <b class="tva-somme">{{ montant(total) }}</b>
    </div>
    <p v-if="chiffres.ailleurs_annee_centimes" class="doux petit">
      Dont {{ montant(chiffres.encaisse_annee_centimes) }} sur rafals et {{ montant(chiffres.ailleurs_annee_centimes) }} ailleurs.
    </p>
    <template v-if="barre">
      <div class="tva-barre" role="img" :aria-label="`${barre.pourcent} % du seuil de TVA`"><span :style="{ width: `${barre.pourcent}%` }" /></div>
      <p class="petit">Il vous reste <b>{{ barre.reste }}</b> avant le seuil de TVA ({{ barre.seuil }}). Barre pleine : la TVA s’active toute seule.</p>
      <button type="button" class="btn btn-2 btn-petit" style="align-self: flex-start" @click="ouvrir"><AppIcone nom="plus" />Ajouter ce que j’ai encaissé ailleurs</button>
    </template>
    <p v-else class="tva-ok"><AppIcone nom="ok" />TVA activée : vos devis et factures indiquent la TVA.</p>
    <div v-if="ailleurs.length" class="tva-liste">
      <div v-for="ligne in ailleurs" :key="ligne.id" class="tva-ligne">
        <span>{{ montant(ligne.montant_centimes) }} encaissés ailleurs le {{ jourCourt(ligne.encaisse_le) }}</span>
        <button type="button" class="btn btn-2 btn-petit" @click="retirer(ligne)">Retirer</button>
      </div>
    </div>

    <AppFenetre :ouverte="fenetre" titre="Encaissé ailleurs" @fermer="fenetre = false">
      <div class="flex flex-col gap-3 text-texte">
        <p class="text-[13.5px] text-texte-doux">
          L'argent gagné sans passer par rafals (anciens clients, espèces…). Il s'ajoute à la barre de {{ chiffres.annee }}.
        </p>
        <AppChamp v-model="somme" etiquette="Montant en euros" obligatoire inputmode="decimal" placeholder="2000" />
        <AppChamp v-model="jour" type="date" etiquette="Encaissé le" obligatoire :max="aujourdhui" />
        <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      </div>
      <template #pied>
        <AppBouton :occupe="envoiEnCours" @click="ajouter">Ajouter</AppBouton>
        <AppBouton variante="secondaire" @click="fenetre = false">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </section>
</template>
