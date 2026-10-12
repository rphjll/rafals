<script setup lang="ts">
// Mon profil › « Particulier, non professionnel » (.doc/ihm/RM-PROFIL-IHM.md ; RM-PRESTATAIRES.md § « Limites d'un
// prestataire sans SIRET ») : affichée seulement sans SIRET vérifié. Ses limites, où il en est, la case à cocher,
// et le chemin pour ne plus en avoir (créer son auto-entreprise).
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { formaterDate } from '../../outils/dates'
import { montant } from '../../outils/paiements'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppCase from '../ui/AppCase.vue'
import AppSection from '../ui/AppSection.vue'

interface Limites {
  particulier: boolean
  etiquette: string
  avertissement: string
  texte_case: string
  adresse_remplie: boolean
  case_cochee_le: string | null
  prix_max_centimes: number
  rendez_vous_ce_mois: number
  rendez_vous_par_mois: number
  total_12_mois_centimes: number
  total_max_centimes: number
  plafond_atteint: boolean
}

const routeur = useRouter()
const { afficherMessage } = useMessage()
const limites = ref<Limites | null>(null)
const coche = ref(false)
const occupe = ref(false)

onMounted(async () => {
  limites.value = await appelerServeur<Limites>('/api/moi/prestataire/limites').catch(() => null)
})

async function declarer() {
  if (!coche.value) return
  occupe.value = true
  try {
    limites.value = await appelerServeur<Limites>('/api/moi/prestataire/activite-occasionnelle', {})
    afficherMessage('C’est noté : vous pouvez répondre aux demandes.')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  } finally {
    occupe.value = false
  }
}
</script>

<template>
  <AppSection v-if="limites?.particulier" titre="Sans SIRET : vos limites">
    <div class="flex flex-col gap-3">
      <div><AppBadge etat="attente">{{ limites.etiquette }}</AppBadge></div>
      <p class="text-texte-doux">
        Sans SIRET vérifié, vous rendez de petits services, payés en espèces. Vos clients lisent cette étiquette sur votre
        profil et sur vos propositions, avec l'avertissement « {{ limites.avertissement }} »
      </p>
      <ul class="flex flex-col gap-1.5">
        <li>Seulement les métiers autorisés sans SIRET (ex. promener un chien, repasser, tondre une pelouse).</li>
        <li>
          <b>{{ montant(limites.prix_max_centimes) }}</b> au plus par proposition.
        </li>
        <li>
          <b>{{ limites.rendez_vous_ce_mois }} sur {{ limites.rendez_vous_par_mois }}</b> rendez-vous ce mois-ci.
        </li>
        <li>
          <b>{{ montant(limites.total_12_mois_centimes) }} sur {{ montant(limites.total_max_centimes) }}</b> de rendez-vous
          sur les 12 derniers mois.
        </li>
      </ul>
      <AppAlerte v-if="limites.plafond_atteint">
        Vous avez atteint la limite des particuliers : vous ne pouvez plus répondre aux demandes tant que vous n'avez pas de SIRET.
      </AppAlerte>

      <template v-if="limites.case_cochee_le">
        <p class="text-[14px] text-texte-doux">
          ✓ « {{ limites.texte_case }} » : déclaré le {{ formaterDate(limites.case_cochee_le) }}.
        </p>
      </template>
      <template v-else>
        <AppCase v-model="coche" :texte="limites.texte_case" />
        <div>
          <AppBouton v-if="coche" :occupe="occupe" @click="declarer">Enregistrer ma déclaration</AppBouton>
          <AppBouton v-else variante="verrouille" raison-verrou="Cochez d’abord la case : sans elle, vous ne pouvez pas répondre aux demandes.">
            Enregistrer ma déclaration
          </AppBouton>
        </div>
      </template>
      <AppAlerte v-if="!limites.adresse_remplie" etat="attente">
        Indiquez aussi votre adresse, plus bas : elle n'est pas montrée au public, mais rafals doit la connaître.
      </AppAlerte>

      <p class="text-texte-doux">Avec un SIRET vérifié, aucune de ces limites : tous les métiers, tous les prix, la carte bancaire et les devis.</p>
      <div><AppBouton variante="secondaire" @click="routeur.push('/creer-mon-auto-entreprise')">Créer mon auto-entreprise</AppBouton></div>
    </div>
  </AppSection>
</template>
