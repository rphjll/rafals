<script setup lang="ts">
// [S'abonner] / [Abonné ✓] (.doc/regles-metier/RM-ABONNEMENTS.md) : le même bouton sur les cartes de « Trouver un
// prestataire » (petit) et sur la page publique. Pas connecté : connexion, puis retour ici. Un 2e clic se désabonne.
// Absent sur son propre profil (c'est à la page qui l'affiche de ne pas le montrer).
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte } from '../../composables/useCompte'
import { useMessage } from '../../composables/useMessage'
import { type EtatAbonnement, cheminAbonnement } from '../../outils/abonnements'

const props = withDefaults(defineProps<{ prestataireId: number; nom: string; abonne: boolean; petit?: boolean }>(), { petit: false })
const emit = defineEmits<{ change: [etat: EtatAbonnement] }>()
const route = useRoute()
const routeur = useRouter()
const { compte } = useCompte()
const { afficherMessage } = useMessage()
const occupe = ref(false)

async function basculer() {
  if (!compte.value) {
    afficherMessage(`Connectez-vous pour suivre ${props.nom} : vous reviendrez ici.`)
    routeur.push({ path: '/connexion', query: { retour: route.fullPath } })
    return
  }
  occupe.value = true
  try {
    const etat = await appelerServeur<EtatAbonnement>(cheminAbonnement(props.prestataireId, props.abonne), {})
    emit('change', etat)
    afficherMessage(etat.abonne ? `Vous suivez ${props.nom}` : `Vous ne suivez plus ${props.nom}`)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  } finally {
    occupe.value = false
  }
}
</script>

<template>
  <button
    type="button"
    class="relative z-10 rounded-bouton font-extrabold whitespace-nowrap"
    :class="[
      abonne ? 'bg-primaire-doux text-primaire' : 'bg-primaire text-primaire-texte',
      petit ? 'min-h-9 px-3.5 text-[13.5px]' : 'min-h-[42px] px-[18px]',
      occupe ? 'cursor-wait opacity-70' : 'cursor-pointer',
    ]"
    :aria-pressed="abonne"
    :disabled="occupe"
    @click.stop.prevent="basculer"
  >
    {{ abonne ? 'Abonné ✓' : "S'abonner" }}
  </button>
</template>
