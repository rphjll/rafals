<template>
  <!-- Trait horizontal avec un petit texte au milieu (ex. « déjà inscrit ? ») -->
  <div class="flex items-center gap-2.5 text-[13px] text-texte-doux before:flex-1 before:border-t before:border-bord before:content-[''] after:flex-1 after:border-t after:border-bord after:content-['']">
    <slot />
  </div>
</template>
