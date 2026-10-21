<script setup lang="ts">
// Mes abonnements (.doc/ihm/RM-ABONNEMENTS-IHM.md ; RM-ABONNEMENTS.md), ouverte depuis la liste sous le prénom :
// les prestataires suivis, le plus récent d'abord. [Notifications] ouvre les 3 cases de ce prestataire seulement,
// enregistrées à chaque clic ; [Se désabonner] retire la carte.
import { onMounted, ref } from 'vue'
import { appelerServeur, messageErreur } from '../api'
import AvatarPrestataire from '../components/prestataire/AvatarPrestataire.vue'
import AppAlerte from '../components/ui/AppAlerte.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import AppBouton from '../components/ui/AppBouton.vue'
import AppCase from '../components/ui/AppCase.vue'
import { useMessage } from '../composables/useMessage'
import {
  type AbonnementVisible,
  type NotificationsAbonnement,
  CASES_NOTIFICATIONS,
  cheminAbonnement,
  texteAbonnes,
} from '../outils/abonnements'
import { noteLisible } from '../outils/recherche'

const { afficherMessage } = useMessage()
const abonnements = ref<AbonnementVisible[] | null>(null)
const erreur = ref('')
const ouverte = ref<number | null>(null) // la carte dont la cloche est ouverte (une seule à la fois)

onMounted(async () => {
  try {
    abonnements.value = await appelerServeur<AbonnementVisible[]>('/api/moi/abonnements')
  } catch (e) {
    erreur.value = messageErreur(e)
  }
})

const cochees = (n: NotificationsAbonnement) => Object.values(n).filter(Boolean).length

// Chaque clic est enregistré tout de suite ; en cas d'échec, la case revient comme avant
async function changerCase(a: AbonnementVisible, cle: keyof NotificationsAbonnement, valeur: boolean) {
  const avant = { ...a.notifications }
  a.notifications[cle] = valeur
  try {
    a.notifications = await appelerServeur<NotificationsAbonnement>(`/api/moi/abonnements/${a.prestataire_id}/notifications`, a.notifications)
    afficherMessage('Enregistré')
  } catch (e) {
    a.notifications = avant
    afficherMessage(messageErreur(e), 'erreur')
  }
}

async function desabonner(a: AbonnementVisible) {
  try {
    await appelerServeur(cheminAbonnement(a.prestataire_id, true), {})
    abonnements.value = (abonnements.value ?? []).filter((x) => x.prestataire_id !== a.prestataire_id)
    afficherMessage(`Vous ne suivez plus ${a.nom_affiche}`)
  } catch (e) {
    afficherMessage(messageErreur(e), 'erreur')
  }
}
</script>

<template>
  <div class="flex w-full flex-col gap-4">
    <div>
      <h1 class="text-[clamp(28px,4.5vw,40px)] font-black">Mes abonnements</h1>
      <p class="text-texte-doux">Les prestataires que vous suivez. La cloche choisit ce qui vous est envoyé sur votre téléphone.</p>
    </div>
    <AppAlerte v-if="erreur">{{ erreur }}</AppAlerte>

    <div v-if="abonnements?.length" class="grid grid-cols-[repeat(auto-fill,minmax(260px,1fr))] items-start gap-4">
      <article
        v-for="a in abonnements"
        :key="a.prestataire_id"
        class="carte flex min-w-0 flex-col gap-3 p-4"
        :class="a.visible ? '' : 'opacity-70'"
      >
        <component
          :is="a.visible ? 'RouterLink' : 'div'"
          :to="a.visible ? `/prestataires/${a.prestataire_id}` : undefined"
          class="flex items-center gap-3"
          :class="a.visible ? 'hover:text-primaire' : ''"
        >
          <AvatarPrestataire :id="a.prestataire_id" :nom="a.nom_affiche" :a-une-photo="a.a_une_photo" />
          <span class="flex min-w-0 flex-col leading-snug">
            <b class="text-[17px] font-black break-words">{{ a.nom_affiche }}</b>
            <span class="text-[13.5px] font-extrabold">{{ a.metier }}</span>
            <span class="text-[13.5px] text-texte-doux">
              {{ a.ville }}<template v-if="a.nombre_avis"> · <b class="text-accent">★ {{ noteLisible(a.note ?? 0) }}</b></template>
            </span>
            <AppBadge v-if="!a.visible" etat="attente" class="mt-1 self-start">Profil en pause</AppBadge>
            <span v-else-if="a.abonnes" class="text-[13px] font-bold text-texte-doux tabular-nums">{{ texteAbonnes(a.abonnes) }}</span>
          </span>
        </component>

        <div class="flex flex-wrap items-center justify-between gap-2">
          <button
            type="button"
            class="inline-flex min-h-[42px] items-center gap-1.5 rounded-bouton px-3.5 font-extrabold"
            :class="ouverte === a.prestataire_id ? 'bg-primaire text-primaire-texte' : 'bg-primaire-doux text-primaire'"
            :aria-expanded="ouverte === a.prestataire_id"
            @click="ouverte = ouverte === a.prestataire_id ? null : a.prestataire_id"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="size-[18px]" aria-hidden="true">
              <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
              <path d="M10.3 21a1.9 1.9 0 0 0 3.4 0" />
            </svg>
            Notifications · {{ cochees(a.notifications) }}/3
          </button>
          <AppBouton variante="secondaire" @click="desabonner(a)">Se désabonner</AppBouton>
        </div>

        <div v-if="ouverte === a.prestataire_id" class="flex flex-col gap-1 border-t border-bord pt-3">
          <div v-for="c in CASES_NOTIFICATIONS" :key="c.cle">
            <AppCase
              :model-value="a.notifications[c.cle]"
              :texte="c.titre"
              @update:model-value="changerCase(a, c.cle, $event)"
            />
            <p class="-mt-1.5 pl-[30px] text-[12.5px] text-texte-doux">{{ c.exemple.replace('{nom}', a.nom_affiche) }}</p>
          </div>
        </div>
      </article>
    </div>

    <div v-else-if="abonnements" class="carte flex flex-col items-center gap-3.5 px-4 py-12 text-center text-texte-doux">
      <p>Vous ne suivez encore personne. Sur la carte d'un prestataire, appuyez sur [S'abonner].</p>
      <RouterLink to="/trouver"><AppBouton>Trouver un prestataire</AppBouton></RouterLink>
    </div>
  </div>
</template>
