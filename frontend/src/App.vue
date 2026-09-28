<script setup lang="ts">
// Page provisoire du lot 0.1 : prouve que les écrans tournent et parlent au serveur.
// Les vraies couleurs (Tailwind + charte) et les composants arrivent au lot 0.4.
import { onMounted, ref } from 'vue'

const etatServeur = ref('Vérification du serveur…')
const serveurOk = ref<boolean | null>(null)

onMounted(async () => {
  try {
    const reponse = await fetch('/api/etat')
    const donnees = await reponse.json()
    etatServeur.value = donnees.message
    serveurOk.value = true
  } catch {
    etatServeur.value = 'Le serveur ne répond pas.'
    serveurOk.value = false
  }
})
</script>

<template>
  <main class="page">
    <h1 class="logo">rafals<span>.</span></h1>
    <p>En construction.</p>
    <p class="etat" :class="{ ok: serveurOk === true, erreur: serveurOk === false }">{{ etatServeur }}</p>
  </main>
</template>

<style>
body {
  margin: 0;
  background: #f3f6f2;
  color: #1d2620;
  font-family: 'Segoe UI', system-ui, sans-serif;
}
.page {
  max-width: 640px;
  margin: 0 auto;
  padding: 64px 16px;
}
.logo {
  color: #2f6b4f;
  font-size: 48px;
  margin: 0 0 8px;
}
.logo span {
  color: #d9793a;
}
.etat {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 999px;
  background: #e8ecf1;
}
.etat.ok {
  background: #e3f2e8;
  color: #2e7d4f;
}
.etat.erreur {
  background: #fbe4e2;
  color: #b3261e;
}
</style>
