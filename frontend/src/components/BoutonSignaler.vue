<script setup lang="ts">
// Bouton « Signaler cette annonce… » / « Signaler ce prestataire… » (.doc/ihm/RM-SIGNALEMENTS-IHM.md ;
// RM-ADMINISTRATION.md, lot 6.4), en bas d'une annonce et de la page publique d'un prestataire. Pas connecté : on se
// connecte, puis on revient. L'administrateur regardera ; le prestataire ne sait pas qui a signalé.
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import FenetreTexte, { type DemandeTexte } from './FenetreTexte.vue'
import AppBouton from './ui/AppBouton.vue'

const props = defineProps<{ annonceId?: number; prestataireId?: number; nomPrestataire: string }>()
const route = useRoute()
const routeur = useRouter()
const { compte } = useCompte()
const { afficherMessage } = useMessage()
const demande = ref<DemandeTexte | null>(null)
const annonce = computed(() => props.annonceId !== undefined)

function ouvrir() {
  if (!compte.value) {
    afficherMessage(`Connectez-vous pour signaler ${annonce.value ? 'une annonce' : 'un prestataire'} : vous reviendrez ici.`)
    routeur.push({ path: '/connexion', query: { retour: route.fullPath } })
    return
  }
  demande.value = {
    titre: annonce.value ? 'Signaler cette annonce ?' : `Signaler ${props.nomPrestataire} ?`,
    explication: `L'administrateur de rafals regardera. ${props.nomPrestataire} ne saura pas qui a signalé.`,
    etiquette: 'Le problème',
    aide: annonce.value ? 'ex. « Prix mensonger, il demande 80 € sur place ». De 10 à 1000 caractères.' : 'ex. « Faux profil, la photo est volée ». De 10 à 1000 caractères.',
    chemin: '/api/signalements',
    cle: 'motif',
    fixes: annonce.value ? { annonce_id: props.annonceId } : { prestataire_id: props.prestataireId },
    bouton: 'Signaler',
    danger: true,
    reussite: "Merci : l'administrateur va regarder.",
  }
}
</script>

<template>
  <div class="flex justify-end">
    <AppBouton variante="danger" @click="ouvrir">{{ annonce ? 'Signaler cette annonce…' : 'Signaler ce prestataire…' }}</AppBouton>
  </div>
  <FenetreTexte :demande="demande" @fermer="demande = null" @fait="demande = null" />
</template>
