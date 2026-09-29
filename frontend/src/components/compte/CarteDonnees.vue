<script setup lang="ts">
// Mon compte › Mes données (.doc/ihm/RM-COMPTE-IHM.md ; RM-CLIENTS.md) : droit d'accès prévu par la loi (RGPD).
// Le serveur répond « fichier à enregistrer » : le navigateur télécharge mes-donnees-rafals.json sans quitter la page.
import AppBouton from '../ui/AppBouton.vue'
import AppSection from '../ui/AppSection.vue'

function telecharger() {
  window.location.assign('/api/moi/donnees')
}
</script>

<template>
  <AppSection titre="Mes données">
    <p class="text-[13.5px] text-texte-doux">
      Un fichier avec tout ce que rafals sait sur vous (compte, adresse, profil de prestataire, historique de vos actions).
      C'est un droit prévu par la loi.
    </p>
    <div><AppBouton variante="secondaire" @click="telecharger">Télécharger mes données</AppBouton></div>
  </AppSection>
</template>
