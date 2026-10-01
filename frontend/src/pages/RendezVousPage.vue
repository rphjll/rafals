<script setup lang="ts">
// Mes rendez-vous, côté client (.doc/ihm/RM-RENDEZ-VOUS-IHM.md ; RM-RENDEZ-VOUS.md) : à venir (annuler, déplacer dans
// le délai du prestataire), puis passés et annulés.
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../api'
import ChoixHoraire from '../components/rendez-vous/ChoixHoraire.vue'
import LigneRendezVous from '../components/rendez-vous/LigneRendezVous.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCarte from '../components/ui/AppCarte.vue'
import AppFenetre from '../components/ui/AppFenetre.vue'
import AppOnglets from '../components/ui/AppOnglets.vue'
import AppSection from '../components/ui/AppSection.vue'
import { useCompte } from '../composables/useCompte'
import { useMessage } from '../composables/useMessage'
import { aParis, heure, jourCourt } from '../outils/agenda'
import { type RendezVousVisible, aVenir, momentCourt, plage } from '../outils/rendez_vous'

const routeur = useRouter()
const { compte, chargementFait } = useCompte()
const { afficherMessage } = useMessage()
const onglet = ref('a-venir')
const tous = ref<RendezVousVisible[] | null>(null)
const erreur = ref('')

async function charger() {
  if (!compte.value) return
  try {
    tous.value = await appelerServeur<RendezVousVisible[]>('/api/moi/rendez-vous')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
watch(compte, charger)

// À venir : le plus proche d'abord ; passés et annulés : le plus récent d'abord
const avenir = computed(() => (tous.value ?? []).filter((r) => aVenir(r)).sort((a, b) => a.debut.localeCompare(b.debut)))
const passes = computed(() => (tous.value ?? []).filter((r) => !aVenir(r)))
const dansLeDelai = (r: RendezVousVisible) => !r.annulable_jusqu_au || new Date() < new Date(r.annulable_jusqu_au)
const raisonHorsDelai = (r: RendezVousVisible) =>
  `Le délai d'annulation gratuite est passé : appelez ${r.autre.nom}${r.autre.telephone ? ` au ${r.autre.telephone}` : ''}.`

// ---------- Annuler ----------
const aAnnuler = ref<RendezVousVisible | null>(null)
async function annuler() {
  const r = aAnnuler.value
  if (!r) return
  try {
    await appelerServeur(`/api/moi/rendez-vous/${r.id}/annuler`, {})
    aAnnuler.value = null
    afficherMessage(r.statut === 'en_attente' ? 'Demande annulée.' : 'Rendez-vous annulé.')
    await charger()
  } catch (e) {
    aAnnuler.value = null
    afficherMessage(messageErreur(e), 'erreur')
  }
}

// ---------- Déplacer ----------
const aDeplacer = ref<RendezVousVisible | null>(null)
const erreurDeplacement = ref('')
async function deplacer(debut: string) {
  const r = aDeplacer.value
  if (!r) return
  erreurDeplacement.value = ''
  try {
    const nouveau = await appelerServeur<RendezVousVisible>(`/api/moi/rendez-vous/${r.id}/deplacer`, { debut })
    aDeplacer.value = null
    const m = aParis(nouveau.debut)
    afficherMessage(
      nouveau.statut === 'confirme'
        ? `Rendez-vous déplacé au ${jourCourt(m.jour).slice(0, 5)} à ${heure(m.heure)}.`
        : `Demande envoyée : votre rendez-vous actuel reste valable tant que ${r.autre.nom} n'a pas accepté.`,
    )
    await charger()
  } catch (e) {
    erreurDeplacement.value = messageErreur(e)
  }
}
</script>

<template>
  <AppCarte v-if="chargementFait && !compte" titre="Mes rendez-vous" intro="Connectez-vous pour voir vos rendez-vous.">
    <AppBouton pleine-largeur @click="routeur.push({ path: '/connexion', query: { retour: '/rendez-vous' } })">Se connecter</AppBouton>
  </AppCarte>

  <div v-else-if="compte" class="mx-auto flex w-full max-w-[720px] flex-col gap-4">
    <h1 class="text-[28px] font-bold">Mes rendez-vous</h1>
    <AppOnglets
      v-model="onglet"
      :onglets="[{ id: 'a-venir', texte: 'À venir' }, { id: 'passes', texte: 'Passés et annulés' }]"
    />
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <template v-if="tous">
      <AppSection v-if="onglet === 'a-venir'">
        <template v-if="!avenir.length">
          <p class="text-texte-doux">Aucun rendez-vous pour l'instant.</p>
          <div><AppBouton @click="routeur.push('/trouver')">Trouver un prestataire</AppBouton></div>
        </template>
        <div class="flex flex-col divide-y divide-bord">
          <LigneRendezVous v-for="r in avenir" :key="r.id" :rdv="r" libelle-autre="Avec">
            <template #actions>
              <template v-if="r.statut === 'en_attente'">
                <span class="text-[13.5px] text-texte-doux">
                  {{ r.autre.nom }} doit accepter avant le {{ momentCourt(r.reponse_avant ?? r.debut) }}.
                </span>
                <AppBouton variante="danger" @click="aAnnuler = r">Annuler la demande</AppBouton>
              </template>
              <template v-else-if="dansLeDelai(r)">
                <AppBouton variante="secondaire" @click="(aDeplacer = r), (erreurDeplacement = '')">Déplacer</AppBouton>
                <AppBouton variante="danger" @click="aAnnuler = r">Annuler…</AppBouton>
                <span v-if="r.annulable_jusqu_au" class="text-[13.5px] text-texte-doux">
                  Annulation gratuite jusqu'au {{ momentCourt(r.annulable_jusqu_au) }}.
                </span>
              </template>
              <template v-else>
                <AppBouton variante="verrouille" :raison-verrou="raisonHorsDelai(r)">Déplacer</AppBouton>
                <AppBouton variante="verrouille" :raison-verrou="raisonHorsDelai(r)">Annuler</AppBouton>
              </template>
            </template>
          </LigneRendezVous>
        </div>
      </AppSection>

      <AppSection v-else>
        <p v-if="!passes.length" class="text-texte-doux">Aucun rendez-vous passé ou annulé.</p>
        <div class="flex flex-col divide-y divide-bord">
          <LigneRendezVous v-for="r in passes" :key="r.id" :rdv="r" libelle-autre="Avec" />
        </div>
      </AppSection>
    </template>

    <AppFenetre :ouverte="aAnnuler !== null" :titre="aAnnuler?.statut === 'en_attente' ? 'Annuler la demande ?' : 'Annuler ce rendez-vous ?'" @fermer="aAnnuler = null">
      <template v-if="aAnnuler">
        {{ aAnnuler.titre }} avec {{ aAnnuler.autre.nom }}, {{ plage(aAnnuler).toLowerCase() }}.
        {{ aAnnuler.autre.nom }} est prévenu par mail et l'horaire redevient libre.
      </template>
      <template #pied>
        <AppBouton variante="danger" @click="annuler">{{ aAnnuler?.statut === 'en_attente' ? 'Annuler la demande' : 'Annuler le rendez-vous' }}</AppBouton>
        <AppBouton variante="secondaire" @click="aAnnuler = null">Garder</AppBouton>
      </template>
    </AppFenetre>

    <AppFenetre :ouverte="aDeplacer !== null" :titre="`Déplacer « ${aDeplacer?.titre} »`" @fermer="aDeplacer = null">
      <div v-if="aDeplacer" class="flex flex-col gap-3 text-texte">
        <p class="text-[14px] text-texte-doux">Actuellement : {{ plage(aDeplacer).toLowerCase() }}. Choisissez un nouvel horaire (même prix).</p>
        <ChoixHoraire :annonce-id="aDeplacer.annonce_id" :heures="aDeplacer.heures" @choisir="deplacer" />
        <AppAlerte v-if="erreurDeplacement">{{ erreurDeplacement }}</AppAlerte>
      </div>
      <template #pied>
        <span />
        <AppBouton variante="secondaire" @click="aDeplacer = null">Fermer</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
