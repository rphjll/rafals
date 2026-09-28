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
  <div class="flex flex-col gap-1.5">
    <label :for="id" class="text-[13px] font-semibold">
      {{ etiquette }}<span v-if="obligatoire" class="text-erreur" aria-hidden="true"> *</span>
    </label>
    <input
      v-bind="$attrs"
      :id="id"
      v-model="valeur"
      :type="type"
      :required="obligatoire"
      :aria-invalid="erreur ? true : undefined"
      :aria-describedby="erreur || aide ? `${id}-aide` : undefined"
      class="min-h-[42px] rounded-rafals border bg-fond px-3 py-2.5 text-texte outline-none focus:border-primaire focus:ring-2 focus:ring-primaire"
      :class="erreur ? 'border-erreur' : 'border-bord'"
    />
    <p v-if="erreur" :id="`${id}-aide`" class="text-[13px] font-medium text-erreur">{{ erreur }}</p>
    <p v-else-if="aide" :id="`${id}-aide`" class="text-[13px] text-texte-doux">{{ aide }}</p>
  </div>
</template>
