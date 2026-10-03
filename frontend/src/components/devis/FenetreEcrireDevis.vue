<script setup lang="ts">
// Fenêtre « Devis pour Marie Dupont » (.doc/ihm/RM-DEVIS-IHM.md ; RM-DEVIS.md) : lignes (désignation, quantité, prix
// à l'unité, taux de TVA si le prestataire la facture), total calculé, jours des travaux, arrhes, validité (30 jours).
import { computed, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { ajouterJours, aParis } from '../../outils/agenda'
import { versCentimes } from '../../outils/annonces'
import { type AvecPaiement, type DemandeVisible, TAUX_TVA, versCentiemes } from '../../outils/devis'
import { montant } from '../../outils/paiements'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSelection from '../ui/AppSelection.vue'

const LIGNES_MAX = 20
const props = defineProps<{ demande: DemandeVisible | null; factureTva: boolean }>()
const emit = defineEmits<{ fermer: []; envoye: [] }>()
const { afficherMessage } = useMessage()

interface LigneSaisie {
  libelle: string
  quantite: string
  prix: string
  tva: number | null
}
const aujourdhui = aParis(new Date().toISOString()).jour
const lignes = ref<LigneSaisie[]>([])
const debut = ref('')
const fin = ref('')
const arrhes = ref('30')
const valable = ref('')
const erreur = ref('')
const envoiEnCours = ref(false)
const nouvelleLigne = (): LigneSaisie => ({ libelle: '', quantite: '1', prix: '', tva: 200 })
watch(
  () => props.demande,
  () => {
    lignes.value = [nouvelleLigne()]
    debut.value = fin.value = ajouterJours(aujourdhui, 7)
    arrhes.value = '30'
    valable.value = ajouterJours(aujourdhui, 30) // « Valable jusqu'au » rempli d'avance (RM-DEVIS), modifiable
    erreur.value = ''
  },
)

// Total calculé comme le serveur : chaque ligne arrondie au centime ; TVA par ligne
const total = computed(() => {
  let ht = 0
  let tva = 0
  for (const l of lignes.value) {
    const q = versCentiemes(l.quantite) ?? 0
    const p = versCentimes(l.prix) ?? 0
    const ligne = Math.round((q * p) / 100)
    ht += ligne
    if (props.factureTva) tva += Math.round((ligne * (l.tva ?? 0)) / 1000)
  }
  const ttc = ht + tva
  const pourcent = Number(arrhes.value) || 0
  return { ht, tva, ttc, arrhes: Math.round((ttc * pourcent) / 100) }
})

async function envoyer() {
  if (!props.demande) return
  erreur.value = ''
  envoiEnCours.value = true
  try {
    await appelerServeur<AvecPaiement>(`/api/moi/prestataire/demandes-devis/${props.demande.id}/devis`, {
      lignes: lignes.value.map((l) => ({
        libelle: l.libelle,
        quantite_centiemes: versCentiemes(l.quantite) ?? 0,
        prix_unitaire_centimes: versCentimes(l.prix) ?? -1,
        tva_pour_mille: props.factureTva ? l.tva : null,
      })),
      arrhes_pourcent: Number(arrhes.value) || 0,
      travaux_debut: debut.value,
      travaux_fin: fin.value,
      valable_jusqu_au: valable.value,
    })
    afficherMessage(`Devis envoyé à ${props.demande.autre.nom}.`)
    emit('envoye')
  } catch (e) {
    erreur.value = messageErreur(e) // ex. « Le 19/10/2026 n'est pas libre dans votre agenda… »
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppFenetre :ouverte="demande !== null" :titre="`Devis pour ${demande?.autre.nom ?? ''}`" @fermer="emit('fermer')">
    <div v-if="demande" class="flex flex-col gap-3 text-texte">
      <p class="text-[14px] text-texte-doux">{{ demande.titre }} · « {{ demande.texte }} »</p>
      <span class="text-[13px] font-semibold">Lignes<span class="text-erreur"> *</span> ({{ LIGNES_MAX }} au plus)</span>
      <div v-for="(ligne, rang) in lignes" :key="rang" class="flex flex-wrap items-end gap-1.5 border-b border-bord pb-2">
        <div class="min-w-[160px] flex-1"><AppChamp v-model="ligne.libelle" etiquette="Désignation" placeholder="ex. Parpaings" /></div>
        <div class="w-[80px]"><AppChamp v-model="ligne.quantite" etiquette="Quantité" inputmode="decimal" /></div>
        <div class="w-[110px]"><AppChamp v-model="ligne.prix" :etiquette="factureTva ? 'Prix unit. HT €' : 'Prix unit. €'" inputmode="decimal" placeholder="3,50" /></div>
        <div v-if="factureTva" class="w-[100px]"><AppSelection v-model="ligne.tva" etiquette="TVA" :options="TAUX_TVA" /></div>
        <AppBouton v-if="lignes.length > 1" variante="danger" :aria-label="`Retirer la ligne ${rang + 1}`" @click="lignes.splice(rang, 1)">×</AppBouton>
      </div>
      <div v-if="lignes.length < LIGNES_MAX">
        <AppBouton variante="secondaire" @click="lignes.push(nouvelleLigne())">+ Ajouter une ligne</AppBouton>
      </div>
      <p class="text-right">
        <template v-if="factureTva">
          <span class="text-[13.5px] text-texte-doux">HT {{ montant(total.ht) }} · TVA {{ montant(total.tva) }} · </span>
          <b>Total TTC : {{ montant(total.ttc) }}</b>
        </template>
        <template v-else>
          <b>Total : {{ montant(total.ttc) }}</b>
          <span class="block text-[13px] text-texte-doux">TVA non applicable, art. 293 B du CGI</span>
        </template>
      </p>
      <div class="grid gap-2 sm:grid-cols-2">
        <AppChamp v-model="debut" etiquette="Travaux du" obligatoire type="date" />
        <AppChamp v-model="fin" etiquette="au" obligatoire type="date" />
        <AppChamp v-model="arrhes" etiquette="Arrhes (%)" obligatoire inputmode="numeric" aide="0 si vous n'en demandez pas." />
        <AppChamp v-model="valable" etiquette="Valable jusqu'au" obligatoire type="date" />
      </div>
      <p class="text-[13.5px] text-texte-doux">
        Arrhes : {{ montant(total.arrhes) }}, payées par carte en acceptant, gardées par vous si le client annule. Seuls
        des jours libres dans votre agenda ; ils seront bloqués quand le client acceptera.
      </p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </div>
    <template #pied>
      <AppBouton :occupe="envoiEnCours" @click="envoyer">Envoyer le devis</AppBouton>
      <AppBouton variante="secondaire" @click="emit('fermer')">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
