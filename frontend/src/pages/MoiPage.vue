<script setup lang="ts">
// Page « Moi » (entrée de la barre du bas, sur téléphone), identique à la grande maquette : mon rond et mon nom,
// puis Mon profil, Mes abonnements, Paramètres, et [Se déconnecter]. Sur ordinateur, la même liste s'ouvre sous le
// prénom, en haut à droite (AppEntete). .doc/ihm/RM-ENTETE-IHM.md.
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import AppIcone from '../components/ui/AppIcone.vue'
import AppInitiales from '../components/ui/AppInitiales.vue'
import { useCompte } from '../composables/useCompte'
import { useInstallation } from '../composables/useInstallation'
import { useMessage } from '../composables/useMessage'
import { useRetour } from '../composables/useRetour'
import type { NomIcone } from '../outils/icones'
import type { ProfilPrestataire } from '../outils/prestataires'

const routeur = useRouter()
const { compte, chargementFait, seDeconnecter } = useCompte()
const { afficherMessage } = useMessage()
const { retourOuvert } = useRetour()
const { facon: faconInstaller, installer } = useInstallation()

// Sous le nom : « Électricien · Plombier · Nantes » pour un prestataire, l'adresse mail pour un client
const profil = ref<ProfilPrestataire | null>(null)
async function charger() {
  if (compte.value?.prestataire_id && !profil.value) profil.value = await appelerServeur<ProfilPrestataire>('/api/moi/prestataire').catch(() => null)
}
onMounted(charger)
watch(compte, charger)
const sousTitre = computed(() => {
  if (!profil.value) return compte.value?.email ?? ''
  const p = profil.value
  return [p.metier_principal.nom, ...p.metiers_secondaires.map((m) => m.nom), p.commune.nom].join(' · ')
})
watch([chargementFait, compte], () => {
  if (chargementFait.value && !compte.value) routeur.replace('/connexion')
})

const lignes = computed<{ vers: string; icone: NomIcone; texte: string; detail: string }[]>(() => [
  { vers: '/profil', icone: 'moi', texte: 'Mon profil', detail: compte.value?.prestataire_id ? 'Mes métiers, ma zone' : 'Mes informations, proposer mes services' },
  { vers: '/mes-abonnements', icone: 'coeur', texte: 'Mes abonnements', detail: 'Les prestataires que je suis' },
  { vers: '/parametres', icone: 'reglages', texte: 'Paramètres', detail: 'Thème, notifications' },
  ...(compte.value?.est_administrateur ? [{ vers: '/administration', icone: 'bouclier' as const, texte: 'Administration', detail: 'Comptes, métiers, signalements' }] : []),
])

async function installerRafals() {
  if (faconInstaller.value === 'apple') afficherMessage('Dans Safari : bouton Partager, puis « Sur l’écran d’accueil ».')
  else if (await installer()) afficherMessage('rafals est installé sur cet appareil.')
}
async function deconnexion() {
  try {
    await seDeconnecter()
    afficherMessage('Vous êtes déconnecté.')
    routeur.push('/connexion')
  } catch (erreur) {
    afficherMessage(messageErreur(erreur), 'erreur')
  }
}
</script>

<template>
  <div v-if="compte" class="page">
    <div class="tete"><h1>Mon compte</h1></div>
    <div class="carte fiche p-[18px]">
      <AppInitiales :nom="compte.prenom" taille="g" />
      <div class="infos">
        <h2>{{ compte.prenom }} {{ compte.nom[0] }}.</h2>
        <span class="doux">{{ sousTitre }}</span>
      </div>
    </div>
    <div class="liste">
      <RouterLink v-for="l in lignes" :key="l.vers" class="ligne" :to="l.vers">
        <span class="ico-rond"><AppIcone :nom="l.icone" /></span>
        <div class="txt"><b>{{ l.texte }}</b><span>{{ l.detail }}</span></div>
        <span class="fin"><AppIcone nom="suite" /></span>
      </RouterLink>
      <button type="button" class="ligne" @click="retourOuvert = true">
        <span class="ico-rond"><AppIcone nom="messages" /></span>
        <div class="txt"><b>Un problème ? Une idée ?</b><span>Écrivez-nous, nous regardons chaque soir</span></div>
      </button>
      <button v-if="faconInstaller" type="button" class="ligne" @click="installerRafals">
        <span class="ico-rond"><AppIcone nom="telecharger" /></span>
        <div class="txt"><b>Installer rafals</b><span>Une icône sur l’écran d’accueil</span></div>
      </button>
      <button type="button" class="ligne" @click="deconnexion">
        <span class="ico-rond" style="background: var(--erreur-doux); color: var(--erreur)"><AppIcone nom="sortir" /></span>
        <div class="txt"><b>Se déconnecter</b></div>
      </button>
    </div>
  </div>
</template>
