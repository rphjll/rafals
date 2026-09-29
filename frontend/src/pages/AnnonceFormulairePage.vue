<script setup lang="ts">
// Écrire ou modifier une annonce (.doc/ihm/RM-MES-ANNONCES-IHM.md ; RM-ANNONCES.md).
// /mes-annonces/nouvelle : écrire (publiée aussitôt, puis on ajoute les photos) ; /mes-annonces/12 : modifier.
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import PhotosAnnonce from '../components/annonces/PhotosAnnonce.vue'
import GardePrestataire from '../components/prestataire/GardePrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCase from '../components/ui/AppCase.vue'
import AppChamp from '../components/ui/AppChamp.vue'
import AppChoix from '../components/ui/AppChoix.vue'
import AppSection from '../components/ui/AppSection.vue'
import AppSelection from '../components/ui/AppSelection.vue'
import AppZoneTexte from '../components/ui/AppZoneTexte.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import {
  type AnnonceVisible,
  DUREES_PROPOSEES,
  type FormePrix,
  type Lieu,
  duree,
  euros,
  versCentimes,
} from '../outils/annonces'
import { aujourdhuiIso } from '../outils/dates'
import type { ProfilPrestataire } from '../outils/prestataires'

const DESCRIPTION_MAX = 1000

const route = useRoute()
const routeur = useRouter()
const { compte } = useCompte()
const { afficherMessage } = useMessage()

const profil = ref<ProfilPrestataire | null>(null)
const aUnLocal = ref(false)
const annonce = ref<AnnonceVisible | null>(null)
const pret = ref(false)
const erreur = ref('')
const envoiEnCours = ref(false)

// Le formulaire
const metierId = ref<number | null>(null)
const titre = ref('')
const description = ref('')
const forme = ref<FormePrix>('fixe')
const prix = ref('')
const dureeMinutes = ref<number | null>(60)
const heuresMin = ref('1')
const heuresMax = ref('3')
const lieu = ref<Lieu>('chez_client')
const carte = ref(false)
const especes = ref(true)

const identifiant = computed(() => (route.params.id ? Number(route.params.id) : null))
const titrePage = computed(() => (annonce.value ? `Modifier « ${annonce.value.titre} »` : 'Écrire une annonce'))

async function charger() {
  if (!compte.value?.prestataire_id) return
  try {
    const [p, local, mes] = await Promise.all([
      appelerServeur<ProfilPrestataire>('/api/moi/prestataire'),
      appelerServeur<object | null>('/api/moi/local'),
      identifiant.value ? appelerServeur<AnnonceVisible[]>('/api/moi/annonces') : Promise.resolve([]),
    ])
    profil.value = p
    aUnLocal.value = local !== null
    annonce.value = mes.find((a) => a.id === identifiant.value) ?? null
    if (identifiant.value && !annonce.value) erreur.value = "Cette annonce n'existe pas."
    remplir()
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    pret.value = true
  }
}
onMounted(charger)
watch([compte, identifiant], charger)

function remplir() {
  const a = annonce.value
  metierId.value = a?.metier.id ?? profil.value?.metier_principal.id ?? null
  titre.value = a?.titre ?? ''
  description.value = a?.description ?? ''
  forme.value = a?.forme_prix ?? 'fixe'
  prix.value = a?.prix_centimes ? euros(a.prix_centimes).replace(' €', '') : ''
  dureeMinutes.value = a?.duree_minutes ?? 60
  heuresMin.value = String(a?.heures_min ?? 1)
  heuresMax.value = String(a?.heures_max ?? 3)
  lieu.value = a?.lieu ?? 'chez_client'
  carte.value = a?.paiement_carte ?? false
  especes.value = a?.paiement_especes ?? true
}

// Seulement les métiers encore exercés du profil (RM-ANNONCES) ; celui d'une annonce existante reste choisissable
const metiers = computed(() => {
  const p = profil.value
  if (!p) return []
  const liste = [p.metier_principal, ...p.metiers_secondaires].filter((m) => !m.fin_le || m.fin_le >= aujourdhuiIso())
  if (annonce.value && !liste.some((m) => m.id === annonce.value?.metier.id)) liste.push({ ...annonce.value.metier, fin_le: null })
  return liste.map((m) => ({ valeur: m.id, texte: m.nom }))
})

const raisonLocal = computed(() =>
  aUnLocal.value ? undefined : "Ajoutez d'abord l'adresse de votre local (page « Mon activité »).",
)
const raisonCarte = computed(() =>
  profil.value?.siret_statut === 'verifie'
    ? undefined
    : 'Le paiement par carte demande un SIRET vérifié (page « Mon activité ») : sans lui, espèces seulement.',
)
const total = computed(() => {
  const centimes = versCentimes(prix.value)
  return centimes ? `ex. ${heuresMin.value} h → ${euros(centimes * Number(heuresMin.value))}` : ''
})

async function enregistrer() {
  erreur.value = ''
  if (!metierId.value) {
    erreur.value = 'Choisissez le métier.'
    return
  }
  const donnees = {
    metier_id: metierId.value,
    titre: titre.value,
    description: description.value,
    forme_prix: forme.value,
    prix_centimes: forme.value === 'devis' ? null : versCentimes(prix.value),
    duree_minutes: forme.value === 'fixe' ? dureeMinutes.value : null,
    heures_min: forme.value === 'heure' ? Number(heuresMin.value) : null,
    heures_max: forme.value === 'heure' ? Number(heuresMax.value) : null,
    lieu: lieu.value,
    paiement_carte: raisonCarte.value ? false : carte.value,
    paiement_especes: especes.value,
  }
  envoiEnCours.value = true
  try {
    if (annonce.value) {
      await appelerServeur<AnnonceVisible>(`/api/moi/annonces/${annonce.value.id}/modifier`, donnees)
      afficherMessage('Annonce enregistrée.')
      await routeur.push('/mes-annonces')
    } else {
      const nouvelle = await appelerServeur<AnnonceVisible>('/api/moi/annonces', donnees)
      afficherMessage('Annonce publiée : les clients peuvent la voir. Ajoutez des photos.')
      await routeur.replace(`/mes-annonces/${nouvelle.id}`) // on reste sur l'annonce, pour ajouter les photos
    }
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <GardePrestataire :titre="titrePage">
    <p class="text-[13.5px] text-texte-doux">
      <RouterLink to="/proposer" class="hover:text-primaire">Mon activité</RouterLink> ›
      <RouterLink to="/mes-annonces" class="hover:text-primaire">Mes annonces</RouterLink> › {{ titrePage }}
    </p>
    <h1 class="text-[28px] font-bold">{{ titrePage }}</h1>

    <form v-if="pret && profil" class="flex flex-col gap-4" @submit.prevent="enregistrer">
      <AppSection titre="Le service">
        <AppSelection v-model="metierId" etiquette="Métier" obligatoire :options="metiers" />
        <p class="-mt-2 text-[13px] text-texte-doux">Seulement les métiers de votre profil.</p>
        <AppChamp v-model="titre" etiquette="Titre" obligatoire maxlength="80" placeholder="ex. Ménage 2 h" />
        <AppZoneTexte v-model="description" etiquette="Description" :maximum="DESCRIPTION_MAX" aide="Facultative." />
      </AppSection>

      <AppSection titre="Le prix">
        <AppChoix
          v-model="forme"
          etiquette="Forme du prix"
          obligatoire
          :options="[
            { valeur: 'fixe', texte: 'Prix fixe', detail: 'ex. 50 € pour 2 h' },
            { valeur: 'heure', texte: 'À l\'heure', detail: 'le client choisit ses heures' },
            { valeur: 'devis', texte: 'Sur devis', detail: 'le client vous écrit' },
          ]"
        />
        <div v-if="forme === 'fixe'" class="grid gap-3 sm:grid-cols-2">
          <AppChamp v-model="prix" etiquette="Prix (€)" obligatoire inputmode="decimal" placeholder="ex. 50" />
          <AppSelection
            v-model="dureeMinutes"
            etiquette="Durée"
            obligatoire
            :options="DUREES_PROPOSEES.map((m) => ({ valeur: m, texte: duree(m) }))"
          />
        </div>
        <p v-if="forme === 'fixe'" class="text-[13px] text-texte-doux">
          La durée bloque votre agenda : jamais deux clients en même temps.
        </p>
        <template v-if="forme === 'heure'">
          <AppChamp v-model="prix" etiquette="Prix de l'heure (€)" obligatoire inputmode="decimal" placeholder="ex. 25" />
          <div class="grid gap-3 sm:grid-cols-2">
            <AppChamp v-model="heuresMin" etiquette="Au moins (heures)" type="number" min="1" obligatoire />
            <AppChamp v-model="heuresMax" etiquette="Au plus (heures)" type="number" min="1" obligatoire />
          </div>
          <p class="text-[13px] text-texte-doux">
            Le client choisit entre {{ heuresMin }} h et {{ heuresMax }} h et voit le total avant de réserver ({{ total }}).
          </p>
        </template>
        <p v-if="forme === 'devis'" class="text-[13px] text-texte-doux">
          Pas de prix ni de durée : le client vous décrit son besoin (avec photos), vous répondez par un devis (bientôt
          disponible).
        </p>
      </AppSection>

      <AppSection titre="Où et comment payer">
        <AppChoix
          v-model="lieu"
          etiquette="Lieu"
          obligatoire
          :options="[
            { valeur: 'chez_client', texte: 'Chez le client' },
            { valeur: 'chez_moi', texte: 'Chez moi', detail: 'à votre local', raisonVerrou: raisonLocal },
            { valeur: 'les_deux', texte: 'Les deux', raisonVerrou: raisonLocal },
          ]"
        />
        <div class="flex flex-col">
          <span class="text-[13px] font-semibold">Paiement <span class="text-erreur" aria-hidden="true">*</span> (au moins un)</span>
          <AppCase v-model="carte" texte="Carte bancaire, sur rafals" :raison-verrou="raisonCarte" />
          <AppCase v-model="especes" texte="Espèces, le jour du service" />
        </div>
      </AppSection>

      <PhotosAnnonce v-if="annonce" :annonce="annonce" @maj="(a) => (annonce = a)" />
      <AppSection v-else titre="Photos">
        <p class="text-[13.5px] text-texte-doux">Vous pourrez ajouter jusqu'à 5 photos juste après avoir publié.</p>
      </AppSection>

      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
      <div class="flex flex-wrap gap-2">
        <AppBouton type="submit" :occupe="envoiEnCours">{{ annonce ? 'Enregistrer' : "Publier l'annonce" }}</AppBouton>
        <AppBouton variante="secondaire" @click="routeur.push('/mes-annonces')">Annuler</AppBouton>
      </div>
    </form>
    <AppAlerte v-else-if="erreur">{{ erreur }}</AppAlerte>
  </GardePrestataire>
</template>
