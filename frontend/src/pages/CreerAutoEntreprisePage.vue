<script setup lang="ts">
// Créer mon auto-entreprise sans quitter rafals (.doc/ihm/RM-CREATION-AUTO-ENTREPRISE-IHM.md ; lot 7.2, maquette validée
// par Raphael le 04/10/2026) : départ, 5 étapes, puis suivi du dossier. rafals envoie le dossier au guichet de l'État.
// Le guide « je le fais moi-même » reste à /creer-mon-auto-entreprise/guide.
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import CarteDejaEntreprise from '../components/creation/CarteDejaEntreprise.vue'
import EtapeActivite from '../components/creation/EtapeActivite.vue'
import EtapeChoix from '../components/creation/EtapeChoix.vue'
import EtapeEnvoi from '../components/creation/EtapeEnvoi.vue'
import EtapePapiers from '../components/creation/EtapePapiers.vue'
import EtapesCreation from '../components/creation/EtapesCreation.vue'
import EtapeVous from '../components/creation/EtapeVous.vue'
import SuiviDossier from '../components/creation/SuiviDossier.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppFenetre from '../components/ui/AppFenetre.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { CHEMIN, CLES_ETAPES, envoyerEtape, type ReglesMetiers, type Situation } from '../outils/creation'

const routeur = useRouter()
const { compte, chargementFait } = useCompte()
const { afficherMessage } = useMessage()
const situation = ref<Situation | null>(null)
const regles = ref<ReglesMetiers | null>(null)
// 0 : le départ (ou le suivi d'un dossier envoyé) ; 1 à 5 : les étapes
const etape = ref(0)
const erreur = ref('')
const envoiEnCours = ref(false)
const fenetreEffacer = ref(false)

const dossier = computed(() => situation.value?.dossier ?? null)
const modifiable = computed(() => dossier.value?.statut === 'brouillon' || dossier.value?.statut === 'a_corriger')
const fini = computed(() => dossier.value !== null && ['refuse', 'ferme'].includes(dossier.value.statut))
// Une étape est finie quand il ne lui manque rien
const faites = computed(() => [...CLES_ETAPES.map((cle) => dossier.value !== null && !dossier.value.manque[cle]?.length), false])

async function charger() {
  erreur.value = ''
  try {
    regles.value ??= await appelerServeur<ReglesMetiers>('/api/creation-entreprise/metiers')
    situation.value = compte.value ? await appelerServeur<Situation>(CHEMIN) : null
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
watch(compte, charger)

function recu(nouvelle: Situation, suivante?: number) {
  situation.value = nouvelle
  if (suivante !== undefined) aller(suivante)
  // Dossier envoyé (ou correction envoyée) : on revient au suivi
  if (!['brouillon', 'a_corriger'].includes(nouvelle.dossier?.statut ?? '')) aller(0)
}

function aller(numero: number) {
  etape.value = numero
  window.scrollTo({ top: 0 })
}

async function commencer() {
  if (!compte.value) {
    routeur.push({ path: '/connexion', query: { retour: '/creer-mon-auto-entreprise' } })
    return
  }
  erreur.value = ''
  envoiEnCours.value = true
  try {
    situation.value = await envoyerEtape('')
    // On reprend à la première étape pas encore finie
    const premiere = faites.value.findIndex((faite) => !faite)
    aller(premiere + 1)
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}

async function effacer() {
  erreur.value = ''
  try {
    situation.value = await envoyerEtape('/effacer')
    fenetreEffacer.value = false
    aller(0)
    afficherMessage('Dossier effacé.')
  } catch (e) {
    fenetreEffacer.value = false
    erreur.value = messageErreur(e)
  }
}
</script>

<template>
  <div class="mx-auto flex w-full max-w-[720px] flex-col gap-4">
    <h1 class="text-[28px] font-bold">{{ dossier && !modifiable ? 'Mon dossier de création' : 'Créer mon auto-entreprise' }}</h1>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <!-- Les 5 étapes -->
    <template v-if="dossier && modifiable && etape > 0 && regles">
      <EtapesCreation :etape="etape" :faites="faites" @aller="aller" />
      <AppAlerte v-if="dossier.statut === 'a_corriger'" etat="attente">
        Correction demandée par l'administration : « {{ dossier.motif }} ». Corrigez, puis revenez au suivi pour envoyer.
      </AppAlerte>
      <EtapeVous v-if="etape === 1" :key="`vous-${dossier.id}`" :dossier="dossier" @enregistre="(s) => recu(s, 2)" @retour="aller(0)" />
      <EtapeActivite v-else-if="etape === 2" :dossier="dossier" :regles="regles" @enregistre="(s) => recu(s, 3)" @retour="aller(1)" />
      <EtapeChoix v-else-if="etape === 3" :dossier="dossier" @enregistre="(s) => recu(s, dossier?.statut === 'a_corriger' ? 0 : 4)" @retour="aller(2)" />
      <EtapePapiers v-else-if="etape === 4" :dossier="dossier" @enregistre="(s) => recu(s)" @suite="(s) => recu(s, dossier?.statut === 'a_corriger' ? 0 : 5)" @retour="aller(3)" />
      <EtapeEnvoi v-else :dossier="dossier" @enregistre="(s) => recu(s)" @aller="aller" @retour="aller(4)" />
      <div v-if="dossier.statut === 'a_corriger'"><AppBouton variante="secondaire" @click="aller(0)">Revenir au suivi</AppBouton></div>
    </template>

    <!-- Le suivi d'un dossier envoyé -->
    <SuiviDossier
      v-else-if="dossier && dossier.statut !== 'brouillon'"
      :dossier="dossier"
      :a-un-profil="situation?.a_un_profil ?? false"
      @enregistre="(s) => recu(s)"
      @corriger-reponses="aller(1)"
      @recommencer="commencer"
    />

    <!-- Le départ -->
    <template v-if="etape === 0 && (!dossier || dossier.statut === 'brouillon' || fini) && chargementFait">
      <AppAlerte v-if="situation && !situation.peut_commencer" etat="ok">{{ situation.raison }}</AppAlerte>
      <template v-else>
        <AppSection v-if="!fini" titre="rafals fait la démarche avec vous">
          <p>
            Vous répondez à quelques questions ici, vous déposez 2 ou 3 papiers, et rafals envoie votre dossier au guichet
            officiel de l'État. Vous n'avez aucun autre site à ouvrir.
          </p>
          <dl class="grid grid-cols-[auto_1fr] gap-x-3.5 gap-y-1 text-[14px]">
            <dt class="text-texte-doux">Durée</dt>
            <dd>environ 15 minutes</dd>
            <dt class="text-texte-doux">Prix</dt>
            <dd>gratuit</dd>
            <dt class="text-texte-doux">Résultat</dt>
            <dd>votre numéro SIRET, sous 1 à 4 semaines, ajouté tout seul à votre profil</dd>
          </dl>
          <AppAlerte etat="neutre">
            À préparer : votre pièce d'identité, votre numéro de sécurité sociale (sur la carte Vitale) et, pour un métier
            réglementé (plombier, coiffeur…), votre diplôme.
          </AppAlerte>
          <div class="flex flex-wrap gap-2">
            <AppBouton :occupe="envoiEnCours" @click="commencer">{{ dossier ? 'Reprendre mon dossier' : 'Commencer' }}</AppBouton>
            <AppBouton variante="secondaire" @click="routeur.push('/creer-mon-auto-entreprise/guide')">Je préfère le faire moi-même</AppBouton>
            <AppBouton v-if="dossier" variante="danger" @click="fenetreEffacer = true">Effacer mon dossier…</AppBouton>
          </div>
          <p v-if="!compte" class="text-[13px] text-texte-doux">Il faut être connecté : votre dossier est gardé dans votre compte, vous pouvez vous arrêter et reprendre plus tard.</p>
        </AppSection>
        <CarteDejaEntreprise v-if="!dossier || fini" :a-un-profil="situation?.a_un_profil ?? false" @enregistre="(s) => recu(s)" />
      </template>
      <p class="text-[13.5px] text-texte-doux">
        Besoin d'un conseil sur le statut ? Voyez la CCI ou la chambre des métiers (gratuit). Ces explications sont une aide,
        pas un conseil juridique.
      </p>
    </template>

    <AppFenetre :ouverte="fenetreEffacer" titre="Effacer mon dossier ?" @fermer="fenetreEffacer = false">
      <p>Vos réponses et vos papiers seront effacés de rafals. Rien n'a été envoyé à l'administration.</p>
      <template #pied>
        <AppBouton variante="danger" @click="effacer">Effacer</AppBouton>
        <AppBouton variante="secondaire" @click="fenetreEffacer = false">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
