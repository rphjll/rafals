<script setup lang="ts">
// « Publier une demande » (/demandes/nouvelle), comme la grande maquette : le lien « ‹ Mes demandes », le titre, puis
// le formulaire. Une fois publiée, on arrive sur « Mes demandes ». .doc/ihm/RM-DEMANDES-IHM.md.
import { useRouter } from 'vue-router'
import CartePublierDemande from '../components/demandes/CartePublierDemande.vue'
import AppIcone from '../components/ui/AppIcone.vue'

const routeur = useRouter()
</script>

<template>
  <div class="page">
    <RouterLink class="retour" :to="{ path: '/demandes', query: { onglet: 'miennes' } }"><AppIcone nom="retour" />Mes demandes</RouterLink>
    <div class="tete">
      <h1>Publier une demande</h1>
      <p>Dites ce dont vous avez besoin : les prestataires près de chez vous sont prévenus.</p>
    </div>
    <CartePublierDemande @publiee="routeur.push({ path: '/demandes', query: { onglet: 'miennes' } })" />
  </div>
</template>
