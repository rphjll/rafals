<script setup lang="ts">
// Mon agenda › Rendez-vous (.doc/ihm/RM-RENDEZ-VOUS-IHM.md) : demandes à accepter, rendez-vous à venir, puis passés.
import { computed, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { type RendezVousVisible, absenceSignalable, aVenir, contestable, momentCourt, plage } from '../../outils/rendez_vous'
import FenetreTexte, { type DemandeTexte } from '../FenetreTexte.vue'
import AvisAffiche from '../avis/AvisAffiche.vue'
import LigneRendezVous from '../rendez-vous/LigneRendezVous.vue'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSection from '../ui/AppSection.vue'

const props = defineProps<{ rendezVous: RendezVousVisible[] }>()
const emit = defineEmits<{ maj: [] }>()
const { afficherMessage } = useMessage()

const demandes = computed(() => props.rendezVous.filter((r) => r.statut === 'en_attente' && aVenir(r)).sort((a, b) => a.debut.localeCompare(b.debut)))
const confirmes = computed(() => props.rendezVous.filter((r) => r.statut === 'confirme' && aVenir(r)).sort((a, b) => a.debut.localeCompare(b.debut)))
const passes = computed(() => props.rendezVous.filter((r) => !aVenir(r)))

async function accepter(r: RendezVousVisible) {
  try {
    await appelerServeur(`/api/moi/prestataire/rendez-vous/${r.id}/accepter`, {})
    afficherMessage(`Rendez-vous accepté : ${r.autre.nom} est prévenu.`)
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

// Absences (lot 4.6) : « Client absent » après l'heure ; « Je suis venu » si le client l'a signalé absent
const aContester = ref<DemandeTexte | null>(null)
// [Je suis venu…] : la fenêtre commune à un seul texte
const contester = (chemin: string): DemandeTexte => ({
  titre: "Contester l'absence",
  explication: "Expliquez ce qui s'est passé : l'administrateur de rafals lira les deux versions et tranchera. En attendant, rien n'est compté ni affiché.",
  etiquette: "Ce qui s'est passé", aide: "ex. « Je suis venu à 10 h, personne n'a ouvert, j'ai appelé 2 fois. »",
  chemin, cle: 'explication', bouton: 'Envoyer', reussite: 'Contestation envoyée : rafals va trancher.',
})
async function clientAbsent(r: RendezVousVisible) {
  try {
    await appelerServeur(`/api/moi/prestataire/rendez-vous/${r.id}/absent`, {})
    afficherMessage(`Absence signalée : ${r.autre.nom} a 7 jours pour contester.`)
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

// Avis reçus (lot 4.8) : une seule réponse publique ; un signalement à l'administrateur
const aEcrire = ref<DemandeTexte | null>(null)
const repondre = (avisId: number, auteur: string): DemandeTexte => ({
  titre: `Répondre à ${auteur}`, explication: "Votre réponse sera affichée sous l'avis, pour tous. Une seule réponse ; la note ne change pas.",
  etiquette: 'Votre réponse', aide: 'ex. « Bouchon sur la rocade, j\'avais prévenu par SMS. »',
  chemin: `/api/moi/prestataire/avis/${avisId}/repondre`, cle: 'texte', bouton: 'Publier ma réponse', reussite: 'Réponse publiée.',
})
const signaler = (avisId: number): DemandeTexte => ({
  titre: 'Signaler cet avis ?', explication: "L'administrateur de rafals le lira ; l'avis reste affiché en attendant.",
  etiquette: 'Pourquoi ?', aide: 'ex. « Fausse accusation », « Contient mon numéro de téléphone »',
  chemin: `/api/moi/prestataire/avis/${avisId}/signaler`, cle: 'texte', bouton: 'Signaler', danger: true,
  reussite: "Avis signalé : l'administrateur va le regarder.",
})

// Refuser (motif facultatif) ou annuler (motif obligatoire) : la même fenêtre
const cible = ref<{ rdv: RendezVousVisible; action: 'refuser' | 'annuler' } | null>(null)
const motif = ref('')
const erreur = ref('')
function ouvrir(rdv: RendezVousVisible, action: 'refuser' | 'annuler') {
  cible.value = { rdv, action }
  motif.value = ''
  erreur.value = ''
}
async function confirmer() {
  const c = cible.value
  if (!c) return
  erreur.value = ''
  try {
    await appelerServeur(`/api/moi/prestataire/rendez-vous/${c.rdv.id}/${c.action}`, { motif: motif.value })
    cible.value = null
    afficherMessage(
      c.action === 'refuser'
        ? "Demande refusée : l'horaire est de nouveau libre."
        : `Rendez-vous annulé : ${c.rdv.autre.nom} est prévenu.`,
    )
    emit('maj')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
const moinsDe24h = computed(() => !!cible.value && new Date(cible.value.rdv.debut).getTime() - Date.now() < 24 * 3600 * 1000)
</script>

<template>
  <AppSection v-if="demandes.length" titre="Demandes à accepter">
    <div class="flex flex-col divide-y divide-bord">
      <LigneRendezVous v-for="r in demandes" :key="r.id" :rdv="r" libelle-autre="Client">
        <template #actions>
          <AppBouton @click="accepter(r)">Accepter</AppBouton>
          <AppBouton variante="secondaire" @click="ouvrir(r, 'refuser')">Refuser…</AppBouton>
          <span class="text-[13.5px] text-texte-doux">Répondez avant le {{ momentCourt(r.reponse_avant ?? r.debut) }}.</span>
        </template>
      </LigneRendezVous>
    </div>
  </AppSection>

  <AppSection titre="À venir">
    <p v-if="!confirmes.length" class="text-texte-doux">Aucun rendez-vous à venir.</p>
    <div class="flex flex-col divide-y divide-bord">
      <LigneRendezVous v-for="r in confirmes" :key="r.id" :rdv="r" libelle-autre="Client">
        <template #actions>
          <AppBouton variante="danger" @click="ouvrir(r, 'annuler')">Annuler…</AppBouton>
        </template>
      </LigneRendezVous>
    </div>
  </AppSection>

  <details v-if="passes.length" class="rounded-rafals border border-bord bg-surface p-5" :open="passes.some((r) => absenceSignalable(r) || contestable(r.absence, 'prestataire') || (r.avis && !r.avis.reponse))">
    <summary class="min-h-[28px] cursor-pointer font-bold">Passés et annulés ({{ passes.length }})</summary>
    <div class="flex flex-col divide-y divide-bord">
      <LigneRendezVous v-for="r in passes" :key="r.id" :rdv="r" libelle-autre="Client">
        <template #actions>
          <div v-if="r.avis" class="w-full rounded-rafals bg-fond p-3">
            <AvisAffiche :avis="r.avis" :titre="`Avis de ${r.avis.auteur}`" nom-prestataire="vous">
              <template #actions>
                <AppBouton v-if="!r.avis.reponse && !r.avis.cache_motif" variante="secondaire" @click="aEcrire = repondre(r.avis.id, r.avis.auteur)">
                  Répondre…
                </AppBouton>
                <AppBouton v-if="!r.avis.signale && !r.avis.cache_motif" variante="danger" @click="aEcrire = signaler(r.avis.id)">
                  Signaler…
                </AppBouton>
              </template>
            </AvisAffiche>
          </div>
          <AppBouton v-if="absenceSignalable(r)" variante="danger" @click="clientAbsent(r)">Client absent</AppBouton>
          <AppBouton
            v-if="contestable(r.absence, 'prestataire')"
            variante="secondaire"
            @click="aContester = contester(`/api/moi/prestataire/rendez-vous/${r.id}/contester`)"
          >
            Je suis venu…
          </AppBouton>
        </template>
      </LigneRendezVous>
    </div>
  </details>

  <AppFenetre
    :ouverte="cible !== null"
    :titre="cible?.action === 'refuser' ? `Refuser la demande de ${cible?.rdv.autre.nom} ?` : `Annuler le rendez-vous de ${cible?.rdv.autre.nom} ?`"
    @fermer="cible = null"
  >
    <form v-if="cible" class="flex flex-col gap-3 text-texte" @submit.prevent="confirmer">
      <p class="text-[14px] text-texte-doux">{{ cible.rdv.titre }}, {{ plage(cible.rdv).toLowerCase() }}.</p>
      <AppChamp
        v-model="motif"
        :etiquette="cible.action === 'refuser' ? 'Motif (facultatif, envoyé au client)' : 'Motif (envoyé au client)'"
        :obligatoire="cible.action === 'annuler'"
        :placeholder="cible.action === 'refuser' ? 'ex. Déjà pris ce jour-là' : 'ex. Malade, désolée'"
      />
      <p v-if="cible.action === 'annuler' && moinsDe24h" class="text-[13.5px] text-attente">
        À moins de 24 h, l'annulation est comptée et visible par l'administrateur.
      </p>
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </form>
    <template #pied>
      <AppBouton variante="danger" @click="confirmer">{{ cible?.action === 'refuser' ? 'Refuser' : 'Annuler le rendez-vous' }}</AppBouton>
      <AppBouton variante="secondaire" @click="cible = null">{{ cible?.action === 'refuser' ? 'Revenir' : 'Garder' }}</AppBouton>
    </template>
  </AppFenetre>
  <FenetreTexte :demande="aContester" @fermer="aContester = null" @fait="(aContester = null), emit('maj')" />
  <FenetreTexte :demande="aEcrire" @fermer="aEcrire = null" @fait="(aEcrire = null), emit('maj')" />
</template>
