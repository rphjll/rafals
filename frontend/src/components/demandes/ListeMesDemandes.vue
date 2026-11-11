<script setup lang="ts">
// Mes demandes (.doc/ihm/RM-DEMANDES-IHM.md ; RM-DEMANDES.md) : les demandes que j'ai publiées, avec leur état ;
// modifier (tant que personne n'a répondu), fermer, prolonger, rouvrir. Une seule liste, montrée à deux endroits :
// l'onglet « Demandes › Mes demandes » et l'onglet « Mes demandes » de l'accueil (demande de Raphael du 21/10/2026).
// Comme la grande maquette : « En cours » puis « Terminées », une ligne par demande ; un clic l'ouvre avec ses boutons.
import { computed, onMounted, ref, watch } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useCompte } from '../../composables/useCompte'
import { useMessage } from '../../composables/useMessage'
import { formaterDate, formaterDateHeure } from '../../outils/dates'
import AppIcone from '../ui/AppIcone.vue'
import { badgeDemande, type MaDemande, texteBudget, texteQuand } from '../../outils/demandes'
import AppAlerte from '../ui/AppAlerte.vue'
import AppBadge from '../ui/AppBadge.vue'
import AppBouton from '../ui/AppBouton.vue'
import AppFenetre from '../ui/AppFenetre.vue'
import FenetreModifierDemande from './FenetreModifierDemande.vue'

const emit = defineEmits<{ nombre: [n: number] }>()
const { compte } = useCompte()
const { afficherMessage } = useMessage()
const demandes = ref<MaDemande[] | null>(null)
const erreur = ref('')
const aFermer = ref<MaDemande | null>(null)
const aModifier = ref<MaDemande | null>(null)
// Mode replié : la demande ouverte (une seule à la fois)
const ouverte = ref<number | null>(null)
const basculer = (id: number) => (ouverte.value = ouverte.value === id ? null : id)
// « En cours » (ouvertes), puis « Terminées » (rendez-vous pris, expirées, fermées)
const groupes = computed(() =>
  [
    { titre: 'En cours', liste: (demandes.value ?? []).filter((d) => d.statut === 'ouverte') },
    { titre: 'Terminées', liste: (demandes.value ?? []).filter((d) => d.statut !== 'ouverte') },
  ].filter((g) => g.liste.length),
)
// La phrase en gras sous la demande ouverte
function info(d: MaDemande): string {
  if (d.statut === 'ouverte') return `Ouverte jusqu’au ${formaterDateHeure(d.expire_le)}. Les prestataires « ${d.metier} » près de chez vous la voient.`
  if (d.statut === 'pourvue') return 'Rendez-vous pris : il est dans votre agenda.'
  if (d.statut === 'expiree') return `Expirée le ${formaterDateHeure(d.expire_le)} : les prestataires ne la voient plus.`
  return 'Fermée : les prestataires ne la voient plus.'
}

async function charger() {
  if (!compte.value) return
  try {
    demandes.value = await appelerServeur<MaDemande[]>('/api/moi/demandes')
    emit('nombre', demandes.value.length)
    erreur.value = ''
  } catch (e) {
    erreur.value = messageErreur(e)
  }
}
onMounted(charger)
watch(compte, charger)
defineExpose({ charger })

async function agir(demande: MaDemande, action: 'fermer' | 'prolonger' | 'rouvrir', reussite: string) {
  try {
    await appelerServeur(`/api/demandes/${demande.id}/${action}`, {})
    afficherMessage(reussite)
    await charger()
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur') // ex. « Le rendez-vous de cette demande est toujours prévu… »
  }
  aFermer.value = null
}
</script>

<template>
  <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>
  <div v-else-if="demandes && !demandes.length" class="carte vide">
    <h3>Aucune demande pour l’instant</h3>
    <p style="margin-top: 6px">Une fuite, une prise, un meuble à monter ? Publiez une demande en 1 minute.</p>
  </div>
  <template v-else-if="demandes">
    <section v-for="groupe in groupes" :key="groupe.titre" class="section">
      <h2 class="h-sec">{{ groupe.titre }}</h2>
      <!-- Une demande repliée en une ligne ; un clic l'ouvre (grande maquette) -->
      <article v-for="d in groupe.liste" :key="d.id" class="carte dmd dmd-perso" :class="{ ouvert: ouverte === d.id }">
        <button type="button" class="dmd-tete" :aria-expanded="ouverte === d.id" @click="basculer(d.id)">
          <div class="txt">
            <AppBadge :etat="badgeDemande(d).etat">{{ badgeDemande(d).texte }}</AppBadge>
            <h3>{{ d.titre }}</h3>
            <span class="doux petit">{{ d.metier }} · {{ d.ville }} · publiée le {{ formaterDate(d.cree_le) }}</span>
          </div>
          <span class="fin">
            <span v-if="d.nombre_reponses" class="puce p-ok">{{ d.nombre_reponses }} réponse{{ d.nombre_reponses > 1 ? 's' : '' }}</span>
            <span class="chev" aria-hidden="true">›</span>
          </span>
        </button>
        <div v-if="ouverte === d.id" class="dmd-corps">
          <p class="whitespace-pre-line">{{ d.description }}</p>
          <p class="doux petit">Pour quand : {{ texteQuand(d) }}<template v-if="d.budget_centimes"> · budget {{ texteBudget(d.budget_centimes) }}</template></p>
          <p class="petit"><b>{{ info(d) }}</b></p>
          <div v-if="d.nombre_reponses" class="dmd-rep">
            <b>{{ d.nombre_reponses }} prestataire{{ d.nombre_reponses > 1 ? 's vous ont' : ' vous a' }} répondu</b>
            <RouterLink class="ligne" to="/messages">
              <span class="ico-rond"><AppIcone nom="messages" /></span>
              <div class="txt"><b>Lire leurs messages</b><span>Chaque réponse est une conversation dans « Messages ».</span></div>
              <span class="fin"><AppIcone nom="suite" /></span>
            </RouterLink>
          </div>
          <p v-else-if="d.statut === 'ouverte'" class="dmd-vide">Pas encore de réponse. Vous aurez un message dès qu’un prestataire répond.</p>
          <div class="btns">
            <template v-if="d.statut === 'ouverte'">
              <button v-if="!d.nombre_reponses" type="button" class="btn btn-2 btn-petit" @click="aModifier = d">Modifier…</button>
              <AppBouton
                v-else
                variante="verrouille"
                petit
                raison-verrou="Un prestataire a déjà répondu : pour changer cette demande, fermez-la et publiez-en une autre."
              >
                Modifier…
              </AppBouton>
              <button type="button" class="btn btn-2 btn-petit" @click="agir(d, 'prolonger', 'Demande prolongée de 30 jours.')">Prolonger de 30 jours</button>
              <button type="button" class="btn btn-danger-2 btn-petit" @click="aFermer = d">Fermer ma demande…</button>
            </template>
            <button v-else-if="d.statut === 'expiree'" type="button" class="btn btn-1 btn-petit" @click="agir(d, 'prolonger', 'Demande rouverte pour 30 jours.')">
              Rouvrir pour 30 jours
            </button>
            <template v-else-if="d.statut === 'pourvue'">
              <RouterLink class="btn btn-2 btn-petit" to="/mon-agenda?calendrier=client">Voir le rendez-vous</RouterLink>
              <button type="button" class="btn btn-2 btn-petit" @click="agir(d, 'rouvrir', 'Demande rouverte pour 30 jours.')">Rouvrir (rendez-vous annulé)</button>
            </template>
          </div>
        </div>
      </article>
    </section>
  </template>

  <FenetreModifierDemande :demande="aModifier" @fermer="aModifier = null" @modifiee="(aModifier = null), charger()" />
  <AppFenetre :ouverte="aFermer !== null" :titre="`Fermer « ${aFermer?.titre} » ?`" @fermer="aFermer = null">
    Les prestataires ne la verront plus et ne pourront plus y répondre. Elle reste dans « Mes demandes ».
    <template #pied>
      <button type="button" class="btn btn-danger" @click="aFermer && agir(aFermer, 'fermer', 'Demande fermée.')">Fermer ma demande</button>
      <AppBouton variante="secondaire" @click="aFermer = null">Annuler</AppBouton>
    </template>
  </AppFenetre>
</template>
