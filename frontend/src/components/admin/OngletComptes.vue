<script setup lang="ts">
// Administration › Comptes (.doc/ihm/RM-ADMINISTRATION-IHM.md).
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte } from '../../composables/useCompte'
import { useMessage } from '../../composables/useMessage'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'

interface CompteAdministre {
  id: number
  email: string
  prenom: string
  nom: string
  email_verifie: boolean
  est_administrateur: boolean
  ferme: boolean
}

const { chargerCompte } = useCompte()
const { afficherMessage } = useMessage()
const comptes = ref<CompteAdministre[]>([])
const erreur = ref('')

async function charger() {
  try {
    comptes.value = await appelerServeur<CompteAdministre[]>('/api/admin/comptes')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)

const cible = ref<CompteAdministre | null>(null)
const erreurFenetre = ref('')

function ouvrir(compte: CompteAdministre) {
  cible.value = compte
  erreurFenetre.value = ''
}

async function changerRole() {
  const compte = cible.value
  if (!compte) return
  const nommer = !compte.est_administrateur
  try {
    await appelerServeur(`/api/admin/comptes/${compte.id}/administrateur`, { est_administrateur: nommer })
    cible.value = null
    afficherMessage(`${compte.prenom} ${compte.nom} ${nommer ? 'est administrateur' : "n'est plus administrateur"}.`)
    await chargerCompte() // si l'on s'est retiré son propre rôle, le menu change
    await charger()
  } catch (e) {
    erreurFenetre.value = messageErreur(e)
  }
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    <div class="overflow-x-auto carte">
      <table class="w-full min-w-[640px] border-collapse text-sm">
        <thead>
          <tr class="text-left text-xs tracking-wide text-texte-doux uppercase">
            <th class="border-b border-bord px-3 py-2.5">Nom</th>
            <th class="border-b border-bord px-3 py-2.5">Adresse mail</th>
            <th class="border-b border-bord px-3 py-2.5">Adresse</th>
            <th class="border-b border-bord px-3 py-2.5">Rôle</th>
            <th class="border-b border-bord px-3 py-2.5"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ligne in comptes" :key="ligne.id" class="border-b border-bord last:border-0">
            <td class="px-3 py-2.5">{{ ligne.nom }} {{ ligne.prenom }}</td>
            <td class="px-3 py-2.5">{{ ligne.email }}</td>
            <td class="px-3 py-2.5">
              <AppBadge :etat="ligne.email_verifie ? 'ok' : 'attente'">{{ ligne.email_verifie ? 'vérifiée' : 'non vérifiée' }}</AppBadge>
            </td>
            <td class="px-3 py-2.5">
              <AppBadge v-if="ligne.ferme" etat="neutre">fermé</AppBadge>
              <AppBadge v-else-if="ligne.est_administrateur" etat="ok">administrateur</AppBadge>
            </td>
            <td class="px-3 py-2.5 text-right">
              <AppBouton
                v-if="!ligne.ferme"
                :variante="ligne.est_administrateur ? 'danger' : 'secondaire'"
                @click="ouvrir(ligne)"
              >
                {{ ligne.est_administrateur ? 'Retirer le rôle' : 'Nommer administrateur' }}
              </AppBouton>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AppFenetre
      :ouverte="cible !== null"
      :titre="
        cible?.est_administrateur
          ? `Retirer le rôle d'administrateur à ${cible?.prenom} ${cible?.nom} ?`
          : `Nommer ${cible?.prenom} ${cible?.nom} administrateur ?`
      "
      @fermer="cible = null"
    >
      <div class="flex flex-col gap-3">
        <p v-if="cible?.est_administrateur">Il ou elle garde son compte, sans l'écran Administration.</p>
        <p v-else>Tous les droits : voir tous les comptes, vérifier les accords, nommer d'autres administrateurs.</p>
        <AppAlerte v-if="erreurFenetre">{{ erreurFenetre }}</AppAlerte>
      </div>
      <template #pied>
        <AppBouton :variante="cible?.est_administrateur ? 'danger' : 'principal'" @click="changerRole">
          {{ cible?.est_administrateur ? 'Retirer' : 'Nommer' }}
        </AppBouton>
        <AppBouton variante="secondaire" @click="cible = null">Annuler</AppBouton>
      </template>
    </AppFenetre>
  </div>
</template>
