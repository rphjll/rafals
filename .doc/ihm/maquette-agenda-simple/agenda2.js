// Propositions D, E, F : mêmes notions que l'agenda actuel (semaine type, fermetures et ouvertures exceptionnelles).
// Données d'exemple : octobre 2026, Julie, coiffeuse. Aujourd'hui = mercredi 7.
const AUJ = 7, NB = 31
const NOMS = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
const JT = [[9, 12], [14, 19]]
const TYPE = [[], [], JT, JT, JT, JT, JT] // semaine type : fermé dimanche et lundi
// Une période : du jour « de » à l'heure « hd », jusqu'au jour « a » à l'heure « ha »
const F = [{ de: 16, hd: 16, a: 16, ha: 20, motif: 'Dentiste' }, { de: 20, hd: 0, a: 24, ha: 24, motif: 'Congés' }]
const O = [{ de: 18, hd: 10, a: 18, ha: 13, motif: 'Mariage' }]
// Horaires changés pour un seul jour (clic droit ou appui long) : jour → [début, fin]. Passe avant tout le reste.
const H = {}
const RDV = [
  { j: 6, d: 14, f: 14.75, quoi: 'Coupe femme', qui: 'Inès Garcia' },
  { j: 8, d: 10, f: 10.75, quoi: 'Coupe femme', qui: 'Marie Dupont' },
  { j: 8, d: 15, f: 15.5, quoi: 'Brushing', qui: 'Léa Martin', attente: true },
  { j: 13, d: 10, f: 10.75, quoi: 'Coupe femme', qui: 'Sophie Bernard' },
  { j: 16, d: 9.5, f: 11, quoi: 'Couleur', qui: 'Nadia Petit' },
  { j: 18, d: 10.5, f: 12, quoi: 'Coiffure de mariage', qui: 'Camille Roux' },
]
const BADGE = {
  ouvert: ['ouvert', 'ok'], ferme: ['fermé', 'neutre'], partiel: ['partiellement fermé', 'attente'],
  conge: ['fermeture exceptionnelle', 'attente'], plus: ['ouverture exceptionnelle', 'ok'],
}

const Maj = (t) => t[0].toUpperCase() + t.slice(1)
const d2 = (n) => String(n).padStart(2, '0') + '/10/2026'
function heure(x) {
  const e = Math.floor(x)
  return e + ' h ' + String(Math.round((x - e) * 60)).padStart(2, '0')
}
const hc = (x) => (x % 1 ? Math.floor(x) + 'h' + (x % 1) * 60 : String(x))
const court = (p) => p.map(([a, b]) => hc(a) + '-' + hc(b)).join(' · ')
const plagesTexte = (p) => p.map(([a, b]) => heure(a) + ' – ' + heure(b)).join(' · ')
const entier = (p) => p.hd === 0 && p.ha === 24
function periodeTexte(p) {
  if (p.de === p.a) return entier(p) ? d2(p.de) : `${d2(p.de)}, de ${heure(p.hd)} à ${heure(p.ha)}`
  return `Du ${d2(p.de)} au ${d2(p.a)}` + (entier(p) ? '' : ` (de ${heure(p.hd)} à ${heure(p.ha)})`)
}
const enPhrase = (p) => periodeTexte(p).replace(/^D/, 'd')

// Heures d'un jour touchées par une liste de périodes
const duJour = (t, n) => t.filter((p) => p.de <= n && p.a >= n).map((p) => ({ h: [p.de === n ? p.hd : 0, p.a === n ? p.ha : 24], p }))
function moins(pl, [a, b]) {
  return pl.flatMap(([x, y]) => (b <= x || a >= y ? [[x, y]] : [[x, Math.min(a, y)], [Math.max(b, x), y]].filter(([u, v]) => v > u)))
}
function union(pl) {
  const r = []
  ;[...pl].sort((a, b) => a[0] - b[0]).forEach(([a, b]) => {
    const d = r[r.length - 1]
    if (d && a <= d[1]) d[1] = Math.max(d[1], b)
    else r.push([a, b])
  })
  return r
}
function jour(n) {
  const js = (n + 3) % 7, base = TYPE[js], fe = duJour(F, n), ou = duJour(O, n)
  let res = union([...base, ...ou.map((x) => x.h)])
  fe.forEach((f) => (res = moins(res, f.h)))
  const tout = fe.some((f) => f.h[0] <= 0 && f.h[1] >= 24)
  let type = tout ? 'conge' : fe.length ? 'partiel' : ou.length ? 'plus' : base.length ? 'ouvert' : 'ferme'
  const h = H[n]
  if (h) {
    res = [h]
    type = base.length ? 'ouvert' : 'plus'
  }
  return {
    n, js, base, fe: h ? [] : fe, ou: h ? [] : ou, res, type, h, passe: n < AUJ,
    nom: NOMS[js] + ' ' + n + ' octobre', court: NOMS[js].slice(0, 3) + '. ' + n,
    rdv: RDV.filter((r) => r.j === n).sort((a, b) => a.d - b.d),
  }
}
const ligneRdv = (r) => `<li><b>${heure(r.d)} – ${heure(r.f)}</b> · ${r.quoi} · ${r.qui}${r.attente ? ' <span class="badge attente">demande en attente</span>' : ''}</li>`

// Message court en bas de l'écran
let minuterie
function dire(texte) {
  let el = document.getElementById('dire')
  if (!el) {
    el = document.createElement('div')
    el.id = 'dire'
    el.setAttribute('role', 'status')
    document.body.appendChild(el)
  }
  el.textContent = texte
  el.hidden = false
  clearTimeout(minuterie)
  minuterie = setTimeout(() => (el.hidden = true), 3500)
}
document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-info]')
  if (b) dire(b.dataset.info)
})

const LEGENDE = `<div class="legende">
  <span><i></i>Ouvert</span>
  <span><i style="background:var(--ferme)"></i>Fermé</span>
  <span><i style="background:repeating-linear-gradient(45deg,var(--hach1) 0 4px,var(--hach2) 4px 8px)"></i>Fermeture exceptionnelle</span>
  <span><i class="pt"></i>Ouverture exceptionnelle</span>
  <span><b class="pastille" style="border:1px solid var(--bord)">2 rdv</b>Rendez-vous</span>
</div>`
const MOIS_NAV = `<div class="mois">
  <button type="button" class="btn sec petit" data-info="Dans la maquette, seul octobre 2026 est dessiné.">‹ septembre</button>
  <h2>octobre 2026</h2>
  <button type="button" class="btn sec petit" data-info="Dans la maquette, seul octobre 2026 est dessiné.">novembre ›</button>
</div>`
function haut(el) {
  const onglet = 'Onglet inchangé : la maquette ne dessine que « Calendrier ».'
  const metier = 'Dans la maquette, seul le calendrier « Coiffeuse » est dessiné.'
  el.innerHTML = `<div class="onglets">
    <button type="button" class="actif">Calendrier</button>
    <button type="button" data-info="${onglet}">Rendez-vous <span class="compteur">1</span></button>
    <button type="button" data-info="${onglet}">Paiements</button>
  </div>
  <div class="barre">
    <div class="segment">
      <button type="button" class="actif">Coiffeuse</button>
      <button type="button" data-info="${metier}">Maquilleuse</button>
      <button type="button" data-info="${metier}">Mes rendez-vous de client</button>
    </div>
    <div class="boutons">
      <button type="button" class="btn sec" data-info="Ouvre la fenêtre « Semaine type — Coiffeuse », inchangée.">Semaine type</button>
      <button type="button" class="btn sec" data-info="Ouvre la fenêtre « Réglages », inchangée.">Réglages</button>
    </div>
  </div>`
}

// Le mois, avec les mêmes informations dans les cases que l'agenda actuel. o.choisis, o.clic(n)
function grille(el, o) {
  let s = ['lun', 'mar', 'mer', 'jeu', 'ven', 'sam', 'dim'].map((c) => `<div class="tete">${c}</div>`).join('') + '<div></div>'.repeat(3)
  for (let n = 1; n <= NB; n++) {
    const j = jour(n), c = o.choisis.includes(n)
    let dedans = `<b>${n}</b>`
    if (j.type === 'partiel')
      j.fe.forEach((f) => {
        const a = Math.max(f.h[0], 7), b = Math.min(f.h[1], 21)
        if (b > a) dedans = `<span class="bande" style="left:${((a - 7) / 14) * 100}%;width:${((b - a) / 14) * 100}%"></span>` + dedans
      })
    if (j.h) dedans += `<span class="eti"><i class="long">ce jour : ${court([j.h])}</i><i class="bref">${court([j.h])}</i></span>`
    else if (j.base.length && j.type !== 'conge') dedans += `<span class="hh">${court(j.base)}</span>`
    if (j.type === 'conge') dedans += '<span class="eti"><i class="long">fermé (exceptionnel)</i><i class="bref">fermé</i></span>'
    if (j.type === 'partiel') dedans += '<span class="eti"><i class="long">partiellement fermé</i><i class="bref">partiel</i></span>'
    if (j.ou.length && j.type !== 'conge') dedans += `<span class="eti"><i class="long">+ ${court(j.ou.map((x) => x.h))}</i><i class="bref">+ ouvert</i></span>`
    if (j.rdv.length) dedans += `<span class="pastille">${j.rdv.length}<i> rdv</i></span>`
    const dessin = j.type === 'partiel' ? 'ouvert' : j.type === 'plus' ? 'plus' : j.type
    s += `<button type="button" class="case ${dessin}${j.ou.length && j.type !== 'conge' ? ' plus' : ''}${j.passe ? ' passe' : ''}${c ? ' choisi' : ''}${n === AUJ ? ' auj' : ''}" data-n="${n}" aria-pressed="${c}" aria-label="${j.nom}, ${BADGE[j.type][0]}${j.rdv.length ? ', ' + j.rdv.length + ' rendez-vous' : ''}">${dedans}</button>`
  }
  el.innerHTML = s
  el.onclick = (e) => {
    const b = e.target.closest('.case')
    if (b) o.clic(+b.dataset.n)
  }
}

function retirer(code) {
  const s = code[0]
  if (s === 'H') {
    delete H[+code.slice(1)]
    return dire('Horaires habituels remis pour ce jour.')
  }
  ;(s === 'F' ? F : O).splice(+code.slice(1), 1)
  dire(s === 'F' ? 'Fermeture retirée : ces horaires sont de nouveau réservables.' : 'Ouverture retirée : ces horaires ne sont plus réservables.')
}
function ecouterRetirer(el, maj) {
  el.onclick = (e) => {
    const b = e.target.closest('[data-r]')
    if (!b) return
    retirer(b.dataset.r)
    maj()
  }
}

// Détail du jour choisi, écrit comme dans l'agenda actuel
function detailJour(el, n, maj) {
  const j = jour(n)
  let s = `<div class="ligne"><h3>${Maj(j.nom)}</h3><span class="badge ${BADGE[j.type][1]}">${BADGE[j.type][0]}</span></div>`
  s += `<p>${j.base.length ? plagesTexte(j.base) + ' (semaine type)' : 'Fermé ce jour-là (semaine type).'}</p>`
  j.fe.forEach((f) => (s += `<p class="t-fer">${f.h[0] <= 0 && f.h[1] >= 24 ? 'Fermé : ' + periodeTexte(f.p) : `Fermé de ${heure(f.h[0])} à ${heure(f.h[1])}`}${f.p.motif ? ' · ' + f.p.motif : ''}</p>`))
  j.ou.forEach((o) => (s += `<p class="t-ouv">Ouvert en plus de ${heure(o.h[0])} à ${heure(o.h[1])}${o.p.motif ? ' · ' + o.p.motif : ''}</p>`))
  if (j.type !== 'conge') s += `<p><b>Réservable :</b> ${j.res.length ? plagesTexte(j.res) : 'aucune heure'}</p>`
  s += '<h4>Rendez-vous</h4>' + (j.rdv.length ? `<ul class="rdv">${j.rdv.map(ligneRdv).join('')}</ul>` : '<p class="doux">Aucun rendez-vous ce jour-là.</p>')
  if (!j.passe && (j.fe.length || j.ou.length)) {
    s += '<div class="boutons">'
    j.fe.forEach((f) => (s += `<button type="button" class="btn danger" data-r="F${F.indexOf(f.p)}">Retirer la fermeture (${enPhrase(f.p)})</button>`))
    j.ou.forEach((o) => (s += `<button type="button" class="btn danger" data-r="O${O.indexOf(o.p)}">Retirer l'ouverture (${enPhrase(o.p)})</button>`))
    s += '</div>'
  }
  el.innerHTML = s
  ecouterRetirer(el, maj)
}

// Liste des fermetures (s = 'F') ou des ouvertures (s = 'O') à venir ; renvoie leur nombre
function listes(el, s, maj) {
  const l = (s === 'F' ? F : O).map((p, i) => [p, i]).filter(([p]) => p.a >= AUJ).sort((x, y) => x[0].de - y[0].de)
  // Les jours aux horaires changés : dans les fermetures si le jour est ouvert d'habitude, sinon dans les ouvertures
  const hs = Object.keys(H).map(Number).filter((n) => n >= AUJ && TYPE[(n + 3) % 7].length > 0 === (s === 'F')).sort((x, y) => x - y)
  const lignes = l.map(([p, i]) => `<li><span><b>${periodeTexte(p)}</b>${p.motif ? `<br><span class="doux">${p.motif}</span>` : ''}</span><button type="button" class="btn danger petit" data-r="${s}${i}">Retirer</button></li>`)
    .concat(hs.map((n) => `<li><span><b>${d2(n)}</b><br><span class="doux">${s === 'F' ? 'Ouvert seulement' : 'Ouvert'} de ${heure(H[n][0])} à ${heure(H[n][1])}</span></span><button type="button" class="btn danger petit" data-r="H${n}">Retirer</button></li>`))
  el.innerHTML = lignes.length
    ? `<ul class="periodes">${lignes.join('')}</ul>`
    : `<p class="doux">Aucune ${s === 'F' ? 'fermeture' : 'ouverture'} à venir.</p>`
  ecouterRetirer(el, maj)
  return lignes.length
}

// Fenêtre « Fermeture exceptionnelle » / « Ouverture exceptionnelle », déjà remplie avec les jours de « de » à « a »
function fenetre(s, de, a, maj) {
  const ferm = s === 'F'
  de = Math.max(de, AUJ)
  a = Math.max(a, de)
  const jours = (v) => {
    let r = ''
    for (let n = AUJ; n <= NB; n++) r += `<option value="${n}"${n === v ? ' selected' : ''}>${jour(n).court} · ${d2(n)}</option>`
    return r
  }
  const hs = (v, x0, x1) => {
    let r = ''
    for (let x = x0; x <= x1; x += 0.25) r += `<option value="${x}"${x === v ? ' selected' : ''}>${heure(x)}</option>`
    return r
  }
  const v = document.createElement('div')
  v.className = 'voile'
  v.innerHTML = `<div class="fenetre" role="dialog" aria-modal="true" aria-labelledby="f-titre">
    <h2 id="f-titre">${ferm ? 'Fermeture' : 'Ouverture'} exceptionnelle</h2>
    <div class="champs">
      <label for="f-de">Du * <select id="f-de">${jours(de)}</select></label>
      <label for="f-hd">à * <select id="f-hd">${hs(ferm ? 0 : 9, 0, 23.75)}</select></label>
      <label for="f-a">Jusqu'au * <select id="f-a">${jours(a)}</select></label>
      <label for="f-ha">à * <select id="f-ha">${hs(ferm ? 24 : 12, 0.25, 24)}</select></label>
    </div>
    <p class="doux" id="f-un">Un seul jour : seules ces heures sont concernées.</p>
    <label for="f-motif">Motif (pour vous seul) <input type="text" id="f-motif" maxlength="120"></label>
    <p class="doux">${ferm ? 'Les clients ne verront plus d\'horaires pendant cette période.' : 'Les clients pourront réserver pendant ces heures, même si votre semaine type est fermée. Une fermeture exceptionnelle passe avant.'}</p>
    <p class="erreur" id="f-err" hidden>La fin doit être après le début.</p>
    <div class="boutons"><button type="button" class="btn" id="f-ok"></button><button type="button" class="btn sec" id="f-non">Annuler</button></div>
  </div>`
  document.body.appendChild(v)
  const q = (id) => v.querySelector('#' + id)
  const lire = () => {
    const p = { de: +q('f-de').value, hd: +q('f-hd').value, a: +q('f-a').value, ha: +q('f-ha').value, motif: q('f-motif').value.trim() }
    q('f-un').hidden = p.de !== p.a
    q('f-ok').textContent = (ferm ? 'Fermer : ' : 'Ouvrir : ') + enPhrase(p)
    return p
  }
  const clavier = (e) => e.key === 'Escape' && fermer()
  const fermer = () => {
    v.remove()
    document.removeEventListener('keydown', clavier)
  }
  document.addEventListener('keydown', clavier)
  v.onchange = lire
  lire()
  v.onclick = (e) => e.target === v && fermer()
  q('f-non').onclick = fermer
  q('f-ok').onclick = () => {
    const p = lire()
    if (p.a < p.de || (p.a === p.de && p.ha <= p.hd)) return void (q('f-err').hidden = false)
    ;(ferm ? F : O).push(p)
    fermer()
    dire((ferm ? 'Fermeture' : 'Ouverture') + ' enregistrée : ' + enPhrase(p) + '.')
    maj()
  }
  q('f-de').focus()
}

// Fenêtre « Horaires du mardi 27 octobre » (clic droit sur un jour, appui long sur téléphone) : les heures de ce jour seul
function fenetreHoraires(n, maj) {
  const j = jour(n)
  if (j.passe) return dire('Ce jour est passé : ses horaires ne se changent plus.')
  const depart = j.res.length ? [j.res[0][0], j.res[j.res.length - 1][1]] : [9, 12]
  const hs = (v, x0, x1) => {
    let r = ''
    for (let x = x0; x <= x1; x += 0.25) r += `<option value="${x}"${x === v ? ' selected' : ''}>${heure(x)}</option>`
    return r
  }
  const v = document.createElement('div')
  v.className = 'voile'
  v.innerHTML = `<div class="fenetre" role="dialog" aria-modal="true" aria-labelledby="h-titre">
    <h2 id="h-titre">Horaires du ${j.nom}</h2>
    <p class="doux">D'habitude : ${j.base.length ? plagesTexte(j.base) : 'fermé'}. Ces horaires valent pour ce jour seulement.</p>
    <div class="champs" style="grid-template-columns:1fr 1fr">
      <label for="h-de">Ouvert de * <select id="h-de">${hs(depart[0], 0, 23.75)}</select></label>
      <label for="h-a">à * <select id="h-a">${hs(depart[1], 0.25, 24)}</select></label>
    </div>
    <p class="erreur" id="h-err" hidden>La fin doit être après le début.</p>
    <div class="boutons">
      <button type="button" class="btn" id="h-ok"></button>
      ${j.h ? '<button type="button" class="btn sec" id="h-habituel">Remettre les horaires habituels</button>' : ''}
      <button type="button" class="btn sec" id="h-non">Annuler</button>
    </div>
  </div>`
  document.body.appendChild(v)
  const q = (id) => v.querySelector('#' + id)
  const lire = () => {
    const p = [+q('h-de').value, +q('h-a').value]
    q('h-ok').textContent = `Enregistrer : ${d2(n)}, de ${heure(p[0])} à ${heure(p[1])}`
    return p
  }
  const clavier = (e) => e.key === 'Escape' && fermer()
  const fermer = () => {
    v.remove()
    document.removeEventListener('keydown', clavier)
  }
  document.addEventListener('keydown', clavier)
  v.onchange = lire
  lire()
  v.onclick = (e) => e.target === v && fermer()
  q('h-non').onclick = fermer
  if (j.h) q('h-habituel').onclick = () => { retirer('H' + n); fermer(); maj() }
  q('h-ok').onclick = () => {
    const p = lire()
    if (p[1] <= p[0]) return void (q('h-err').hidden = false)
    H[n] = p
    fermer()
    dire(`Horaires enregistrés : ${d2(n)}, de ${heure(p[0])} à ${heure(p[1])}.`)
    maj()
  }
  q('h-de').focus()
}
