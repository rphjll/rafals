<script setup lang="ts">
// En-tête commun à toutes les pages (.doc/ihm/RM-ENTETE-IHM.md) : 4 entrées (5 une fois connecté, avec « Messages »),
// puis le menu du compte.
// Sous 768 px de large, les entrées passent dans la barre du bas (AppBarreBas) ; ☰ ne garde que le compte.
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { messageErreur } from '../api'
import { useCompte } from '../composables/useCompte'
import { useMenu } from '../composables/useMenu'
import { useMessage } from '../composables/useMessage'
import { useNonLus } from '../composables/useNonLus'
import AppBouton from './ui/AppBouton.vue'

const menuOuvert = ref(false)
const compteOuvert = ref(false)
const zoneCompte = ref<HTMLElement | null>(null)
const route = useRoute()
const routeur = useRouter()
const { compte, chargementFait, seDeconnecter } = useCompte()
const { estSur, entrees: liens } = useMenu()
const { afficherMessage } = useMessage()
const { actualiserNonLus } = useNonLus()
watch(compte, actualiserNonLus, { immediate: true })
watch(
  () => route.fullPath,
  () => (menuOuvert.value = compteOuvert.value = false),
)

// Les entrées principales (« liens ») viennent de useMenu : la barre du bas, sur téléphone, montre les mêmes
const liensCompte = computed(() => [
  { vers: '/compte', texte: 'Mon compte' },
  // Visible seulement des administrateurs (lot 1.4)
  ...(compte.value?.est_administrateur ? [{ vers: '/administration', texte: 'Administration' }] : []),
])
const initiales = computed(() => `${compte.value?.prenom[0] ?? ''}${compte.value?.nom[0] ?? ''}`.toUpperCase())
const surCompte = computed(() => liensCompte.value.some((lien) => estSur(lien.vers)))

// Un clic ou une tabulation hors du menu du compte le referme
function sortieCompte(evenement: FocusEvent) {
  if (!zoneCompte.value?.contains(evenement.relatedTarget as Node | null)) compteOuvert.value = false
}

async function deconnexion() {
  try {
    await seDeconnecter()
    afficherMessage('Vous êtes déconnecté.')
    routeur.push('/')
  } catch (erreur) {
    afficherMessage(messageErreur(erreur), 'erreur')
  }
}
</script>

<template>
  <header class="sticky top-[env(safe-area-inset-top,0px)] z-10 border-b border-bord bg-surface px-4">
    <div class="relative mx-auto flex h-[60px] max-w-[1080px] items-center gap-4">
      <RouterLink to="/" class="font-marque text-2xl font-bold tracking-tight text-primaire" aria-label="Accueil rafals">
        rafals<span class="text-accent">.</span>
      </RouterLink>
      <button
        type="button"
        class="ml-auto h-[38px] w-[42px] rounded-rafals border border-bord text-xl text-texte md:hidden"
        :aria-expanded="menuOuvert"
        aria-controls="menu-principal"
        :aria-label="menuOuvert ? 'Fermer le menu' : 'Ouvrir le menu'"
        @click="menuOuvert = !menuOuvert"
      >
        ☰
      </button>
      <nav
        id="menu-principal"
        class="absolute top-[60px] right-[-16px] left-[-16px] flex-col border-b border-bord bg-surface px-4 pt-2 pb-3.5 md:static md:ml-auto md:flex md:flex-row md:items-center md:gap-1 md:border-0 md:p-0"
        :class="menuOuvert ? 'flex' : 'hidden'"
      >
        <RouterLink
          v-for="lien in liens"
          :key="lien.vers"
          :to="lien.vers"
          class="rounded-bouton px-3 py-2.5 font-bold hover:bg-primaire-doux hover:text-primaire max-md:hidden md:py-2"
          :class="lien.actif ? 'bg-primaire-doux text-primaire' : 'text-texte'"
        >
          {{ lien.texte }}
          <span
            v-if="lien.compteur"
            class="ml-1 rounded-full bg-erreur px-2 py-0.5 text-xs font-bold text-sur-etat"
            :aria-label="`${lien.compteur} conversation${lien.compteur > 1 ? 's' : ''} non lue${lien.compteur > 1 ? 's' : ''}`"
          >
            {{ lien.compteur }}
          </span>
        </RouterLink>
        <!-- Tant qu'on ne sait pas si quelqu'un est connecté, on n'affiche rien (évite un clignotement) -->
        <div v-if="chargementFait" class="flex flex-col pt-2 md:pt-0 md:pl-2">
          <div
            v-if="compte"
            ref="zoneCompte"
            class="relative flex flex-col"
            @focusout="sortieCompte"
            @keydown.esc="compteOuvert = false"
          >
            <button
              type="button"
              class="hidden min-h-[42px] items-center gap-2 rounded-full border bg-surface py-1 pr-3 pl-1 font-semibold md:inline-flex"
              :class="surCompte ? 'border-primaire text-primaire' : 'border-bord text-texte'"
              :aria-expanded="compteOuvert"
              aria-controls="menu-compte"
              @click="compteOuvert = !compteOuvert"
            >
              <span
                class="flex h-8 w-8 items-center justify-center rounded-full bg-primaire-doux text-[13px] font-bold text-primaire"
                aria-hidden="true"
              >
                {{ initiales }}
              </span>
              {{ compte.prenom }}
              <span aria-hidden="true">▾</span>
            </button>
            <!-- Téléphone : la liste est toujours dépliée dans le menu ☰ ; ordinateur : elle s'ouvre sous le prénom -->
            <div
              id="menu-compte"
              class="flex flex-col gap-1 border-t border-bord pt-2 md:absolute md:top-[calc(100%+8px)] md:right-0 md:w-56 md:rounded-rafals md:border md:bg-surface md:p-1.5"
              :class="compteOuvert ? '' : 'md:hidden'"
            >
              <span class="px-3 text-[13px] text-texte-doux md:hidden">{{ compte.prenom }}</span>
              <RouterLink
                v-for="lien in liensCompte"
                :key="lien.vers"
                :to="lien.vers"
                class="rounded-rafals px-3 py-2.5 font-semibold hover:bg-primaire-doux hover:text-primaire"
                :class="estSur(lien.vers) ? 'bg-primaire-doux text-primaire' : 'text-texte'"
              >
                {{ lien.texte }}
              </RouterLink>
              <AppBouton variante="secondaire" pleine-largeur @click="deconnexion">Se déconnecter</AppBouton>
            </div>
          </div>
          <AppBouton v-else @click="routeur.push('/connexion')">Se connecter</AppBouton>
        </div>
      </nav>
    </div>
  </header>
</template>
