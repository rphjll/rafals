<script setup lang="ts">
// Administration › Prestataires (.doc/ihm/RM-ADMINISTRATION-IHM.md). Règles : RM-PRESTATAIRES.md.
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { badgeSiret, badgeStatut } from '../../outils/prestataires'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'

interface PrestataireAdministre {
  id: number
  nom_affiche: string
  metier_principal: string
  commune: string
  siret_statut: string
  statut: string
  email_compte: string
}

const { afficherMessage } = useMessage()
const prestataires = ref<PrestataireAdministre[]>([])
const erreur = ref('')

async function charger() {
  try {
    prestataires.value = await appelerServeur<PrestataireAdministre[]>('/api/admin/prestataires')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)

async function agir(adresse: string, donnees: unknown, message: string) {
  try {
    await appelerServeur(adresse, donnees)
    afficherMessage(message)
    await charger()
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

const aBloquer = ref<PrestataireAdministre | null>(null)
async function bloquer() {
  const p = aBloquer.value
  if (!p) return
  aBloquer.value = null
  await agir(`/api/admin/prestataires/${p.id}/blocage`, { bloque: true }, `« ${p.nom_affiche} » est bloqué.`)
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <p v-if="!prestataires.length" class="text-texte-doux">Aucun prestataire pour l'instant.</p>
    <div v-else class="overflow-x-auto rounded-rafals border border-bord bg-surface">
      <table class="w-full min-w-[860px] border-collapse text-sm">
        <thead>
          <tr class="text-left text-xs tracking-wide text-texte-doux uppercase">
            <th class="border-b border-bord px-3 py-2.5">Prestataire</th>
            <th class="border-b border-bord px-3 py-2.5">Métier</th>
            <th class="border-b border-bord px-3 py-2.5">Ville</th>
            <th class="border-b border-bord px-3 py-2.5">SIRET</th>
            <th class="border-b border-bord px-3 py-2.5">État</th>
            <th class="border-b border-bord px-3 py-2.5">Compte</th>
            <th class="border-b border-bord px-3 py-2.5"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in prestataires" :key="p.id" class="border-b border-bord last:border-0">
            <td class="px-3 py-2.5">{{ p.nom_affiche }}</td>
            <td class="px-3 py-2.5">{{ p.metier_principal }}</td>
            <td class="px-3 py-2.5">{{ p.commune }}</td>
            <td class="px-3 py-2.5"><AppBadge :etat="badgeSiret(p.siret_statut).etat">{{ badgeSiret(p.siret_statut).texte }}</AppBadge></td>
            <td class="px-3 py-2.5"><AppBadge :etat="badgeStatut(p.statut).etat">{{ badgeStatut(p.statut).texte }}</AppBadge></td>
            <td class="px-3 py-2.5">{{ p.email_compte }}</td>
            <td class="px-3 py-2.5">
              <span class="inline-flex flex-wrap justify-end gap-2">
                <AppBouton
                  v-if="p.siret_statut === 'a_verifier' || p.siret_statut === 'refuse'"
                  variante="secondaire"
                  @click="agir(`/api/admin/prestataires/${p.id}/siret-valide`, {}, `SIRET de « ${p.nom_affiche} » validé à la main.`)"
                >
                  Valider le SIRET
                </AppBouton>
                <AppBouton
                  v-if="p.statut === 'bloque'"
                  variante="secondaire"
                  @click="agir(`/api/admin/prestataires/${p.id}/blocage`, { bloque: false }, `« ${p.nom_affiche} » est débloqué : il est de nouveau actif.`)"
                >
                  Débloquer
                </AppBouton>
                <AppBouton v-else-if="p.statut !== 'arrete'" variante="danger" @click="aBloquer = p">Bloquer…</AppBouton>
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="text-[13px] text-texte-doux">
      Du plus récent au plus ancien. « Valider le SIRET » : seulement après avoir vu un justificatif (avis de situation INSEE).
    </p>

    <AppFenetre :ouverte="aBloquer !== null" :titre="`Bloquer « ${aBloquer?.nom_affiche} » ?`" @fermer="aBloquer = null">
      Il disparaît des recherches et ne peut plus rien changer. Vous seul pourrez le débloquer.
      <template #pied>
        <AppBouton variante="danger" @click="bloquer">Bloquer</AppBouton>
        <AppBouton variante="secondaire" @click="aBloquer = null">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
