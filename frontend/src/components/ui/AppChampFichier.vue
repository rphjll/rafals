<script setup lang="ts">
// Zone « choisir un fichier » : un clic ouvre le sélecteur, le nom du fichier choisi s'affiche.
import { ref, useId } from 'vue'

defineProps<{ etiquette: string; aide: string; accepte: string }>()
const fichier = defineModel<File | null>({ default: null })
const id = useId()
const champ = ref<HTMLInputElement | null>(null)

function choisi(evenement: Event) {
  fichier.value = (evenement.target as HTMLInputElement).files?.[0] ?? null
}
</script>

<template>
  <div class="champ">
    <label :for="id">{{ etiquette }}</label>
    <button
      type="button"
      class="rounded-[14px] border-2 border-dashed border-bord px-4 py-5 text-center text-texte-doux hover:border-primaire hover:bg-primaire-doux"
      @click="champ?.click()"
    >
      <template v-if="fichier">
        <b class="text-texte">{{ fichier.name }}</b> — cliquer pour en choisir un autre
      </template>
      <template v-else>
        <b class="text-texte">Choisir un fichier</b><br />{{ aide }}
      </template>
    </button>
    <input :id="id" ref="champ" type="file" :accept="accepte" class="sr-only" @change="choisi" />
  </div>
</template>
