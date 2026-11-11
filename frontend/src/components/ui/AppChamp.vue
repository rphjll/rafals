<script setup lang="ts">
// Champ de saisie : étiquette au-dessus, astérisque si obligatoire, message d'erreur dessous (CONVENTIONS-IHM).
// Les autres réglages (autocomplete, inputmode…) passent directement au champ.
import { useId } from 'vue'

defineOptions({ inheritAttrs: false })

withDefaults(
  defineProps<{
    etiquette: string
    obligatoire?: boolean
    erreur?: string
    type?: string
    aide?: string
  }>(),
  { obligatoire: false, erreur: '', type: 'text', aide: '' },
)
const valeur = defineModel<string>({ default: '' })
const id = useId()
</script>

<template>
  <!-- Champ de la grande maquette (classe « champ ») : étiquette en gras, case de 48 px, aide en petit dessous -->
  <div class="champ">
    <label :for="id">{{ etiquette }}<span v-if="obligatoire" class="text-erreur" aria-hidden="true"> *</span></label>
    <input
      v-bind="$attrs"
      :id="id"
      v-model="valeur"
      :type="type"
      :required="obligatoire"
      :aria-invalid="erreur ? true : undefined"
      :aria-describedby="erreur || aide ? `${id}-aide` : undefined"
      :class="erreur ? 'border-erreur!' : ''"
    />
    <p v-if="erreur" :id="`${id}-aide`" class="erreur-champ">{{ erreur }}</p>
    <small v-else-if="aide" :id="`${id}-aide`">{{ aide }}</small>
  </div>
</template>
