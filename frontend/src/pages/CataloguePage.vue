<script setup lang="ts">
// Catalogue des composants communs (.doc/ihm/RM-CATALOGUE-IHM.md) : tout voir d'un coup d'œil,
// sur les 4 formats d'écran, avant de s'en servir dans les vrais écrans.
import { ref } from 'vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppChamp from '../components/ui/AppChamp.vue'
import AppFenetre from '../components/ui/AppFenetre.vue'
import { useMessage } from '../composables/useMessage'

const { afficherMessage } = useMessage()
const fenetreOuverte = ref(false)
const email = ref('julie.martin@example.com')
const motDePasse = ref('soleil')

function confirmer() {
  fenetreOuverte.value = false
  afficherMessage('Rendez-vous confirmé · mardi 14/10 à 10 h 00')
}
</script>

<template>
  <div class="flex flex-col gap-8">
    <header class="flex flex-col gap-1">
      <h1 class="text-[28px] font-bold">Catalogue des composants</h1>
      <p class="text-texte-doux">Les briques communes de tous les écrans de rafals. Tout est cliquable.</p>
    </header>

    <section class="flex flex-col gap-3 rounded-rafals border border-bord bg-surface p-5">
      <h2 class="text-xl font-bold">Boutons</h2>
      <div class="flex flex-wrap gap-3 pt-10">
        <AppBouton @click="afficherMessage('Bouton principal cliqué')">Réserver mardi 14/10 à 10 h 00</AppBouton>
        <AppBouton variante="secondaire" @click="afficherMessage('Bouton secondaire cliqué')">Demander un devis</AppBouton>
        <AppBouton variante="danger" @click="afficherMessage('Annulation refusée : exemple de message d\'erreur', 'erreur')">
          Annuler
        </AppBouton>
        <AppBouton
          variante="verrouille"
          raison-verrou="Karim n'a pas encore de SIRET : il ne peut être payé qu'en espèces, le jour du rendez-vous. Réservez, puis payez-le sur place."
        >
          Payer par carte
        </AppBouton>
      </div>
      <p class="text-[13px] text-texte-doux">Clique sur « 🔒 Payer par carte » : une bulle explique pourquoi il est bloqué.</p>
    </section>

    <section class="flex flex-col gap-3 rounded-rafals border border-bord bg-surface p-5">
      <h2 class="text-xl font-bold">Champs</h2>
      <div class="grid gap-4 sm:grid-cols-2">
        <AppChamp v-model="email" etiquette="Adresse mail" type="email" obligatoire aide="Exemple de donnée d'essai : @example.com" />
        <AppChamp
          v-model="motDePasse"
          etiquette="Mot de passe"
          type="password"
          obligatoire
          :erreur="motDePasse.length < 10 ? 'Au moins 10 caractères (ex. MaisonBleue44).' : ''"
        />
      </div>
    </section>

    <section class="flex flex-col gap-3 rounded-rafals border border-bord bg-surface p-5">
      <h2 class="text-xl font-bold">Badges</h2>
      <div class="flex flex-wrap gap-2">
        <AppBadge etat="ok">SIRET vérifié</AppBadge>
        <AppBadge etat="attente">Sans SIRET</AppBadge>
        <AppBadge etat="erreur">Rendez-vous annulé</AppBadge>
        <AppBadge etat="neutre">Espèces seulement</AppBadge>
      </div>
    </section>

    <section class="flex flex-col items-start gap-3 rounded-rafals border border-bord bg-surface p-5">
      <h2 class="text-xl font-bold">Fenêtre et message</h2>
      <AppBouton @click="fenetreOuverte = true">Ouvrir la fenêtre de confirmation</AppBouton>
      <p class="text-[13px] text-texte-doux">« Confirmer » ferme la fenêtre et affiche un message en bas de l'écran pendant 3 secondes.</p>
    </section>

    <AppFenetre :ouverte="fenetreOuverte" titre="Confirmer le rendez-vous ?" @fermer="fenetreOuverte = false">
      Karim Benali · Petits travaux électriques<br />
      Mardi 14/10/2026 à 10 h 00 · 8 allée des Pins, Talence<br />
      Paiement en espèces le jour même.
      <template #pied>
        <AppBouton @click="confirmer">Confirmer</AppBouton>
        <AppBouton variante="danger" @click="fenetreOuverte = false">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
