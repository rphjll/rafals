<script setup lang="ts">
// Aperçu d'une carte de visite (8,5 × 5,5 cm), le même en grand (onglet « Chez un imprimeur ») et en petit sur la
// planche A4 (onglet « Chez moi ») : les tailles sont en « cqw » (% de la largeur de la carte), la carte se réduit d'un bloc.
// Papier blanc même en mode sombre (couleurs papier / encre). .doc/ihm/RM-CARTE-VISITE-IHM.md
defineProps<{
  nom: string
  metier: string
  ville: string
  note: string
  phrase: string
  /** Vide : pas de téléphone sur la carte */
  telephone: string | null
  /** La couleur choisie, ex. « #1D3A5F » : bande, nom et carré */
  teinte: string
  /** L'image du carré à scanner (servie par le serveur) */
  carre: string
  /** Petite carte de la planche : sans ombre, avec le trait de coupe en pointillés */
  petite?: boolean
}>()
</script>

<template>
  <div class="@container w-full">
    <div
      class="relative grid aspect-[85/55] w-full grid-cols-[1fr_31%] gap-[5%] overflow-hidden bg-papier py-[6.5%] pr-[6%] pl-[11%] font-[Helvetica,Arial,sans-serif] text-encre"
      :class="petite ? 'outline-[0.5px] outline-encre-douce/40 outline-dashed' : 'rounded-[1.9cqw] shadow-[0_2px_14px_rgb(0_0_0/0.18)]'"
      :aria-label="petite ? undefined : 'Aperçu de la carte de visite'"
      :aria-hidden="petite ? 'true' : undefined"
    >
      <span class="absolute inset-y-0 left-0 w-[3.5%]" :style="{ background: teinte }" />
      <div class="flex min-w-0 flex-col">
        <b class="truncate text-[4.9cqw] leading-tight" :style="{ color: teinte }">{{ nom }}</b>
        <span class="mt-[3%] truncate text-[3.3cqw]">{{ metier }}</span>
        <span class="truncate text-[2.9cqw] text-encre-douce">{{ ville }}</span>
        <span v-if="phrase.trim()" class="mt-[2%] truncate text-[2.7cqw]">{{ phrase.trim() }}</span>
        <span class="mt-auto truncate text-[2.9cqw]">{{ note }}</span>
        <b v-if="telephone" class="text-[3.3cqw]">{{ telephone }}</b>
        <span class="mt-[3%] text-[2.35cqw] text-encre-douce">rafals.</span>
      </div>
      <div class="flex flex-col items-center justify-center gap-[1cqw]">
        <img :src="carre" :alt="petite ? '' : 'Carré à scanner vers votre page publique'" class="w-full" />
        <span class="text-center text-[2.2cqw] leading-tight text-encre-douce">Mes avis et mes photos</span>
      </div>
    </div>
  </div>
</template>
