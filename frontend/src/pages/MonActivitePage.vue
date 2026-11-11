<script setup lang="ts">
// Mon activité (.doc/ihm/RM-MON-ACTIVITE-IHM.md), identique à la grande maquette depuis le 10/11/2026 : les chiffres,
// la carte « Encaissé en 2026 » (prestataire), puis toutes les fonctions en tuiles rangées par groupe. Un prestataire en
// voit plus qu'un client. Une fonction pas encore construite a une tuile grisée « Bientôt ».
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { appelerServeur } from '../api'
import CarteBarreTva from '../components/prestataire/CarteBarreTva.vue'
import ChiffresActivite from '../components/prestataire/ChiffresActivite.vue'
import AppIcone from '../components/ui/AppIcone.vue'
import { useCompte } from '../composables/useCompte'
import { type ActiviteChiffree, GROUPES_ACTIVITE, adresseDe, fonctionsPour } from '../outils/activite'

const routeur = useRouter()
const { compte, chargementFait } = useCompte()

const prestataireId = computed(() => compte.value?.prestataire_id ?? null)
const groupes = computed(() =>
  GROUPES_ACTIVITE.map((groupe) => ({
    cle: groupe.cle,
    titre: prestataireId.value === null ? (groupe.titreClient ?? groupe.titre) : groupe.titre,
    tuiles: fonctionsPour(prestataireId.value)
      .filter((f) => f.groupe === groupe.cle)
      .map((f) => ({ fonction: f, adresse: adresseDe(f, prestataireId.value) })),
  })).filter((groupe) => groupe.tuiles.length),
)

// Les chiffres du haut (RM-MON-ACTIVITE.md) : relus à chaque ouverture de la page ; sans eux, la page reste utilisable
const chiffres = ref<ActiviteChiffree | null>(null)
const pastilles = ref<Record<string, number>>({})
async function chargerChiffres() {
  try {
    chiffres.value = await appelerServeur<ActiviteChiffree>('/api/moi/activite')
  } catch {
    // serveur injoignable : les tuiles suffisent
  }
}
watch(
  compte,
  async (connecte) => {
    chiffres.value = null
    if (!connecte) return
    await chargerChiffres()
    // Pastilles (RM-ALERTES) : nouvelles demandes près de chez moi, nouveaux avis reçus
    const nombre = (chemin: string) => appelerServeur<{ nombre: number }>(chemin).then((r) => r.nombre).catch(() => 0)
    pastilles.value = {
      'demandes-pres': connecte.prestataire_id ? await nombre('/api/moi/prestataire/demandes/nouvelles') : 0,
      'mes-avis-recus': await nombre('/api/moi/avis-recus/non-vus'),
    }
  },
  { immediate: true },
)
watch([chargementFait, compte], () => {
  if (chargementFait.value && !compte.value) routeur.replace({ path: '/connexion', query: { retour: '/mon-activite' } })
})
</script>

<template>
  <div class="page">
    <div class="tete">
      <h1>Mon activité</h1>
      <p>Tout ce qui fait tourner votre activité, au même endroit.</p>
    </div>
    <template v-if="compte">
      <ChiffresActivite v-if="chiffres" :chiffres="chiffres" />
      <!-- Encaissé dans l'année et barre de la TVA -->
      <CarteBarreTva v-if="chiffres?.prestataire" :chiffres="chiffres.prestataire" @maj="chargerChiffres" />

      <section v-for="groupe in groupes" :key="groupe.cle" class="section">
        <h2>{{ groupe.titre }}</h2>
        <div class="tuiles">
          <template v-for="t in groupe.tuiles" :key="t.fonction.cle">
            <RouterLink v-if="t.adresse" class="tuile" :to="t.adresse">
              <span class="ico-rond"><AppIcone :nom="t.fonction.icone" /></span>
              <div><b>{{ t.fonction.texte }}</b><span class="d">{{ t.fonction.detail }}</span></div>
              <span
                v-if="pastilles[t.fonction.cle]"
                class="badge"
                :aria-label="`${pastilles[t.fonction.cle]} nouveau${pastilles[t.fonction.cle] > 1 ? 'x' : ''}`"
              >{{ pastilles[t.fonction.cle] }}</span>
            </RouterLink>
            <div v-else class="tuile bientot" aria-disabled="true">
              <span class="ico-rond"><AppIcone :nom="t.fonction.icone" /></span>
              <div><b>{{ t.fonction.texte }}</b><span class="d">{{ t.fonction.detail }}</span></div>
              <span class="puce p-neutre">Bientôt</span>
            </div>
          </template>
        </div>
      </section>

      <div v-if="prestataireId === null" class="carte vide">
        <h3>Vous proposez vos services ?</h3>
        <p style="margin-top: 6px">Créez votre profil : les demandes des clients, l’agenda et les démarches s’ajoutent ici.</p>
        <RouterLink class="btn btn-1" to="/profil?proposer=1" style="margin-top: 14px">Proposer mes services</RouterLink>
      </div>
    </template>
  </div>
</template>
