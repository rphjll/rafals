<script setup lang="ts">
// Une annonce vue par un client (.doc/ihm/RM-ANNONCE-IHM.md) : photos, prix, durée, lieu (la ville, jamais la rue),
// paiement, description. Son auteur la voit aussi quand elle est cachée (aperçu).
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import BoutonSignaler from '../components/BoutonSignaler.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppSection from '../components/ui/AppSection.vue'
import AppSelection from '../components/ui/AppSelection.vue'
import ChoixHoraire from '../components/rendez-vous/ChoixHoraire.vue'
import FenetreReservation from '../components/rendez-vous/FenetreReservation.vue'
import FenetreDemandeDevis from '../components/devis/FenetreDemandeDevis.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import type { RendezVousVisible } from '../outils/rendez_vous'
import { type AnnoncePublique, duree, euros, lieuPourLeClient, paiement } from '../outils/annonces'

const route = useRoute()
const routeur = useRouter()
const { afficherMessage } = useMessage()
const { compte } = useCompte()
const annonce = ref<AnnoncePublique | null>(null)
const erreur = ref('')
const photo = ref(1)

async function charger() {
  erreur.value = ''
  try {
    annonce.value = await appelerServeur<AnnoncePublique>(`/api/annonces/${route.params.id}`)
    photo.value = 1
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
watch(() => route.params.id, charger, { immediate: true })

// ---------- Réserver ----------
const heures = ref<number | null>(null)
const debutChoisi = ref<string | null>(null)
watch(annonce, (a) => (heures.value = a?.heures_min ?? null))
const choixHeures = computed(() => {
  const a = annonce.value
  if (!a?.heures_min || !a.heures_max) return []
  return Array.from({ length: a.heures_max - a.heures_min + 1 }, (_, n) => (a.heures_min ?? 1) + n)
})
function choisir(debut: string) {
  if (!compte.value) {
    // Pas connecté : se connecter, puis revenir sur cette annonce
    afficherMessage('Connectez-vous pour réserver : vous reviendrez ici.')
    routeur.push({ path: '/connexion', query: { retour: route.fullPath } })
    return
  }
  if (monAnnonce.value) {
    afficherMessage('Vous ne pouvez pas réserver votre propre annonce.', 'erreur')
    return
  }
  debutChoisi.value = debut
}
function reserve(rdv: RendezVousVisible) {
  debutChoisi.value = null
  afficherMessage(rdv.statut === 'confirme' ? 'Rendez-vous confirmé.' : 'Demande envoyée : le prestataire a 24 h pour répondre.')
  routeur.push('/rendez-vous')
}

// ---------- Demander un devis (lot 5.4) ----------
const demandeOuverte = ref(false)
function demanderDevis() {
  if (!compte.value) {
    afficherMessage('Connectez-vous pour demander un devis : vous reviendrez ici.')
    routeur.push({ path: '/connexion', query: { retour: route.fullPath } })
    return
  }
  demandeOuverte.value = true
}
function demandeEnvoyee() {
  demandeOuverte.value = false
  afficherMessage(`Demande envoyée : ${annonce.value?.prestataire.nom_affiche} va vous répondre.`)
  routeur.push('/devis')
}

const monAnnonce = computed(() => !!annonce.value && compte.value?.prestataire_id === annonce.value.prestataire.id)
const prix = computed(() => {
  const a = annonce.value
  if (!a || a.prix_centimes === null) return 'Sur devis'
  return a.forme_prix === 'heure' ? `${euros(a.prix_centimes)} de l'heure` : euros(a.prix_centimes)
})
</script>

<template>
  <div class="mx-auto flex w-full max-w-[720px] flex-col gap-4">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <template v-if="annonce">
      <AppAlerte v-if="monAnnonce" etat="attente">
        Aperçu de votre annonce, telle que les clients la voient.
        <RouterLink :to="`/mes-annonces/${annonce.id}`" class="font-semibold underline">Modifier</RouterLink>
      </AppAlerte>

      <div v-if="annonce.nombre_photos" class="flex flex-col gap-2">
        <img
          :src="`/api/annonces/${annonce.id}/photos/${photo}`"
          :alt="`Photo ${photo} de « ${annonce.titre} »`"
          class="max-h-[360px] w-full rounded-rafals object-cover"
        />
        <div v-if="annonce.nombre_photos > 1" class="flex flex-wrap gap-2">
          <button
            v-for="ordre in annonce.nombre_photos"
            :key="ordre"
            type="button"
            class="size-14 overflow-hidden rounded-lg border-2"
            :class="ordre === photo ? 'border-primaire' : 'border-transparent'"
            :aria-label="`Voir la photo ${ordre}`"
            @click="photo = ordre"
          >
            <img :src="`/api/annonces/${annonce.id}/photos/${ordre}`" alt="" class="size-full object-cover" />
          </button>
        </div>
      </div>

      <AppSection>
        <div class="flex flex-wrap items-baseline justify-between gap-3">
          <h1 class="text-2xl font-bold">{{ annonce.titre }}</h1>
          <span class="text-[22px] font-bold text-primaire">{{ prix }}</span>
        </div>
        <p class="text-[14.5px] text-texte-doux">
          par
          <RouterLink :to="`/prestataires/${annonce.prestataire.id}`" class="font-bold text-texte underline hover:text-primaire">
            {{ annonce.prestataire.nom_affiche }}
          </RouterLink>
          · {{ annonce.metier.nom }}
        </p>
        <dl class="grid grid-cols-[auto_1fr] gap-x-[18px] gap-y-2 text-[14.5px]">
          <template v-if="annonce.forme_prix === 'fixe' && annonce.duree_minutes">
            <dt class="text-texte-doux">Durée</dt>
            <dd class="font-medium">{{ duree(annonce.duree_minutes) }}</dd>
          </template>
          <template v-if="annonce.forme_prix === 'heure'">
            <dt class="text-texte-doux">Durée</dt>
            <dd class="font-medium">au choix, de {{ annonce.heures_min }} h à {{ annonce.heures_max }} h</dd>
          </template>
          <dt class="text-texte-doux">Où</dt>
          <dd class="font-medium">{{ lieuPourLeClient(annonce) }}</dd>
          <dt class="text-texte-doux">Paiement</dt>
          <dd class="font-medium">{{ paiement(annonce.modes_de_paiement) }}</dd>
        </dl>
        <p v-if="annonce.description" class="whitespace-pre-line">{{ annonce.description }}</p>
        <div v-if="annonce.forme_prix === 'devis'" class="pt-10 sm:pt-0">
          <p v-if="monAnnonce" class="text-[14px] text-texte-doux">Vos clients vous écriront ici (« Mes devis »).</p>
          <AppBouton v-else @click="demanderDevis">Demander un devis</AppBouton>
        </div>
        <BoutonSignaler v-if="!monAnnonce" :annonce-id="annonce.id" :nom-prestataire="annonce.prestataire.nom_affiche" />
      </AppSection>

      <!-- Réserver (RM-RENDEZ-VOUS) : les horaires libres des 14 prochains jours, puis la fenêtre de confirmation -->
      <AppSection v-if="annonce.forme_prix !== 'devis'" titre="Choisir un horaire">
        <p v-if="monAnnonce" class="text-[14px] text-texte-doux">
          Vos clients choisiront ici un horaire libre de votre agenda (vous ne pouvez pas réserver votre propre annonce).
        </p>
        <AppSelection
          v-if="annonce.forme_prix === 'heure' && choixHeures.length > 1"
          v-model="heures"
          etiquette="Combien d'heures ?"
          :options="choixHeures.map((h) => ({ valeur: h, texte: `${h} h · ${euros((annonce?.prix_centimes ?? 0) * h)}` }))"
        />
        <ChoixHoraire :annonce-id="annonce.id" :heures="annonce.forme_prix === 'heure' ? heures : null" @choisir="choisir" />
      </AppSection>
      <FenetreDemandeDevis
        v-if="annonce.forme_prix === 'devis'"
        :annonce="annonce"
        :ouverte="demandeOuverte"
        @fermer="demandeOuverte = false"
        @envoyee="demandeEnvoyee"
      />
      <FenetreReservation
        :annonce="annonce"
        :debut="debutChoisi"
        :heures="heures"
        @fermer="debutChoisi = null"
        @reserve="reserve"
      />
    </template>
  </div>
</template>
