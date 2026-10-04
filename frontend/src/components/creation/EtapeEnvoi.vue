<script setup lang="ts">
// Étape 5 « Vérifier et envoyer » du dossier de création d'auto-entreprise (.doc/ihm/RM-CREATION-AUTO-ENTREPRISE-IHM.md) :
// le récapitulatif, les 2 cases (je certifie, je donne pouvoir à rafals) et l'envoi au guichet de l'État.
import { computed, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { jourCourt } from '../../outils/agenda'
import { CHEMIN, type DossierCreation, envoyerEtape, type Situation, SITUATIONS } from '../../outils/creation'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppCase from '../ui/AppCase.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSection from '../ui/AppSection.vue'

const props = defineProps<{ dossier: DossierCreation }>()
const emit = defineEmits<{ enregistre: [situation: Situation]; aller: [etape: number]; retour: [] }>()
const { afficherMessage } = useMessage()

const certifie = ref(false)
const pouvoir = ref(false)
const erreur = ref('')
const envoiEnCours = ref(false)
const textePouvoir = ref('')
const fenetrePouvoir = ref(false)

const d = computed(() => props.dossier)
const manquants = computed(() => Object.values(d.value.manque).flat())
const lieux = { chez_clients: 'chez mes clients', chez_moi: 'chez moi', local: 'dans un local' }
const lignes = computed(() => [
  {
    nom: 'Vous',
    etape: 1,
    texte: d.value.nom_naissance
      ? `${d.value.civilite === 'madame' ? 'Mme' : 'M.'} ${d.value.prenoms?.replace(/,/g, '')} ${d.value.nom_naissance}, né(e) le ${d.value.naissance_le ? jourCourt(d.value.naissance_le) : '…'} à ${d.value.naissance_commune?.nom ?? d.value.naissance_pays ?? '…'} · ${SITUATIONS.find((s) => s.cle === d.value.situation_famille)?.texte.toLowerCase() ?? '…'}`
      : 'à remplir',
  },
  { nom: 'Adresse', etape: 1, texte: d.value.adresse_rue ? `${d.value.adresse_rue}, ${d.value.code_postal} ${d.value.commune?.nom}` : 'à remplir' },
  {
    nom: 'Activité',
    etape: 2,
    texte: d.value.description
      ? `${d.value.metier} · « ${d.value.description} » · à partir du ${d.value.debut_le ? jourCourt(d.value.debut_le) : '…'} · ${d.value.lieu_travail ? lieux[d.value.lieu_travail] : ''}`
      : 'à remplir',
  },
  {
    nom: 'Choix',
    etape: 3,
    texte: d.value.periodicite
      ? `URSSAF chaque ${d.value.periodicite} · ${d.value.impot_avec_cotisations ? 'impôt payé avec les cotisations' : 'impôt à part'} · ${d.value.acre_demandee ? 'ACRE demandée' : 'pas d\'ACRE'} · ${d.value.adresse_non_publique ? 'adresse non publique' : 'adresse publique'}`
      : 'à remplir',
  },
  {
    nom: 'Papiers',
    etape: 4,
    texte: [...d.value.pieces.filter((p) => p.depose_le).map((p) => p.nom.replace(/^(la |le |l')/, '')), 'attestation sur l\'honneur'].join(', '),
  },
])

async function lirePouvoir() {
  try {
    textePouvoir.value = (await appelerServeur<{ texte: string }>(`${CHEMIN}/pouvoir`)).texte
    fenetrePouvoir.value = true
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}

async function envoyer() {
  erreur.value = ''
  envoiEnCours.value = true
  try {
    const situation = await envoyerEtape('/envoi', { certifie: certifie.value, pouvoir: pouvoir.value })
    afficherMessage(d.value.demonstration ? 'Dossier envoyé (démonstration).' : "Dossier envoyé au guichet de l'État.")
    emit('enregistre', situation)
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoiEnCours.value = false
  }
}
</script>

<template>
  <AppSection titre="Vérifier et envoyer">
    <dl class="grid grid-cols-[auto_1fr] gap-x-3.5 gap-y-2 text-[14px]">
      <template v-for="ligne in lignes" :key="ligne.nom">
        <dt class="text-texte-doux">{{ ligne.nom }}</dt>
        <dd>
          {{ ligne.texte }} ·
          <button type="button" class="font-semibold text-primaire underline" @click="emit('aller', ligne.etape)">modifier</button>
        </dd>
      </template>
    </dl>
    <AppAlerte v-if="dossier.demonstration" etat="attente">
      Mode démonstration : rafals n'est pas encore branché au guichet de l'État. Rien n'est envoyé, aucune entreprise n'est créée.
    </AppAlerte>
    <AppCase v-model="certifie" texte="Je certifie que ces informations sont exactes, et je signe l'attestation sur l'honneur." />
    <div>
      <AppCase v-model="pouvoir" texte="Je donne pouvoir à rafals pour déposer ce dossier de création d'entreprise en mon nom auprès du guichet des formalités des entreprises." />
      <button v-if="!manquants.length" type="button" class="min-h-[36px] text-[14px] font-semibold text-primaire underline" @click="lirePouvoir">
        Lire le pouvoir
      </button>
    </div>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div class="flex flex-wrap justify-between gap-2">
      <AppBouton variante="secondaire" @click="emit('retour')">Retour</AppBouton>
      <AppBouton v-if="manquants.length" variante="verrouille" :raison-verrou="`Il manque : ${manquants.join(', ')}.`">Envoyer mon dossier</AppBouton>
      <AppBouton v-else-if="!certifie || !pouvoir" variante="verrouille" raison-verrou="Cochez les deux cases pour envoyer.">Envoyer mon dossier</AppBouton>
      <AppBouton v-else :occupe="envoiEnCours" @click="envoyer">Envoyer mon dossier</AppBouton>
    </div>
    <p class="text-[13px] text-texte-doux">Une fois envoyé, plus rien ne se modifie, sauf si l'administration demande une correction.</p>

    <AppFenetre :ouverte="fenetrePouvoir" titre="Pouvoir donné à rafals" @fermer="fenetrePouvoir = false">
      <p>{{ textePouvoir }}</p>
      <p class="text-[13.5px] text-texte-doux">Il est joint au dossier envoyé.</p>
      <template #pied><AppBouton @click="fenetrePouvoir = false">Fermer</AppBouton></template>
    </AppFenetre>
  </AppSection>
</template>
