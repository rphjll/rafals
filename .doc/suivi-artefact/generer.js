// Fabrique la page « Suivi rafals » (https://claude.ai/artifact/ArjXcQ9XcV87srh54GYXj6) à partir de .doc/SUIVI-DEV.md :
// un tableau par niveau, un lot par ligne. Lancer : node .doc/suivi-artefact/generer.js, puis republier suivi-rafals.html
// sur ce lien (règle : CLAUDE.md § Suivi). À tenir à la main ici : TITRES (un titre court par lot) et HORS_LOT.
const fs = require('fs')
const path = require('path')
const md = fs.readFileSync(path.join(__dirname, '..', 'SUIVI-DEV.md'), 'utf8').split(/\r?\n/)

// Titres courts écrits à la main (le suivi n'a qu'une longue description par lot)
const TITRES = {
  '0.1': 'Docker et scripts de démarrage', '0.2': 'Connexion à la base', '0.3': 'Tests et base de test', '0.4': 'Squelette des écrans et charte',
  '1.1': 'Comptes : inscription et connexion', '1.2': 'Pages Inscription, Connexion, Mot de passe oublié', '1.3': 'Fichiers, âge, administrateurs, journal', '1.4': 'Mon compte et administration des comptes',
  '2.1': 'Métiers et catégories', '2.2': "Choix d'un métier, administration des métiers", '2.3': 'Profil prestataire', '2.4': 'Vérification du SIRET', '2.5': 'Proposer mes services, profil, SIRET', '2.6': 'Clients : adresse, données, fermeture du compte', '2.7': 'Mon compte : adresse, données, fermeture',
  '3.0': "Règles des annonces et de l'agenda", '3.1': 'Annonces', '3.2': 'Mes annonces', '3.3': 'Agenda : semaine type, blocages, horaires libres', '3.4': 'Mon agenda',
  '4.0': 'Règles : recherche, rendez-vous, avis', '4.1': 'Recherche de prestataires', '4.2': 'Trouver un prestataire, page publique', '4.3': 'Rendez-vous', '4.4': 'Réserver, mes rendez-vous', '4.5': 'Absences et annulations', '4.6': "Boutons d'absence, contestations", '4.7': 'Avis', '4.8': 'Laisser un avis, avis signalés',
  '5.0': "Règles de l'argent (Stripe, 5 %)", '5.1': 'Paiement par carte', '5.2': 'Activer la carte, payer, mes paiements', '5.3': 'Devis', '5.4': 'Écrans des devis', '5.5': 'Factures', '5.6': 'Mes factures',
  '6.0': 'Règles des services', '6.1': "Chiffres de l'administration, chiffre d'affaires à déclarer", '6.2': 'Tableau de bord, Mes démarches, guide auto-entreprise', '6.3': 'Signalements, rappels URSSAF', '6.4': 'Signaler, administration des signalements', '6.5': 'Sites vitrines', '6.6': 'Mon site',
  '7.0': 'Règles des démarches par API', '7.1': "Dossier de création d'auto-entreprise", '7.2': 'Créer mon auto-entreprise', '7.3': "Déclarer à l'URSSAF",
  '8.0': 'Règles « comme AlloVoisins »', '8.1': 'Messagerie', '8.2': 'Écran Messages', '8.3a': 'Demandes des clients', '8.3b': 'Répondre à une demande, propositions', '8.4': 'Mes demandes, demandes près de chez moi', '8.5': 'Alertes, notation du client', '8.6': 'Onglet Alertes, avis reçus', '8.7': 'Site installable et notifications',
  '9.1': 'Retrait des annonces : ajouts dans la base', '9.2': 'Rendez-vous par proposition, retrait du code des annonces', '9.3': 'Écrans sans annonces', '9.4': 'Retrait des annonces : suppressions dans la base',
  '10.1': 'Chiffres de Mon activité', '10.2': 'Mes clients', '10.3': "Relance d'un devis", '10.4': 'Ma carte de visite', '10.5': 'Être mis en avant',
  '11.1': 'Limites sans SIRET : serveur', '11.2': 'Limites sans SIRET : écrans',
}
// Tâches hors lot de la rubrique « Travail en cours » (résumées à la main)
const HORS_LOT = [
  { lot: '—', titre: 'Mon profil façon Instagram', type: 'Écrans', desc: 'Demande du 21/10/2026 : « Mon profil » façon Instagram (photo et 4 chiffres en haut, métiers en bulles, onglets Photos · Mon activité · Mon compte, grille de photos). Validé par Raphael le 21/10/2026.', etat: 'fait' },
  { lot: '—', titre: "S'abonner à un prestataire", type: 'Base + Serveur + Écrans', desc: 'Demande du 21/10/2026 : [S\'abonner] sur chaque prestataire, page « Mes abonnements », notifications choisies par prestataire (créneau libéré, nouveau métier ou service, retour d\'absence), nombre d\'abonnés visible par tous. Construit le 21/10/2026 (schema_v31.sql, 456 tests). À vérifier à l’écran par Raphael.', etat: 'verifier' },
  { lot: '—', titre: 'Thème sombre au choix (Paramètres)', type: 'Écrans', desc: 'Demande du 17/10/2026 : choisir Automatique, Clair ou Sombre dans une nouvelle page Paramètres, sous le prénom en haut à droite. Construit le 17/10/2026, à vérifier à l\'écran par Raphael.', etat: 'verifier' },
  { lot: '—', titre: 'Simplifier « Mon agenda › Calendrier »', type: 'Écrans', desc: 'Maquette F retenue, en pause : à valider par Raphael avant de coder. Aucun fichier du site modifié.', etat: 'cours' },
  { lot: '—', titre: 'Nouvelle présentation du site (style chaleureux)', type: 'Écrans', desc: 'Demande du 04/10/2026. Plusieurs étapes faites, à vérifier à l\'écran par Raphael.', etat: 'verifier' },
  { lot: '—', titre: 'Notifications de la barre de TVA', type: 'Serveur', desc: 'Demande du 17/10/2026 : une notification et un mail à 80 % du seuil de TVA, puis quand il est dépassé.', etat: 'verifier' },
  { lot: '—', titre: 'Adresse du compte et cadenas sans SIRET', type: 'Serveur + Écrans', desc: 'Demandes du 15/10/2026 : demandes près de l\'adresse du compte, bouton [Ajouter votre adresse], cadenas sur ce qu\'un prestataire sans SIRET ne peut pas faire.', etat: 'verifier' },
  { lot: '—', titre: 'Retrait des annonces', type: 'Serveur + Écrans', desc: 'Décision du 04/10/2026. Lots 9.1 à 9.4 faits le 17/10/2026 : tables des annonces supprimées. À vérifier par Raphael.', etat: 'verifier' },
]
const ETATS = { faire: 'À faire', cours: 'En cours', verifier: 'À vérifier', fait: 'Fait' }

const ech = (t) => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
const riche = (t) => ech(t).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/`(.+?)`/g, '<code>$1</code>')

const niveaux = []
for (const l of md) {
  const n = l.match(/^## (Niveau \d+) — ([^(]+)/)
  if (n) niveaux.push({ nom: n[1], titre: n[2].trim(), lots: [] })
  const r = l.match(/^\| (\d+\.\d+[a-z]?) \|/)
  if (!r || !niveaux.length) continue
  const c = l.split('|').slice(1, -1).map((x) => x.trim())
  const fin = c[c.length - 1]
  const etat = fin.includes('✅') ? 'fait' : fin.includes('🔎') ? 'verifier' : fin.includes('🟡') ? 'cours' : 'faire'
  niveaux[niveaux.length - 1].lots.push({ lot: c[0], type: c[1], desc: c[2], etat, note: fin.replace(/[✅🔎🟡⬜]/gu, '').trim(), titre: TITRES[c[0]] || c[2].slice(0, 60) })
}
const tous = niveaux.flatMap((n) => n.lots)
const manquants = tous.filter((x) => !TITRES[x.lot]).map((x) => x.lot)
if (manquants.length) console.log('Lots sans titre court :', manquants.join(', '))
const compte = (l) => Object.fromEntries(Object.keys(ETATS).map((e) => [e, l.filter((x) => x.etat === e).length]))
const lignes = [...HORS_LOT, ...tous]
const total = compte(lignes)

const ligne = (x) => `<tr data-etat="${x.etat}">
  <td class="lot">${x.lot}</td>
  <td><span class="titre">${ech(x.titre)}</span><span class="type">${ech(x.type)}</span><p>${riche(x.desc)}</p></td>
  <td class="etat"><span class="badge ${x.etat}">${ETATS[x.etat]}</span>${x.note ? `<small>${ech(x.note)}</small>` : ''}</td>
</tr>`
const tableau = (lots) => `<div class="defile"><table><thead><tr><th>Lot</th><th>Titre</th><th>État</th></tr></thead><tbody>${lots.map(ligne).join('')}</tbody></table></div>`
const section = (nom, titre, lots, avecCompte) => {
  const c = compte(lots)
  return `<section><header><h2><span>${nom}</span>${ech(titre)}</h2>${avecCompte ? `<span class="avance">${c.fait} fait${c.fait > 1 ? 's' : ''} sur ${lots.length}</span>` : ''}</header>${tableau(lots)}</section>`
}
const jour = new Date().toLocaleDateString('fr-FR', { timeZone: 'Europe/Paris' })

const html = `<title>Suivi rafals</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito:wght@500;700;900&display=swap">
<style>
/* Une colonne : résumé et filtres en haut, puis un tableau par niveau. Couleurs de la charte rafals. */
:root{--fond:#F3F6F2;--surface:#FFFFFF;--texte:#1D2620;--doux:#58665C;--bord:#D8E1DA;--primaire:#2F6B4F;--primaire-texte:#FFFFFF;--primaire-doux:#E2EEE7;--accent:#D9793A;
  --fait:#2E7D4F;--fait-doux:#E3F2E8;--cours:#B26A00;--cours-doux:#FCF0DC;--verifier:#1D4A72;--verifier-doux:#DCEAF7;--faire:#5D6673;--faire-doux:#E8ECF1;--ombre:0 8px 28px rgba(31,77,56,.10)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--fond:#121713;--surface:#1A211C;--texte:#E7ECF2;--doux:#A3AEBD;--bord:#2C3730;--primaire:#79C49C;--primaire-texte:#0F1A13;--primaire-doux:#1C3024;--accent:#F0955A;
  --fait:#6CC592;--fait-doux:#17301F;--cours:#F0B35A;--cours-doux:#33260F;--verifier:#93C2EC;--verifier-doux:#17293A;--faire:#9AA5B4;--faire-doux:#262E39;--ombre:0 8px 28px rgba(0,0,0,.35);color-scheme:dark}}
:root[data-theme="dark"]{--fond:#121713;--surface:#1A211C;--texte:#E7ECF2;--doux:#A3AEBD;--bord:#2C3730;--primaire:#79C49C;--primaire-texte:#0F1A13;--primaire-doux:#1C3024;--accent:#F0955A;
  --fait:#6CC592;--fait-doux:#17301F;--cours:#F0B35A;--cours-doux:#33260F;--verifier:#93C2EC;--verifier-doux:#17293A;--faire:#9AA5B4;--faire-doux:#262E39;--ombre:0 8px 28px rgba(0,0,0,.35);color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--fond);color:var(--texte);font:500 15px/1.5 Nunito,system-ui,sans-serif;padding-inline:16px;padding-block:28px 56px}
.page{max-width:980px;margin:0 auto;display:flex;flex-direction:column;gap:22px}
h1,h2,p{margin:0}
h1{font-weight:900;font-size:clamp(28px,4.5vw,38px);line-height:1.1}
h1 i{font-style:normal;color:var(--accent)}
.doux{color:var(--doux)}
:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.barre{display:flex;height:14px;border-radius:99px;overflow:hidden;background:var(--faire-doux)}
.barre span{display:block}
.filtres{display:flex;flex-wrap:wrap;gap:8px}
.filtres button{font:inherit;font-weight:700;min-height:42px;padding:6px 16px;border-radius:99px;border:2px solid transparent;background:var(--surface);color:var(--texte);cursor:pointer;display:inline-flex;align-items:center;gap:8px;box-shadow:var(--ombre)}
.filtres button[aria-pressed="true"]{border-color:var(--primaire);background:var(--primaire-doux)}
.filtres b{font-weight:900;font-variant-numeric:tabular-nums}
.point{width:10px;height:10px;border-radius:50%;flex:none}
section{background:var(--surface);border-radius:20px;box-shadow:var(--ombre);padding:18px 20px;display:flex;flex-direction:column;gap:10px;min-width:0}
section header{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:baseline;justify-content:space-between}
h2{font-weight:900;font-size:19px;line-height:1.25;text-wrap:balance}
h2 span{display:block;font-size:12.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--doux)}
.avance{font-weight:700;color:var(--doux);font-variant-numeric:tabular-nums;white-space:nowrap}
.defile{overflow-x:auto}
table{width:100%;border-collapse:collapse}
th{text-align:left;font-size:12.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--doux);padding:6px 10px 6px 0}
td{vertical-align:top;padding:11px 10px 11px 0;border-top:1px solid var(--bord)}
td:last-child,th:last-child{padding-right:0}
.lot{font-weight:900;font-size:16px;font-variant-numeric:tabular-nums;white-space:nowrap;width:56px}
.titre{font-weight:700;font-size:16px;margin-right:8px}
.type{font-size:12px;font-weight:700;color:var(--doux);border:1px solid var(--bord);border-radius:99px;padding:1px 8px;white-space:nowrap}
td p{color:var(--doux);font-size:13.5px;line-height:1.45;margin-top:3px;max-width:70ch}
code{font-size:.92em;background:var(--fond);border-radius:5px;padding:0 4px;overflow-wrap:anywhere}
.etat{width:128px}
.etat small{display:block;color:var(--doux);font-size:12px;line-height:1.3;margin-top:4px}
.badge{display:inline-block;border-radius:99px;padding:3px 12px;font-size:13px;font-weight:700;white-space:nowrap}
.badge.fait,.point.fait{background:var(--fait-doux);color:var(--fait)}
.badge.cours,.point.cours{background:var(--cours-doux);color:var(--cours)}
.badge.verifier,.point.verifier{background:var(--verifier-doux);color:var(--verifier)}
.badge.faire,.point.faire{background:var(--faire-doux);color:var(--faire)}
.point.fait,.barre .fait{background:var(--fait)}.point.cours,.barre .cours{background:var(--cours)}.point.verifier,.barre .verifier{background:var(--verifier)}.point.faire,.barre .faire{background:var(--faire)}
@media (max-width:560px){section{padding:14px}.lot{width:44px}.etat{width:auto}td p{display:none}tr.ouvert td p{display:block}.titre{display:block}}
</style>

<div class="page">
  <div>
    <h1>Suivi de rafals<i>.</i></h1>
    <p class="doux">D'après <code>.doc/SUIVI-DEV.md</code>, au ${jour}. ${tous.length} lots, du niveau 0 au niveau ${niveaux.length - 1}, et ${HORS_LOT.length} tâches hors lot.</p>
  </div>
  <div class="barre" role="img" aria-label="${total.fait} faits, ${total.verifier} à vérifier, ${total.cours} en cours, ${total.faire} à faire">
    ${['fait', 'verifier', 'cours', 'faire'].map((e) => `<span class="${e}" style="width:${(total[e] / lignes.length) * 100}%"></span>`).join('')}
  </div>
  <div class="filtres" role="group" aria-label="Montrer seulement un état">
    <button type="button" data-f="tout" aria-pressed="true">Tout <b>${lignes.length}</b></button>
    ${['faire', 'cours', 'verifier', 'fait'].map((e) => `<button type="button" data-f="${e}" aria-pressed="false"><span class="point ${e}"></span>${ETATS[e]} <b>${total[e]}</b></button>`).join('')}
  </div>
  <p class="doux" id="vide" hidden>Aucun lot dans cet état.</p>
  ${section('Hors lot', 'Travail en cours', HORS_LOT, false)}
  ${niveaux.map((n) => section(n.nom, n.titre, n.lots, true)).join('\n  ')}
</div>

<script>
  // Filtre par état : cache les lignes des autres états, et les niveaux qui n'ont plus de ligne
  const boutons = document.querySelectorAll('.filtres button')
  function filtrer(f) {
    let vus = 0
    document.querySelectorAll('section').forEach((s) => {
      let n = 0
      s.querySelectorAll('tbody tr').forEach((tr) => {
        tr.hidden = f !== 'tout' && tr.dataset.etat !== f
        if (!tr.hidden) n++
      })
      s.hidden = !n
      vus += n
    })
    document.getElementById('vide').hidden = vus > 0
    boutons.forEach((b) => b.setAttribute('aria-pressed', b.dataset.f === f))
  }
  boutons.forEach((b) => (b.onclick = () => filtrer(b.dataset.f)))
  // Sur téléphone, la description est repliée : un toucher sur la ligne la montre
  document.querySelectorAll('tbody tr').forEach((tr) => (tr.onclick = () => tr.classList.toggle('ouvert')))
</script>
`
fs.writeFileSync(path.join(__dirname, 'suivi-rafals.html'), html)
console.log(tous.length, 'lots', JSON.stringify(total))
