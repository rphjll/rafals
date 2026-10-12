// Sommes d'argent : écriture et lecture, à un seul endroit.

/** 5000 → « 50 € » ; 4550 → « 45,50 € » */
export function euros(centimes: number): string {
  const valeur = centimes / 100
  return `${Number.isInteger(valeur) ? valeur : valeur.toFixed(2).replace('.', ',')} €`
}

/** « 45,50 » ou « 45.5 » → 4550 ; texte vide ou illisible → null */
export function versCentimes(texte: string): number | null {
  const nombre = Number(texte.replace(',', '.').replace(/\s|€/g, ''))
  return texte.trim() && Number.isFinite(nombre) ? Math.round(nombre * 100) : null
}
