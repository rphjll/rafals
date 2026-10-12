<script setup lang="ts">
// Administration › Métiers (.doc/ihm/RM-ADMINISTRATION-IHM.md). Règles : RM-METIERS.md.
// Un métier ne se supprime jamais : on le désactive.
import { computed, onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { useMetiers } from '../../composables/useMetiers'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppCase from '../ui/AppCase.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSelection from '../ui/AppSelection.vue'

interface MetierComplet {
  id: number
  nom: string
  categorie_id: number
  mots_cles: string[]
  est_active: boolean
}
interface DossierAdmin {
  id: number
  nom: string
}

const { afficherMessage } = useMessage()
const { chargerDossiers } = useMetiers()
const metiers = ref<MetierComplet[]>([])
const dossiersAdmin = ref<DossierAdmin[]>([])
const filtre = ref('')
const erreur = ref('')

const sansAccents = (texte: string) => texte.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
const nomDossier = (id: number) => dossiersAdmin.value.find((d) => d.id === id)?.nom ?? ''
const optionsDossiers = computed(() => dossiersAdmin.value.map((d) => ({ valeur: d.id, texte: d.nom })))
// Les métiers désactivés sont cachés, sauf si l'on coche « Montrer les désactivés »
const montrerDesactives = ref(false)
const metiersFiltres = computed(() => {
  const q = sansAccents(filtre.value.trim())
  return metiers.value.filter(
    (m) =>
      (montrerDesactives.value || m.est_active) &&
      (!q || sansAccents(`${m.nom} ${m.mots_cles.join(' ')}`).includes(q)),
  )
})

async function charger() {
  try {
    dossiersAdmin.value = await appelerServeur<DossierAdmin[]>('/api/admin/dossiers')
    metiers.value = await appelerServeur<MetierComplet[]>('/api/admin/metiers')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)

// Une seule fenêtre pour créer ou modifier
const fiche = ref<{ id: number | null; nom: string; categorie_id: number | null; mots_cles: string; est_active: boolean } | null>(null)
const erreurFenetre = ref('')

function nouveau() {
  fiche.value = { id: null, nom: '', categorie_id: null, mots_cles: '', est_active: true }
  erreurFenetre.value = ''
}

function modifier(metier: MetierComplet) {
  fiche.value = { ...metier, mots_cles: metier.mots_cles.join(', ') }
  erreurFenetre.value = ''
}

// Désactiver : le métier disparaît pour tout le monde (recherche, dossiers, profils) ; réversible
async function basculer(metier: MetierComplet) {
  try {
    await appelerServeur(`/api/admin/metiers/${metier.id}`, {
      nom: metier.nom,
      categorie_id: metier.categorie_id,
      mots_cles: metier.mots_cles,
      est_active: !metier.est_active,
    })
    afficherMessage(
      metier.est_active
        ? `« ${metier.nom} » désactivé : il n'est plus proposé.`
        : `« ${metier.nom} » réactivé : il est de nouveau proposé.`,
    )
    await charger()
    await chargerDossiers(true)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

async function enregistrer() {
  const f = fiche.value
  if (!f) return
  try {
    if (f.id === null) {
      await appelerServeur('/api/admin/metiers', { nom: f.nom, categorie_id: f.categorie_id })
    } else {
      await appelerServeur(`/api/admin/metiers/${f.id}`, {
        nom: f.nom,
        categorie_id: f.categorie_id,
        mots_cles: f.mots_cles.split(','),
        est_active: f.est_active,
      })
    }
    fiche.value = null
    afficherMessage(f.id === null ? `Métier « ${f.nom} » créé.` : `Métier « ${f.nom} » enregistré.`)
    await charger()
    await chargerDossiers(true)
  } catch (e) {
    erreurFenetre.value = messageErreur(e)
  }
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div class="flex flex-wrap items-end gap-2.5">
      <div class="min-w-[220px] flex-1"><AppChamp v-model="filtre" etiquette="Filtrer" placeholder="ex. plom" /></div>
      <AppCase v-model="montrerDesactives" texte="Montrer les désactivés" />
      <AppBouton @click="nouveau">+ Nouveau métier</AppBouton>
    </div>
    <div class="overflow-x-auto carte">
      <table class="w-full min-w-[760px] border-collapse text-sm">
        <thead>
          <tr class="text-left text-xs tracking-wide text-texte-doux uppercase">
            <th class="border-b border-bord px-3 py-2.5">Métier</th>
            <th class="border-b border-bord px-3 py-2.5">Dossier</th>
            <th class="border-b border-bord px-3 py-2.5">Mots-clés</th>
            <th class="border-b border-bord px-3 py-2.5">État</th>
            <th class="border-b border-bord px-3 py-2.5"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="metier in metiersFiltres" :key="metier.id" class="border-b border-bord last:border-0">
            <td class="px-3 py-2.5">{{ metier.nom }}</td>
            <td class="px-3 py-2.5">{{ nomDossier(metier.categorie_id) }}</td>
            <td class="px-3 py-2.5 text-[13px] text-texte-doux">{{ metier.mots_cles.join(', ') }}</td>
            <td class="px-3 py-2.5">
              <AppBadge :etat="metier.est_active ? 'ok' : 'neutre'">{{ metier.est_active ? 'actif' : 'désactivé' }}</AppBadge>
            </td>
            <td class="px-3 py-2.5 text-right">
              <span class="inline-flex flex-wrap justify-end gap-2">
                <AppBouton variante="secondaire" @click="modifier(metier)">Modifier</AppBouton>
                <AppBouton :variante="metier.est_active ? 'danger' : 'secondaire'" @click="basculer(metier)">
                  {{ metier.est_active ? 'Désactiver' : 'Réactiver' }}
                </AppBouton>
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="text-[13px] text-texte-doux">
      {{ metiersFiltres.length }} métier(s) affiché(s) sur {{ metiers.length }}, triés par nom. Un métier ne se supprime
      jamais : on le désactive (il disparaît pour tout le monde, et d'ici tant que « Montrer les désactivés » n'est pas coché).
    </p>

    <AppFenetre
      :ouverte="fiche !== null"
      :titre="fiche?.id === null ? 'Nouveau métier' : `Modifier « ${fiche?.nom} »`"
      @fermer="fiche = null"
    >
      <div v-if="fiche" class="flex flex-col gap-3">
        <AppChamp v-model="fiche.nom" etiquette="Nom" obligatoire placeholder="ex. Cordiste" />
        <AppSelection v-model="fiche.categorie_id" etiquette="Dossier" :options="optionsDossiers" obligatoire />
        <AppChamp v-if="fiche.id !== null" v-model="fiche.mots_cles" etiquette="Mots-clés (séparés par des virgules)" />
        <AppAlerte v-if="erreurFenetre">{{ erreurFenetre }}</AppAlerte>
      </div>
      <template #pied>
        <AppBouton @click="enregistrer">{{ fiche?.id === null ? 'Créer' : 'Enregistrer' }}</AppBouton>
        <AppBouton variante="secondaire" @click="fiche = null">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
