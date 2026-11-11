<script setup lang="ts">
// Interrupteur de la grande maquette (classe « switch ») : vert et poussé à droite quand c'est activé.
// Ex. « Créneau libre » dans « Paramètres », « Paiement par carte » dans « Mon profil ». Chaque clic change la valeur.
defineProps<{ etiquette: string; desactive?: boolean }>()
const valeur = defineModel<boolean>({ required: true })
</script>

<template>
  <button type="button" class="switch" role="switch" :aria-checked="valeur" :aria-label="etiquette" :disabled="desactive" @click="valeur = !valeur" />
</template>
