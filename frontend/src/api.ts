// Un seul endroit pour parler au serveur : envoie la demande, renvoie la réponse,
// ou lève une erreur qui porte le message à montrer tel quel à l'utilisateur.

export class ErreurServeur extends Error {
  constructor(
    message: string,
    public readonly statut: number,
  ) {
    super(message)
  }
}

export async function appelerServeur<T>(chemin: string, donnees?: unknown, methode?: 'GET' | 'POST' | 'PUT'): Promise<T> {
  // Un fichier (FormData) part tel quel ; le reste part en JSON
  const estFormulaire = donnees instanceof FormData
  let reponse: Response
  try {
    reponse = await fetch(chemin, {
      method: methode ?? (donnees === undefined ? 'GET' : 'POST'),
      headers: donnees === undefined || estFormulaire ? undefined : { 'Content-Type': 'application/json' },
      body: donnees === undefined ? undefined : estFormulaire ? donnees : JSON.stringify(donnees),
      credentials: 'same-origin',
    })
  } catch {
    throw new ErreurServeur('Le serveur ne répond pas. Vérifiez votre connexion, puis réessayez.', 0)
  }
  const contenu = await reponse.json().catch(() => ({}))
  if (!reponse.ok) {
    // Message d'une règle (texte) ; sinon (champ mal rempli, liste d'erreurs techniques) un message général
    const detail = typeof contenu.detail === 'string' ? contenu.detail : 'Vérifiez les champs remplis, puis réessayez.'
    throw new ErreurServeur(detail, reponse.status)
  }
  return contenu as T
}

export function messageErreur(erreur: unknown): string {
  return erreur instanceof ErreurServeur ? erreur.message : 'Une erreur inattendue est survenue. Réessayez.'
}
