<script setup lang="ts">
// Mon compte (.doc/ihm/RM-COMPTE-IHM.md) : mes informations et, pour les 16-17 ans, l'accord des parents.
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppChampFichier from '../components/ui/AppChampFichier.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { age, formaterDate, formaterDateHeure } from '../outils/dates'

interface EtatAccord {
  necessaire: boolean
  statut: 'en_attente' | 'accepte' | 'refuse' | null
  motif_refus: string | null
  depose_le: string | null
}

const routeur = useRouter()
const { compte, chargementFait, chargerCompte } = useCompte()
const { afficherMessage } = useMessage()
const accord = ref<EtatAccord | null>(null)
const fichier = ref<File | null>(null)
const erreur = ref('')
const envoiEnCours = ref(false)

async function chargerAccord() {
  if (compte.value?.accord_parental_necessaire) {
    accord.value = await appelerServeur<EtatAccord>('/api/moi/accord-parental')
  }
}
onMounted(chargerAccord)
watch(compte, chargerAccord)

async function envoyerAccord() {
  erreur.value = ''
  if (!fichier.value) {
    erreur.value = 'Choisis d\'abord le fichier de l\'accord signé.'
    return
  }
  envoiEnCours.value = true
  try {
    const formulaire = new FormData()
    formulaire.append('fichier', fichier.value)
    accord.value = await appelerServeur<EtatAccord>('/api/moi/accord-parental', formulaire)
    fichier.value = null
    afficherMessage("Accord envoyé : il attend la vérification de l'administrateur.")
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}

async function renvoyerLien() {
  try {
    afficherMessage((await appelerServeur<{ message: string }>('/api/comptes/verification/renvoi', { email: compte.value?.email })).message)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

async function actualiser() {
  await chargerCompte()
  await chargerAccord()
}
</script>

<template>
  <AppCarte v-if="chargementFait && !compte" titre="Mon compte" intro="Connectez-vous pour voir votre compte.">
    <AppBouton pleine-largeur @click="routeur.push('/connexion')">Se connecter</AppBouton>
  </AppCarte>

  <div v-else-if="compte" class="flex flex-col gap-5">
    <h1 class="text-[28px] font-bold">Mon compte</h1>

    <section class="flex flex-col gap-3.5 rounded-rafals border border-bord bg-surface p-5">
      <h2 class="text-xl font-bold">Mes informations</h2>
      <dl class="grid grid-cols-[auto_1fr] gap-x-[18px] gap-y-2 text-[14.5px]">
        <dt class="text-texte-doux">Nom</dt>
        <dd class="font-medium">{{ compte.prenom }} {{ compte.nom }}</dd>
        <dt class="text-texte-doux">Adresse mail</dt>
        <dd class="flex flex-wrap items-center gap-2 font-medium">
          {{ compte.email }}
          <AppBadge v-if="compte.email_verifie" etat="ok">vérifiée</AppBadge>
          <template v-else>
            <AppBadge etat="attente">pas encore vérifiée</AppBadge>
            <AppBouton variante="secondaire" @click="renvoyerLien">Renvoyer le lien</AppBouton>
          </template>
        </dd>
        <dt class="text-texte-doux">Téléphone</dt>
        <dd class="font-medium">{{ compte.telephone }}</dd>
        <template v-if="compte.date_naissance">
          <dt class="text-texte-doux">Date de naissance</dt>
          <dd class="font-medium">{{ formaterDate(compte.date_naissance) }} ({{ age(compte.date_naissance) }} ans)</dd>
        </template>
      </dl>
      <p class="text-[13px] text-texte-doux">Modifier vos informations ou fermer votre compte : bientôt disponible.</p>
    </section>

    <section
      v-if="compte.accord_parental_necessaire && accord"
      class="flex flex-col gap-3.5 rounded-rafals border border-bord bg-surface p-5"
    >
      <h2 class="text-xl font-bold">Accord de tes parents</h2>

      <template v-if="accord.statut === 'accepte'">
        <div><AppBadge etat="ok">Accepté</AppBadge></div>
        <p class="text-texte-doux">Tu peux réserver et publier des annonces.</p>
      </template>

      <template v-else-if="accord.statut === 'en_attente'">
        <div><AppBadge etat="attente">En attente de vérification</AppBadge></div>
        <p class="text-texte-doux">
          Envoyé le {{ formaterDateHeure(accord.depose_le ?? '') }}. Tu verras la réponse ici.
        </p>
        <div><AppBouton variante="secondaire" @click="actualiser">Actualiser</AppBouton></div>
      </template>

      <template v-else>
        <AppAlerte etat="attente">
          Tu as {{ age(compte.date_naissance ?? '') }} ans : pour réserver ou publier une annonce, il faut l'accord signé de
          tes parents, vérifié par rafals.
        </AppAlerte>
        <AppAlerte v-if="accord.statut === 'refuse'">
          Ton accord a été refusé : « {{ accord.motif_refus }} ». Tu peux en envoyer un nouveau.
        </AppAlerte>
        <form class="flex flex-col gap-3.5" @submit.prevent="envoyerAccord">
          <AppChampFichier
            v-model="fichier"
            etiquette="Accord signé de tes parents"
            aide="PDF, JPG ou PNG, 5 Mo au maximum (ex. une photo de la lettre signée)"
            accepte="application/pdf,image/jpeg,image/png"
          />
          <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
          <div><AppBouton type="submit" :occupe="envoiEnCours">Envoyer l'accord</AppBouton></div>
        </form>
      </template>
    </section>
  </div>
</template>
