<script setup lang="ts">
// Fenêtre « Ajouter un métier » (.doc/ihm/RM-PROFIL-IHM.md, 21/10/2026) : ouverte par la bulle « + Ajouter » de
// « Mon profil ». On cherche un métier, puis [Ajouter Chauffagiste] l'enregistre comme métier secondaire,
// sans passer par tout le formulaire « Modifier mon profil ». 5 métiers secondaires au plus (RM-PRESTATAIRES.md).
import { ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { type MetierVisible, useMetiers } from '../../composables/useMetiers'
import { useMessage } from '../../composables/useMessage'
import { type ProfilPrestataire, SECONDAIRES_MAX } from '../../outils/prestataires'
import { versCentimes } from '../../outils/prix'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppElementChoisi from '../ui/AppElementChoisi.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppRecherche from '../ui/AppRecherche.vue'

const props = defineProps<{ ouverte: boolean; profil: ProfilPrestataire }>()
const emit = defineEmits<{ fermer: []; maj: [profil: ProfilPrestataire] }>()
const { rechercherSauf } = useMetiers()
const { afficherMessage } = useMessage()

const choisi = ref<MetierVisible | null>(null)
// Le prix de l'heure de ce métier (facultatif, schema_v35), ex. « 40 » ou « 45,50 »
const prix = ref('')
const erreur = ref('')
const envoi = ref(false)

const chercher = (texte: string) =>
  rechercherSauf(texte, [props.profil.metier_principal.id, ...props.profil.metiers_secondaires.map((m) => m.id)])

function fermer() {
  choisi.value = null
  prix.value = ''
  erreur.value = ''
  emit('fermer')
}

async function ajouter() {
  if (!choisi.value) return
  const p = props.profil
  erreur.value = ''
  const centimes = versCentimes(prix.value)
  if (prix.value.trim() && (centimes === null || centimes < 100 || centimes > 100_000)) {
    erreur.value = "Le prix de l'heure doit être entre 1 € et 1 000 € (ex. 40 ou 45,50), ou laissez la case vide."
    return
  }
  envoi.value = true
  try {
    // Le reste du profil est renvoyé tel quel (le SIRET n'est revérifié que s'il change)
    const nouveau = await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/modifier', {
      nom_affiche: p.nom_affiche,
      metier_principal_id: p.metier_principal.id,
      metiers_secondaires: [...p.metiers_secondaires.map((m) => m.id), choisi.value.id],
      commune_id: p.commune.id,
      distance_km: p.distance_km,
      lieu: p.lieu,
      presentation: p.presentation,
      siret: p.siret,
    })
    const metierId = choisi.value.id
    const avecPrix = centimes
      ? await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/prix', { metier_id: metierId, prix_centimes: centimes })
      : nouveau
    afficherMessage(`${choisi.value.nom} ajouté à vos métiers.`)
    emit('maj', avecPrix)
    fermer()
  } catch (e) {
    erreur.value = messageErreur(e)
  } finally {
    envoi.value = false
  }
}
</script>

<template>
  <AppFenetre :ouverte="ouverte" titre="Ajouter un métier" @fermer="fermer">
    <p v-if="profil.metiers_secondaires.length >= SECONDAIRES_MAX" class="text-texte-doux">
      Vous avez déjà {{ SECONDAIRES_MAX }} métiers secondaires : c'est le maximum. Arrêtez-en un d'abord (ligne « Mes métiers »).
    </p>
    <template v-else>
      <AppElementChoisi v-if="choisi" :texte="choisi.nom" :detail="choisi.categorie" @changer="choisi = null" />
      <AppRecherche
        v-else
        etiquette="Métier à ajouter"
        :chercher="chercher"
        :libelle="(m: MetierVisible) => m.nom"
        :detail="(m: MetierVisible) => m.categorie"
        :cle="(m: MetierVisible) => m.id"
        placeholder="Tapez les premières lettres, ex. « chauf »…"
        aide="Vous apparaîtrez aussi dans les recherches de ce métier, après les spécialistes."
        @choisir="(m: MetierVisible) => (choisi = m)"
      />
      <AppChamp v-model="prix" etiquette="Votre prix de l’heure (€), facultatif" inputmode="decimal" placeholder="Ex. 40" aide="Montré sur votre carte dans « Trouver » : « 40 €/h »." />
      <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
    </template>
    <template #pied>
      <AppBouton v-if="choisi" :occupe="envoi" @click="ajouter">Ajouter {{ choisi.nom }}</AppBouton>
      <AppBouton v-else-if="profil.metiers_secondaires.length < SECONDAIRES_MAX" variante="verrouille" raison-verrou="Choisissez d'abord un métier dans la liste.">
        Ajouter ce métier
      </AppBouton>
      <AppBouton variante="secondaire" @click="fermer">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
