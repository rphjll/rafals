<script setup lang="ts">
// Carte « Aujourd'hui » en haut de « Mon activité » (prestataire ; demande de Raphael du 25/11/2026, maquette
// .doc/ihm/maquette-faciliter-prestataires.html ; .doc/ihm/RM-MON-ACTIVITE-IHM.md). 3 lignes au plus :
// le prochain rendez-vous du jour (itinéraire, appeler), celui qui reste à encaisser ([Payé…] → facture, comme dans
// l'agenda), puis « + 1 autre aujourd'hui (17 h 30, Sophie L.) › ». Sans rendez-vous aujourd'hui : le prochain.
// L'agenda ne change pas : la carte lit les mêmes rendez-vous et appelle la même adresse que lui.
import { computed, onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../../api'
import { useMessage } from '../../composables/useMessage'
import { aParis, heure, jourLisible } from '../../outils/agenda'
import type { MoyenDirect } from '../../outils/factures'
import { montant } from '../../outils/paiements'
import { type RendezVousVisible, encaissable } from '../../outils/rendez_vous'
import FenetrePayeDirect from '../FenetrePayeDirect.vue'
import AppIcone from '../ui/AppIcone.vue'

const props = defineProps<{ siretVerifie: boolean }>()
const emit = defineEmits<{ maj: [] }>()
const { afficherMessage } = useMessage()

const tous = ref<RendezVousVisible[] | null>(null)
async function charger() {
  tous.value = await appelerServeur<RendezVousVisible[]>('/api/moi/prestataire/rendez-vous').catch(() => null)
}
onMounted(charger)

const maintenant = ref(new Date())
const aujourdhui = computed(() => aParis(maintenant.value.toISOString()).jour)
const confirmes = computed(() =>
  (tous.value ?? []).filter((r) => r.statut === 'confirme').sort((a, b) => a.debut.localeCompare(b.debut)),
)
const duJour = computed(() => confirmes.value.filter((r) => aParis(r.debut).jour === aujourdhui.value))
/** Le prochain du jour : pas encore fini */
const prochain = computed(() => duJour.value.find((r) => new Date(r.fin) > maintenant.value) ?? null)
/** Celui qui reste à encaisser (espèces, commencé, pas encore noté payé), seulement avec un SIRET vérifié */
const aEncaisserDuJour = computed(() =>
  props.siretVerifie ? (duJour.value.find((r) => r !== prochain.value && encaissable(r, maintenant.value)) ?? null) : null,
)
const autres = computed(() => duJour.value.filter((r) => r !== prochain.value && r !== aEncaisserDuJour.value))
/** Sans rendez-vous aujourd'hui : le prochain des jours suivants */
const plusTard = computed(() =>
  duJour.value.length ? null : (confirmes.value.find((r) => aParis(r.debut).jour > aujourdhui.value) ?? null),
)

const h = (r: RendezVousVisible) => heure(aParis(r.debut).heure)
/** « 3 allée des Pins, 44400 Rezé » → « Rezé » ; chez moi → « chez vous » */
function ou(r: RendezVousVisible): string {
  if (r.lieu === 'chez_moi' || !r.adresse) return 'chez vous'
  return r.adresse.split(',').pop()?.trim().replace(/^\d{5}\s*/, '') || r.adresse
}
const itineraire = (adresse: string) => `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(adresse)}`

// [Payé…] : la fenêtre commune de l'agenda et des devis ; rafals crée la facture
const aEncaisser = ref<RendezVousVisible | null>(null)
async function encaisser(moyen: MoyenDirect) {
  const r = aEncaisser.value
  aEncaisser.value = null
  if (!r) return
  try {
    const fait = await appelerServeur<RendezVousVisible>(`/api/moi/prestataire/rendez-vous/${r.id}/paye`, { moyen })
    afficherMessage(`Paiement noté : la facture ${fait.facture_numero} est créée.`)
    await charger()
    emit('maj')
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <div v-if="duJour.length || plusTard" class="carte jour">
    <div class="jour-tete">
      <h2 v-if="duJour.length">Aujourd’hui · {{ duJour.length }} rendez-vous</h2>
      <h2 v-else>Rien de prévu aujourd’hui</h2>
    </div>

    <div v-if="prochain" class="jl">
      <span class="h">{{ h(prochain) }}</span>
      <div class="txt"><b>{{ prochain.autre.nom }}</b> <span class="doux">· {{ ou(prochain) }} · prochain</span></div>
      <a
        v-if="prochain.lieu === 'chez_client' && prochain.adresse"
        class="btn btn-2 btn-petit rond"
        :href="itineraire(prochain.adresse)"
        target="_blank"
        rel="noopener"
        aria-label="Itinéraire"
        title="Itinéraire"
      ><AppIcone nom="lieu" /></a>
      <a
        v-if="prochain.autre.telephone"
        class="btn btn-2 btn-petit rond"
        :href="`tel:${prochain.autre.telephone.replace(/\s/g, '')}`"
        :aria-label="`Appeler le ${prochain.autre.telephone}`"
        :title="prochain.autre.telephone"
      ><AppIcone nom="telephone" /></a>
    </div>

    <div v-if="aEncaisserDuJour" class="jl">
      <span class="h doux">{{ h(aEncaisserDuJour) }}</span>
      <div class="txt">
        <b>{{ aEncaisserDuJour.autre.nom }}</b>
        <span class="doux"> · {{ montant(aEncaisserDuJour.prix_centimes ?? 0) }} à encaisser</span>
      </div>
      <button type="button" class="btn btn-1 btn-petit" @click="aEncaisser = aEncaisserDuJour">Payé…</button>
    </div>

    <RouterLink v-if="autres.length" class="jl-plus" to="/mon-agenda?onglet=rendez-vous">
      + {{ autres.length }} {{ autres.length > 1 ? 'autres' : 'autre' }} aujourd’hui
      ({{ autres.map((r) => `${h(r)}, ${r.autre.nom}`).join(' ; ') }}) ›
    </RouterLink>

    <RouterLink v-if="plusTard" class="jl-plus" to="/mon-agenda?onglet=rendez-vous">
      Prochain rendez-vous : {{ jourLisible(aParis(plusTard.debut).jour) }} à {{ h(plusTard) }}, {{ plusTard.autre.nom }} ›
    </RouterLink>
  </div>

  <FenetrePayeDirect
    :demande="aEncaisser ? { nom: aEncaisser.autre.nom, centimes: aEncaisser.prix_centimes ?? 0 } : null"
    @fermer="aEncaisser = null"
    @confirmer="encaisser"
  />
</template>

<style scoped>
.jour{display:flex;flex-direction:column;padding:0;overflow:hidden}
.jour-tete{padding:14px 18px;background:var(--primaire-doux)}
.jour-tete h2{color:var(--primaire);font-size:19px}
.jl{display:flex;align-items:center;gap:10px;padding:10px 18px;border-top:1px solid var(--bord)}
.h{font-family:var(--titre);font-weight:800;font-variant-numeric:tabular-nums;width:62px;flex:none}
.txt{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rond{width:38px;padding:0}
.jl-plus{display:block;border-top:1px solid var(--bord);padding:10px 18px;font-weight:600;color:var(--primaire);text-decoration:none}
.jl-plus:hover{text-decoration:underline}
</style>
