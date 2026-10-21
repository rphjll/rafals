<script setup lang="ts">
// Onglet « Mon compte » de « Mon profil » (.doc/ihm/RM-PROFIL-IHM.md, 21/10/2026) : les cartes du compte
// (RM-COMPTE-IHM.md), chacune en ligne qui se déplie. Les mêmes pour un prestataire et pour un client.
import { computed, ref } from 'vue'
import type { CompteVisible } from '../../composables/useCompte'
import CarteAdresse from '../CarteAdresse.vue'
import CarteNotifications from '../alertes/CarteNotifications.vue'
import CarteAbsences from '../compte/CarteAbsences.vue'
import CarteAccordParental from '../compte/CarteAccordParental.vue'
import CarteDonnees from '../compte/CarteDonnees.vue'
import CarteFermeture from '../compte/CarteFermeture.vue'
import CarteInformations from '../compte/CarteInformations.vue'
import CartePaiements from '../compte/CartePaiements.vue'
import AppListeLignes from '../ui/AppListeLignes.vue'

const props = defineProps<{ compte: CompteVisible; prestataire: boolean }>()
const lignes = ref<InstanceType<typeof AppListeLignes> | null>(null)
defineExpose({ ouvrir: (cle: string) => lignes.value?.ouvrir(cle) })

const resumes = computed(() => ({
  'Mes informations': [props.compte.email, props.compte.telephone].filter(Boolean).join(' · '),
  'Accord de tes parents': 'Obligatoire avant 18 ans pour réserver ou proposer vos services',
  'Mon adresse': props.prestataire
    ? 'Aussi celle de votre local ; les clients voient seulement la ville'
    : 'Demandée quand vous réservez un service à domicile',
  Absences: 'Rendez-vous manqués sans prévenir',
  'Notifications sur cet appareil': "Quand on vous écrit ou qu'on vous fait une proposition",
  'Mes paiements par carte': 'Vos paiements et vos remboursements',
  'Mes données': 'Télécharger tout ce que rafals sait de vous',
  'Fermer mon compte': 'Définitif',
}))
</script>

<template>
  <AppListeLignes ref="lignes" :resumes="resumes">
    <CarteInformations :compte="compte" />
    <CarteAccordParental v-if="compte.accord_parental_necessaire" :compte="compte" />
    <CarteAdresse
      titre="Mon adresse"
      chemin="/api/moi/adresse"
      :texte-vide="
        prestataire
          ? 'Aucune adresse enregistrée : ajoutez-la si des clients viennent chez vous (salon, atelier…) ou pour réserver un service à domicile.'
          : 'Aucune adresse enregistrée : elle vous sera demandée quand vous réserverez un service à domicile.'
      "
      :note="prestataire ? 'C’est aussi l’adresse de votre local. Les clients voient seulement la ville ; la rue, après avoir réservé.' : undefined"
      texte-ajouter="Ajouter mon adresse"
      texte-effacer="Effacer mon adresse"
    />
    <CarteAbsences />
    <CarteNotifications
      titre="Notifications sur cet appareil"
      exemple="Une notification quand on vous écrit ou qu'on vous fait une proposition, ex. « Karim vous a écrit »."
    />
    <CartePaiements />
    <CarteDonnees />
    <CarteFermeture />
  </AppListeLignes>
</template>
