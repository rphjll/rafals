<script setup lang="ts">
// Fenêtre « Réserver ce rendez-vous ? » (.doc/ihm/RM-ANNONCE-IHM.md ; RM-RENDEZ-VOUS.md) : récapitulatif, lieu
// (si « chez vous ou chez le prestataire »), adresse du client si besoin, paiement, puis « Réserver mardi 13/10 à 10 h 45 »,
// ou par carte « Payer 50 € et réserver » → la page de paiement de Stripe (lot 5.2, RM-PAIEMENTS.md).
import { computed, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { aParis, heure, jourCourt, jourLisible } from '../../outils/agenda'
import { type AnnoncePublique, euros } from '../../outils/annonces'
import { type RendezVousVisible, plage } from '../../outils/rendez_vous'
import CarteAdresse from '../CarteAdresse.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChoix from '../ui/AppChoix.vue'
import AppFenetre from '../ui/AppFenetre.vue'

const props = defineProps<{ annonce: AnnoncePublique; debut: string | null; heures: number | null }>()
const emit = defineEmits<{ fermer: []; reserve: [rdv: RendezVousVisible] }>()

const lieu = ref<'chez_client' | 'chez_moi'>('chez_client')
const paiement = ref<'especes' | 'carte'>(props.annonce.modes_de_paiement[0] ?? 'especes')
const aUneAdresse = ref(false)
const erreur = ref('')
const envoiEnCours = ref(false)

watch(
  () => props.debut,
  () => {
    erreur.value = ''
    lieu.value = props.annonce.lieu === 'chez_moi' ? 'chez_moi' : 'chez_client'
    paiement.value = props.annonce.modes_de_paiement[0] ?? 'especes'
  },
)

const minutes = computed(() =>
  props.annonce.forme_prix === 'heure' ? (props.heures ?? props.annonce.heures_min ?? 1) * 60 : (props.annonce.duree_minutes ?? 0),
)
const fin = computed(() => (props.debut ? new Date(new Date(props.debut).getTime() + minutes.value * 60000).toISOString() : ''))
const montantTotal = computed(() => {
  const a = props.annonce
  if (a.prix_centimes === null) return 0
  return a.forme_prix === 'heure' ? a.prix_centimes * (props.heures ?? a.heures_min ?? 1) : a.prix_centimes
})
const prix = computed(() => {
  const a = props.annonce
  if (a.prix_centimes === null) return ''
  return a.forme_prix === 'heure'
    ? `${euros(a.prix_centimes * (props.heures ?? a.heures_min ?? 1))} (${props.heures ?? a.heures_min} h à ${euros(a.prix_centimes)})`
    : euros(a.prix_centimes)
})
const titreBouton = computed(() => {
  if (paiement.value === 'carte') return `Payer ${euros(montantTotal.value)} et réserver`
  if (!props.debut) return 'Réserver'
  const m = aParis(props.debut)
  return `Réserver ${jourLisible(m.jour).split(' ')[0]} ${jourCourt(m.jour).slice(0, 5)} à ${heure(m.heure)}`
})
const besoinAdresse = computed(() => lieu.value === 'chez_client' && !aUneAdresse.value)

async function reserver() {
  if (!props.debut) return
  erreur.value = ''
  envoiEnCours.value = true
  try {
    const rdv = await appelerServeur<RendezVousVisible>('/api/rendez-vous', {
      annonce_id: props.annonce.id,
      debut: props.debut,
      heures: props.annonce.forme_prix === 'heure' ? props.heures : null,
      lieu: props.annonce.lieu === 'les_deux' ? lieu.value : null,
      mode_paiement: paiement.value,
    })
    if (rdv.paiement_adresse) {
      window.location.href = rdv.paiement_adresse // la page de paiement de Stripe ; retour sur « Mes rendez-vous »
      return
    }
    emit('reserve', rdv)
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Cet horaire vient d'être pris… »
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppFenetre :ouverte="debut !== null" titre="Réserver ce rendez-vous ?" @fermer="emit('fermer')">
    <div v-if="debut" class="flex flex-col gap-3 text-texte">
      <dl class="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-[14.5px]">
        <dt class="text-texte-doux">Service</dt>
        <dd class="font-medium">{{ annonce.titre }}, avec {{ annonce.prestataire.nom_affiche }}</dd>
        <dt class="text-texte-doux">Quand</dt>
        <dd class="font-medium">{{ plage({ debut, fin }) }}</dd>
        <dt class="text-texte-doux">Prix</dt>
        <dd class="font-medium">{{ prix }}</dd>
      </dl>
      <AppChoix
        v-if="annonce.lieu === 'les_deux'"
        v-model="lieu"
        etiquette="Où ?"
        obligatoire
        :options="[
          { valeur: 'chez_client', texte: 'Chez moi' },
          { valeur: 'chez_moi', texte: `Chez ${annonce.prestataire.nom_affiche}`, detail: annonce.ville },
        ]"
      />
      <p v-else-if="annonce.lieu === 'chez_moi'" class="text-[14px] text-texte-doux">
        Chez {{ annonce.prestataire.nom_affiche }}, à {{ annonce.ville }} : l'adresse exacte vous sera donnée dès la confirmation.
      </p>
      <CarteAdresse
        v-if="lieu === 'chez_client'"
        titre="Votre adresse"
        chemin="/api/moi/adresse"
        texte-vide="Le prestataire vient chez vous : indiquez votre adresse (elle sera gardée pour les prochaines fois)."
        texte-ajouter="Ajouter mon adresse"
        texte-effacer="Effacer"
        @change="(a) => (aUneAdresse = a !== null)"
      />
      <AppChoix
        v-model="paiement"
        etiquette="Paiement"
        obligatoire
        :options="[
          { valeur: 'especes', texte: 'Espèces, le jour même', raisonVerrou: annonce.modes_de_paiement.includes('especes') ? undefined : `${annonce.prestataire.nom_affiche} se fait payer par carte pour ce service.` },
          { valeur: 'carte', texte: 'Carte, maintenant', raisonVerrou: annonce.modes_de_paiement.includes('carte') ? undefined : `${annonce.prestataire.nom_affiche} se fait payer en espèces pour ce service.` },
        ]"
      />
      <AppAlerte v-if="paiement === 'carte'" etat="neutre">
        Vous payez {{ euros(montantTotal) }} maintenant sur la page sécurisée de Stripe (30 minutes pour payer). Remboursé en
        entier si {{ annonce.prestataire.nom_affiche }} refuse ou annule ; si vous annulez à temps, remboursé moins les frais
        de paiement (environ 1 €).
      </AppAlerte>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton
        v-if="besoinAdresse"
        variante="verrouille"
        raison-verrou="Ajoutez d'abord votre adresse, juste au-dessus."
      >
        {{ titreBouton }}
      </AppBouton>
      <AppBouton v-else :occupe="envoiEnCours" @click="reserver">{{ titreBouton }}</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
