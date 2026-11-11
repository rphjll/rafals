<script setup lang="ts">
// Mon profil › Mes métiers (.doc/ihm/RM-PROFIL-IHM.md ; RM-PRESTATAIRES.md) : la liste des métiers et leur date
// d'arrêt. Depuis le 17/10/2026 (agenda simplifié), la date d'arrêt se règle ici : [Arrêter ce métier…] sur chaque
// métier exercé, [Retirer la date d'arrêt] s'il en a une. Métier arrêté : [Reprendre ce métier].
// Depuis le 11/11/2026 (schema_v35) : le prix de l'heure de chaque métier, [Prix…] pour le donner ou le changer.
import { ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { formaterDate } from '../../outils/dates'
import { euros, versCentimes } from '../../outils/prix'
import type { MetierExerce, ProfilPrestataire } from '../../outils/prestataires'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppChamp from '../ui/AppChamp.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import AppSection from '../ui/AppSection.vue'
import FenetreArret from './FenetreArret.vue'

const props = defineProps<{ profil: ProfilPrestataire }>()
const emit = defineEmits<{ maj: [profil: ProfilPrestataire] }>()
const { afficherMessage } = useMessage()

// [Arrêter ce métier…] : la fenêtre de la date d'arrêt, pour ce métier
const aArreter = ref<MetierExerce | null>(null)

async function retirerArret(metier: MetierExerce) {
  try {
    emit('maj', await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/metiers/fin', {
      metier_id: metier.id, fin_le: null, suivant_id: null,
    }))
    afficherMessage(`Date d'arrêt retirée : ${metier.nom} continue.`)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

async function reprendre(metier: MetierExerce) {
  try {
    emit('maj', await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/metiers/fin', {
      metier_id: metier.id, fin_le: null, suivant_id: null,
    }))
    afficherMessage(`${metier.nom} repris : vous apparaissez de nouveau dans ses recherches.`)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}

// [Prix…] : le prix de l'heure d'un métier (facultatif, de 1 € à 1 000 €)
const texteDuPrix = (m: MetierExerce) => (m.prix_centimes ? `${euros(m.prix_centimes)} de l'heure` : 'Pas de prix de l’heure')
const aChiffrer = ref<MetierExerce | null>(null)
const prixSaisi = ref('')
const erreurPrix = ref('')
function ouvrirPrix(metier: MetierExerce) {
  aChiffrer.value = metier
  prixSaisi.value = metier.prix_centimes ? String(metier.prix_centimes / 100).replace('.', ',') : ''
  erreurPrix.value = ''
}
async function enregistrerPrix(effacer = false) {
  if (!aChiffrer.value) return
  const centimes = effacer ? null : versCentimes(prixSaisi.value)
  if (!effacer && centimes === null) {
    erreurPrix.value = 'Écrivez un prix, ex. 45 ou 45,50.'
    return
  }
  try {
    emit('maj', await appelerServeur<ProfilPrestataire>('/api/moi/prestataire/prix', { metier_id: aChiffrer.value.id, prix_centimes: centimes }))
    afficherMessage(centimes ? `${aChiffrer.value.nom} : ${euros(centimes)} de l'heure.` : `Prix de ${aChiffrer.value.nom} effacé.`)
    aChiffrer.value = null
  } catch (e) {
    erreurPrix.value = messageErreur(e) // ex. « Le prix de l'heure doit être entre 1 € et 1 000 €. »
  }
}
</script>

<template>
  <AppSection titre="Mes métiers">
    <!-- Comme la grande maquette : une ligne par métier, « 45 € de l'heure », [Prix…] et l'arrêt -->
    <div class="liste">
      <div class="ligne ligne-rdv">
        <div class="txt">
          <b>{{ profil.metier_principal.nom }} <span class="puce p-ok" style="display: inline-flex; margin-left: 6px">principal</span></b>
          <span class="whitespace-normal!">
            {{ texteDuPrix(profil.metier_principal) }}
            <template v-if="profil.metier_principal.fin_le">
              · arrêt prévu après le {{ formaterDate(profil.metier_principal.fin_le) }} :
              <template v-if="profil.metier_principal_suivant">ensuite, {{ profil.metier_principal_suivant.nom }} deviendra votre métier principal.</template>
              <template v-else>c'est votre seul métier ; votre profil restera affiché.</template>
            </template>
          </span>
        </div>
        <span class="fin">
          <button type="button" class="btn btn-2 btn-petit" @click="ouvrirPrix(profil.metier_principal)">Prix…</button>
          <button v-if="profil.metier_principal.fin_le" type="button" class="btn btn-2 btn-petit" @click="retirerArret(profil.metier_principal)">Retirer la date d’arrêt</button>
          <button v-else type="button" class="btn btn-2 btn-petit" @click="aArreter = profil.metier_principal">Arrêter ce métier…</button>
        </span>
      </div>

      <div v-for="metier in profil.metiers_secondaires" :key="metier.id" class="ligne ligne-rdv">
        <div class="txt">
          <b>{{ metier.nom }}</b>
          <span>{{ texteDuPrix(metier) }}<template v-if="metier.fin_le"> · dernier jour le {{ formaterDate(metier.fin_le) }}</template></span>
        </div>
        <span class="fin">
          <button type="button" class="btn btn-2 btn-petit" @click="ouvrirPrix(metier)">Prix…</button>
          <button v-if="metier.fin_le" type="button" class="btn btn-2 btn-petit" @click="retirerArret(metier)">Retirer la date d’arrêt</button>
          <button v-else type="button" class="btn btn-2 btn-petit" @click="aArreter = metier">Arrêter ce métier…</button>
        </span>
      </div>

      <div v-for="metier in profil.metiers_arretes" :key="metier.id" class="ligne ligne-rdv">
        <div class="txt">
          <b>{{ metier.nom }} <span class="puce p-neutre" style="display: inline-flex; margin-left: 6px">arrêté depuis le {{ formaterDate(metier.fin_le ?? '') }}</span></b>
          <span>Vous n'apparaissez plus dans les recherches de ce métier.</span>
        </div>
        <span class="fin"><button type="button" class="btn btn-1 btn-petit" @click="reprendre(metier)">Reprendre ce métier</button></span>
      </div>
    </div>
    <p class="doux petit">
      Ajouter un métier : la bulle « + Ajouter » en haut du profil. Arrêter un métier : [Arrêter ce métier…], puis choisir son dernier jour. Après cette date,
      vous n'apparaissez plus dans les recherches de ce métier, et les rendez-vous de ce métier pris après cette date sont annulés (clients prévenus).
    </p>
  </AppSection>
  <FenetreArret
    v-if="aArreter"
    :ouverte="aArreter !== null"
    :metier="aArreter"
    :profil="props.profil"
    @maj-profil="(p) => emit('maj', p)"
    @fermer="aArreter = null"
  />
  <AppFenetre :ouverte="aChiffrer !== null" :titre="`Prix de l'heure — ${aChiffrer?.nom}`" @fermer="aChiffrer = null">
    <AppChamp v-model="prixSaisi" etiquette="Votre prix de l’heure (€)" inputmode="decimal" placeholder="Ex. 45" aide="De 1 € à 1 000 €. Montré sur votre carte dans « Trouver » et sur votre page." />
    <AppAlerte v-if="erreurPrix">{{ erreurPrix }}</AppAlerte>
    <template #pied>
      <AppBouton @click="enregistrerPrix()">Enregistrer</AppBouton>
      <AppBouton v-if="aChiffrer?.prix_centimes" variante="secondaire" @click="enregistrerPrix(true)">Effacer le prix</AppBouton>
      <AppBouton variante="secondaire" @click="aChiffrer = null">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
