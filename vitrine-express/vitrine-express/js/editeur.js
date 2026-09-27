// ============================================================
//  L'ÉDITEUR : relie le formulaire à l'aperçu en direct
// ============================================================

document.querySelectorAll(".nom-service").forEach(el => el.textContent = CONFIG.nomService);

const apercu = document.getElementById("apercu");
const selectModele = document.getElementById("modele");
const champs = document.querySelectorAll("[data-champ]");

// Le modèle et le style demandés dans l'adresse (editeur.html?modele=duo&variante=menthe)
const params = new URLSearchParams(location.search);
let modeleActuel = "classique";

// Les infos du client (textes, photos, style, disposition…)
let donnees = {};

// ---------- Sauvegarde sur l'appareil ----------
// Un seul projet : changer de modèle garde tout ce que le client a écrit.
// (si le navigateur bloque la sauvegarde, l'éditeur marche quand même)

const CLE_SAUVEGARDE = "vitrine-express-projet";

function sauvegarder() {
  try {
    localStorage.setItem(CLE_SAUVEGARDE, JSON.stringify({ modele: modeleActuel, donnees }));
  } catch (e) {
    // Trop de photos pour la mémoire du navigateur : on garde au moins les textes
    try {
      const sansPhotos = { ...donnees, photoHero: "", galerie: [] };
      localStorage.setItem(CLE_SAUVEGARDE, JSON.stringify({ modele: modeleActuel, donnees: sansPhotos }));
    } catch (e2) { /* sauvegarde impossible, pas grave */ }
  }
}

function charger() {
  let sauve = null;
  try { sauve = JSON.parse(localStorage.getItem(CLE_SAUVEGARDE)); } catch (e) {}
  const demande = params.get("modele");
  modeleActuel = MODELES[demande] ? demande : (sauve && MODELES[sauve.modele] ? sauve.modele : "classique");

  if (sauve && sauve.donnees) {
    donnees = { ...copieOptions(), photoHero: "", galerie: [], ...sauve.donnees };
    // Nouveau modèle demandé depuis l'accueil : on prend son style, on garde les textes
    if (demande && demande !== sauve.modele) choisirVariante(params.get("variante"), false);
  } else {
    // Premier passage : les textes d'exemple du métier associé au modèle
    donnees = { ...copieOptions(), photoHero: "", galerie: [], ...donneesExemple(modeleActuel) };
  }
  if (params.get("variante")) choisirVariante(params.get("variante"), false);
  if (!METIERS[donnees.metier]) donnees.metier = MODELES[modeleActuel].exemple;
}

// Applique un style (sous-modèle) du modèle actuel
function choisirVariante(idVariante, rafraichir = true) {
  const v = varianteDe(modeleActuel, { variante: idVariante });
  donnees.variante = v.id;
  donnees.couleur = v.couleur;
  donnees.fondStyle = "modele";
  donnees.ecriture = "modele";
  donnees.entete = "auto";
  if (!rafraichir) return;
  document.getElementById("couleur").value = v.couleur;
  rafraichirOptions();
  miseAJour(true);
}

// Une copie neuve des réglages de style par défaut
function copieOptions() { return JSON.parse(JSON.stringify(OPTIONS_PAR_DEFAUT)); }

// ---------- Formulaire <-> données ----------

function remplirFormulaire() {
  champs.forEach(c => { c.value = donnees[c.dataset.champ] || ""; });
  selectModele.value = modeleActuel;
  afficherMetierActuel();
  remplirTitres();
  afficherVignettes();
  rafraichirOptions();
}

champs.forEach(c => {
  c.addEventListener("input", () => {
    donnees[c.dataset.champ] = c.value;
    if (c.id === "couleur") rafraichirOptions();
    // Les parties vides (sans texte, sans tarif) sont signalées dans l'onglet Disposition
    if (["description", "services", "adresse"].includes(c.id)) afficherParties();
    miseAJour();
  });
});

// ---------- Les onglets ----------

document.querySelectorAll(".onglet").forEach(bouton => {
  bouton.addEventListener("click", () => {
    document.querySelectorAll(".onglet").forEach(b => b.classList.toggle("actif", b === bouton));
    document.querySelectorAll(".page-onglet").forEach(p => p.hidden = p.dataset.page !== bouton.dataset.onglet);
  });
});

// ---------- Onglet Style ----------

// Charge les polices pour montrer un aperçu de chaque style d'écriture
(function chargerPolices() {
  const lien = document.createElement("link");
  lien.rel = "stylesheet";
  lien.href = "https://fonts.googleapis.com/css2?" +
    Object.values(ECRITURES).map(e => e.polices).join("&") + "&display=swap";
  document.head.appendChild(lien);
})();

// Couleurs rapides
const COULEURS_RAPIDES = [
  ["#c9a227", "Or"], ["#e4572e", "Orange"], ["#dc2626", "Rouge"], ["#d9678a", "Rose"],
  ["#a855f7", "Violet"], ["#2563eb", "Bleu"], ["#0891b2", "Turquoise"], ["#15803d", "Vert"],
  ["#6b8e23", "Olive"], ["#8a5a3b", "Marron"], ["#1e3a5f", "Bleu marine"], ["#334155", "Gris ardoise"]
];
const zoneCouleurs = document.getElementById("couleurs-rapides");
COULEURS_RAPIDES.forEach(([hex, nom]) => {
  const rond = document.createElement("button");
  rond.type = "button";
  rond.className = "rapide";
  rond.style.background = hex;
  rond.title = nom;
  rond.setAttribute("aria-label", nom);
  rond.dataset.couleur = hex;
  rond.addEventListener("click", () => {
    donnees.couleur = hex;
    document.getElementById("couleur").value = hex;
    rafraichirOptions();
    miseAJour();
  });
  zoneCouleurs.appendChild(rond);
});

// Couleurs de fond
const zoneFond = document.getElementById("choix-fond");
[["modele", { nom: "Du modèle" }], ...Object.entries(FONDS)].forEach(([id, f]) => {
  const b = document.createElement("button");
  b.type = "button";
  b.dataset.valeur = id;
  b.innerHTML = `<span class="pastille-fond"></span>${f.nom}`;
  zoneFond.appendChild(b);
});

// Styles d'écriture
const zoneEcriture = document.getElementById("choix-ecriture");
[["modele", { nom: "Du modèle", titre: "inherit" }], ...Object.entries(ECRITURES)].forEach(([id, e]) => {
  const b = document.createElement("button");
  b.type = "button";
  b.dataset.valeur = id;
  b.innerHTML = `<span class="apercu-police" style="font-family:${e.titre};${e.majuscules ? "text-transform:uppercase" : ""}">Bonjour</span><small>${e.nom}</small>`;
  zoneEcriture.appendChild(b);
});

// Ambiances prêtes
const zoneAmbiances = document.getElementById("ambiances");
AMBIANCES.forEach(a => {
  const f = FONDS[a.fondStyle];
  const fond = f.fond === "TEINTE" ? `color-mix(in srgb, ${a.couleur} 12%, #fff)` : f.fond;
  const e = ECRITURES[a.ecriture];
  const b = document.createElement("button");
  b.type = "button";
  b.className = "ambiance";
  b.innerHTML = `
    <div class="echantillon" style="background:${fond};color:${f.encre}">
      <i style="background:${a.couleur}"></i><b style="font-family:${e.titre}">Aa</b>
    </div>
    <span>${a.nom}</span>`;
  b.addEventListener("click", () => {
    Object.assign(donnees, { couleur: a.couleur, fondStyle: a.fondStyle, ecriture: a.ecriture, entete: a.entete });
    document.getElementById("couleur").value = a.couleur;
    rafraichirOptions();
    miseAJour(true);
  });
  zoneAmbiances.appendChild(b);
});

// Tous les boutons "à choix" : un clic = on garde ce choix
document.querySelectorAll("[data-option]").forEach(zone => {
  zone.addEventListener("click", e => {
    const b = e.target.closest("button[data-valeur]");
    if (!b) return;
    donnees[zone.dataset.option] = b.dataset.valeur;
    rafraichirOptions();
    miseAJour(true);
  });
});

document.getElementById("reinitialiser-style").addEventListener("click", () => {
  const d = copieOptions();
  ["fondStyle", "ecriture", "entete", "tailleTexte", "boutons"].forEach(k => donnees[k] = d[k]);
  donnees.couleur = varianteDe(modeleActuel, donnees).couleur;
  document.getElementById("couleur").value = donnees.couleur;
  rafraichirOptions();
  miseAJour(true);
});

// ---------- Mode "Déplacer / agrandir" ----------

let modeMain = false;
const boutonsMain = document.querySelectorAll("[data-bascule-main]");

function basculerModeMain(actif = !modeMain) {
  modeMain = actif;
  document.getElementById("panneau-main").hidden = !modeMain;
  document.body.classList.toggle("mode-main", modeMain);
  document.getElementById("annuler").hidden = !modeMain;
  elementChoisi = null;
  afficherPanneauMain();
  boutonsMain.forEach(b => {
    if (b.closest(".panneau-main")) return;
    b.classList.toggle("actif", modeMain);
    b.textContent = modeMain
      ? "✅ J'ai fini"
      : (b.id === "bouton-main" ? "✋ Déplacer / agrandir" : "✋ Déplacer et agrandir les éléments");
  });
  // Sur téléphone, on remonte jusqu'à l'aperçu pour qu'il soit bien visible
  if (modeMain && window.innerWidth < 900) document.querySelector(".zone-apercu").scrollIntoView({ behavior: "smooth" });
  miseAJour(true);
}
boutonsMain.forEach(b => b.addEventListener("click", () => basculerModeMain()));

// Bouton "Annuler" : on garde les dernières versions de la disposition
const historique = [];
function memoriser() {
  historique.push(JSON.stringify({
    ajustements: donnees.ajustements || {}, ordre: donnees.ordre, cache: donnees.cache || [], titres: donnees.titres || {}
  }));
  if (historique.length > 50) historique.shift();
  document.getElementById("annuler").disabled = false;
}
document.getElementById("annuler").addEventListener("click", () => {
  const precedent = historique.pop();
  if (!precedent) return;
  Object.assign(donnees, JSON.parse(precedent));
  document.getElementById("annuler").disabled = historique.length === 0;
  remplirTitres();
  afficherParties();
  miseAJour(true);
});
document.getElementById("annuler").disabled = true;

// Messages envoyés par l'aperçu quand on déplace quelque chose
window.addEventListener("message", e => {
  if (e.source !== apercu.contentWindow || !e.data || e.data.source !== "vitrine-edit") return;
  const m = e.data;

  if (m.type === "pret" && elementChoisi) {
    // L'aperçu vient d'être rechargé : on re-sélectionne le même élément
    envoyerAApercu({ type: "choisir", id: elementChoisi.id });
  }
  if (m.type === "choisi") {
    elementChoisi = m.info;
    afficherPanneauMain();
  }
  if (m.type === "ajuster") {
    memoriser();
    donnees.ajustements = { ...(donnees.ajustements || {}), [m.id]: { x: m.x, y: m.y, z: m.z } };
    sauvegarder();             // l'aperçu est déjà à jour, pas besoin de le recharger
  }
  if (m.type === "remettre") {
    memoriser();
    const a = { ...(donnees.ajustements || {}) };
    delete a[m.id];
    donnees.ajustements = a;
    sauvegarder();
  }
  if (m.type === "renommer") {
    memoriser();
    donnees.titres = { ...(donnees.titres || {}), [m.partie]: m.titre };
    miseAJour(true);
  }
  if (m.type === "ordre") {
    memoriser();
    donnees.ordre = [...m.ordre, ...ordreComplet().filter(id => !m.ordre.includes(id))];
    miseAJour(true);
  }
  if (m.type === "cacher") {
    memoriser();
    donnees.cache = [...new Set([...(donnees.cache || []), m.id])];
    afficherParties();
    miseAJour(true);
  }
});

// ---------- Le panneau avec les gros boutons ----------

let elementChoisi = null;   // { id, partie, premiere, derniere }

// Des noms simples pour dire au client ce qu'il est en train de modifier
const NOMS_ELEMENTS = {
  "hero-titre": "le grand titre", "hero-texte": "la phrase d'accroche", "hero-boutons": "les boutons du haut",
  "apropos-titre": "le titre « À propos »", "apropos-texte": "le texte de présentation",
  "services-titre": "le titre des tarifs", "services-liste": "la liste des prix",
  "galerie-titre": "le titre des photos", "galerie-photos": "les photos",
  "horaires": "les horaires", "contact": "le contact", "carte": "le plan", "hero-infos": "la carte de contact"
};

function envoyerAApercu(msg) {
  msg.source = "vitrine-editeur";
  try { apercu.contentWindow.postMessage(msg, "*"); } catch (e) {}
}

function nomPartie(id) {
  const L = libellesDe(donnees);
  return ((donnees.titres || {})[id] || titresDeBase(L)[id]);
}

function afficherPanneauMain() {
  const c = elementChoisi;
  document.getElementById("pm-attente").hidden = !!c;
  document.getElementById("pm-outils").hidden = !c;
  if (!c) return;
  let nom = NOMS_ELEMENTS[c.id] || "cet élément";
  if (/-titre$/.test(c.id) && c.id !== "hero-titre") nom = "le titre « " + nomPartie(c.id.replace(/-titre$/, "")) + " »";
  document.getElementById("pm-nom").textContent = nom;
  document.getElementById("pm-partie").hidden = !c.partie;
  if (c.partie) {
    document.getElementById("pm-nom-partie").textContent = nomPartie(c.partie);
  }
  document.getElementById("pm-renommer").hidden = !(/-titre$/.test(c.id) && c.id !== "hero-titre");
}

// Change la taille ou la position de l'élément choisi
function ajusterChoisi(changer) {
  const id = elementChoisi.id;
  const a = { x: 0, y: 0, z: 1, ...((donnees.ajustements || {})[id] || {}) };
  changer(a);
  a.z = Math.round(Math.min(3, Math.max(0.4, a.z)) * 100) / 100;
  a.x = Math.round(a.x * 100) / 100;
  memoriser();
  donnees.ajustements = { ...(donnees.ajustements || {}), [id]: a };
  envoyerAApercu({ type: "appliquer", id, x: a.x, y: a.y, z: a.z });
  sauvegarder();
}

document.querySelectorAll("[data-cmd]").forEach(b => b.addEventListener("click", () => {
  if (!elementChoisi) return;
  const c = elementChoisi;
  switch (b.dataset.cmd) {
    case "plus-grand": ajusterChoisi(a => a.z *= 1.12); break;
    case "plus-petit": ajusterChoisi(a => a.z /= 1.12); break;
    case "gauche":     ajusterChoisi(a => a.x -= 3); break;
    case "droite":     ajusterChoisi(a => a.x += 3); break;
    case "haut":       ajusterChoisi(a => a.y -= 15); break;
    case "bas":        ajusterChoisi(a => a.y += 15); break;

    case "remettre": {
      memoriser();
      const a = { ...(donnees.ajustements || {}) };
      delete a[c.id];
      donnees.ajustements = a;
      envoyerAApercu({ type: "appliquer", id: c.id, x: 0, y: 0, z: 1 });
      sauvegarder();
      break;
    }
    case "cacher": {
      if (!confirm("Cacher toute la rubrique « " + nomPartie(c.partie) + " » ?\n\nVous pourrez la réafficher avec le bouton « 👁 Réafficher » juste ici.")) break;
      memoriser();
      donnees.cache = [...new Set([...(donnees.cache || []), c.partie])];
      elementChoisi = null;
      afficherPanneauMain();
      afficherParties();
      miseAJour(true);
      break;
    }
    case "renommer": {
      const partie = c.id.replace(/-titre$/, "");
      const nouveau = prompt("Nouveau titre :", nomPartie(partie));
      if (nouveau === null || !nouveau.trim()) break;
      memoriser();
      donnees.titres = { ...(donnees.titres || {}), [partie]: nouveau.trim() };
      afficherPanneauMain();
      remplirTitres();
      miseAJour(true);
      break;
    }
    case "autre":
      elementChoisi = null;
      envoyerAApercu({ type: "deselectionner" });
      afficherPanneauMain();
      break;
  }
}));

// ---------- Onglet Textes : les noms des rubriques ----------

const ICONES_RUBRIQUES = { apropos: "💬", services: "💶", galerie: "📷", infos: "🕒", plan: "📍" };

function remplirTitres() {
  const zone = document.getElementById("champs-titres");
  const L = libellesDe(donnees);
  const base = titresDeBase(L);
  const titres = donnees.titres || {};
  // On ne reconstruit pas les champs si le client est en train d'écrire dedans
  if (zone.contains(document.activeElement)) return;
  zone.innerHTML = "";
  OPTIONS_PAR_DEFAUT.ordre.forEach(id => {
    const ligne = document.createElement("label");
    ligne.className = "champ-titre";
    ligne.innerHTML = `<span class="ico">${ICONES_RUBRIQUES[id]}</span><input type="text" placeholder="${echapper(base[id])}" aria-label="Nom de la rubrique ${echapper(base[id])}">`;
    const champ = ligne.querySelector("input");
    champ.value = titres[id] || "";
    champ.addEventListener("input", () => {
      donnees.titres = { ...(donnees.titres || {}), [id]: champ.value };
      afficherOrdre();
      miseAJour();
    });
    zone.appendChild(ligne);
  });
}

// ---------- Mode Déplacer : l'ordre des rubriques, à faire glisser ----------

function afficherOrdre() {
  const liste = document.getElementById("liste-ordre");
  if (!liste || liste.querySelector(".en-glisse")) return;   // pas pendant un glissement
  const visibles = rubriquesVisibles({ ...OPTIONS_PAR_DEFAUT, ...donnees });
  liste.innerHTML = "";
  visibles.forEach((id, i) => {
    const li = document.createElement("li");
    li.className = "rubrique";
    li.dataset.id = id;
    li.innerHTML = `<span class="poignee-ordre">⋮⋮</span><span class="num">${i + 1}</span>
      <span>${ICONES_RUBRIQUES[id]} ${echapper(nomPartie(id))}</span>`;
    li.addEventListener("pointerdown", e => commencerGlisse(e, li));
    liste.appendChild(li);
  });
}

// Glisser une rubrique (souris ou doigt) : elle suit le pointeur,
// les autres se décalent, et au lâcher le site prend le nouvel ordre.
// Important : on ne déplace JAMAIS la rubrique tenue dans la page (seulement ses voisines),
// sinon le navigateur la "lâche" en plein geste.
let glisseEnCours = null;

function commencerGlisse(e, li) {
  if (e.button > 0 || glisseEnCours) return;
  e.preventDefault();
  const liste = li.parentElement;
  const ecart = parseFloat(getComputedStyle(liste).rowGap) || 6;
  glisseEnCours = { li, liste, departY: e.clientY, pointeur: e.pointerId };
  li.classList.add("en-glisse");
  document.addEventListener("pointermove", bougerGlisse);
  document.addEventListener("pointerup", finGlisse);
  document.addEventListener("pointercancel", finGlisse);

  function bougerGlisse(ev) {
    if (ev.pointerId !== glisseEnCours.pointeur) return;
    ev.preventDefault();
    let dy = ev.clientY - glisseEnCours.departY;
    // On peut passer plusieurs rubriques d'un coup si le geste est rapide
    for (let securite = 0; securite < 10; securite++) {
      const apres = li.nextElementSibling, avant = li.previousElementSibling;
      if (apres && dy > apres.offsetHeight / 2) {
        liste.insertBefore(apres, li);                 // la voisine du dessous passe au-dessus
        glisseEnCours.departY += apres.offsetHeight + ecart;
      } else if (avant && dy < -avant.offsetHeight / 2) {
        liste.insertBefore(avant, li.nextSibling);     // la voisine du dessus passe en dessous
        glisseEnCours.departY -= avant.offsetHeight + ecart;
      } else break;
      dy = ev.clientY - glisseEnCours.departY;
    }
    // La rubrique tenue ne sort pas de la liste
    const premier = liste.firstElementChild === li, dernier = liste.lastElementChild === li;
    if (premier && dy < 0) dy = Math.max(dy, -12);
    if (dernier && dy > 0) dy = Math.min(dy, 12);
    li.style.transform = `translateY(${dy}px)`;
    liste.querySelectorAll(".num").forEach((n, i) => n.textContent = i + 1);
  }

  function finGlisse(ev) {
    if (ev.pointerId !== glisseEnCours.pointeur) return;
    document.removeEventListener("pointermove", bougerGlisse);
    document.removeEventListener("pointerup", finGlisse);
    document.removeEventListener("pointercancel", finGlisse);
    li.classList.remove("en-glisse");
    li.style.transform = "";
    glisseEnCours = null;

    const nouvelOrdre = [...liste.children].map(x => x.dataset.id);
    const ancien = rubriquesVisibles({ ...OPTIONS_PAR_DEFAUT, ...donnees });
    if (nouvelOrdre.join() === ancien.join()) return;
    memoriser();
    // Les rubriques cachées ou vides gardent leur place ; les autres prennent le nouvel ordre
    let k = 0;
    donnees.ordre = ordreComplet().map(id => (ancien.includes(id) ? nouvelOrdre[k++] : id));
    miseAJour(true);
  }
}

function ordreComplet() {
  const toutes = OPTIONS_PAR_DEFAUT.ordre;
  const o = (donnees.ordre || []).filter(id => toutes.includes(id));
  return [...o, ...toutes.filter(id => !o.includes(id))];
}

// Onglet Disposition : les parties cachées, avec un bouton pour les réafficher
// Les rubriques cachées apparaissent à 2 endroits (onglet Disposition + panneau du mode Déplacer)
function afficherParties() {
  afficherOrdre();
  const L = libellesDe(donnees);
  const base = titresDeBase(L);
  const cache = donnees.cache || [];
  document.getElementById("zone-cachees").hidden = cache.length === 0;
  document.getElementById("pm-cachees").hidden = cache.length === 0;

  [document.getElementById("liste-cachees"), document.getElementById("pm-liste-cachees")].forEach(zone => {
    zone.innerHTML = "";
    cache.forEach(id => {
      const b = document.createElement("button");
      b.type = "button";
      b.textContent = "👁 Réafficher « " + ((donnees.titres || {})[id] || base[id]) + " »";
      b.addEventListener("click", () => {
        memoriser();
        donnees.cache = (donnees.cache || []).filter(x => x !== id);
        afficherParties();
        miseAJour(true);
      });
      zone.appendChild(b);
    });
  });
}

document.getElementById("tout-remettre").addEventListener("click", () => {
  if (!confirm("Remettre tous les éléments et toutes les parties à leur place d'origine ?")) return;
  memoriser();
  const d = copieOptions();
  donnees.ajustements = {};
  donnees.ordre = d.ordre;
  donnees.cache = [];
  afficherParties();
  miseAJour(true);
});

// Met à jour tous les boutons pour montrer les choix actuels
function rafraichirOptions() {
  document.querySelectorAll("[data-option]").forEach(zone => {
    const valeur = donnees[zone.dataset.option] || OPTIONS_PAR_DEFAUT[zone.dataset.option];
    zone.querySelectorAll("button[data-valeur]").forEach(b => b.classList.toggle("actif", b.dataset.valeur === valeur));
  });
  document.querySelectorAll(".rapide").forEach(r =>
    r.classList.toggle("actif", (donnees.couleur || "").toLowerCase() === r.dataset.couleur));

  // Petits aperçus des fonds (le fond "Du modèle" dépend du modèle choisi)
  const theme = styleDe(modeleActuel, { ...donnees, fondStyle: "modele", ecriture: "modele" });
  afficherVariantes();
  zoneFond.querySelectorAll("button").forEach(b => {
    const f = b.dataset.valeur === "modele" ? theme : FONDS[b.dataset.valeur];
    const fond = f.fond === "TEINTE" ? `color-mix(in srgb, ${donnees.couleur} 12%, #fff)` : f.fond;
    const pastille = b.querySelector(".pastille-fond");
    pastille.style.background = fond;
    pastille.style.color = f.encre;
    pastille.textContent = "Aa";
  });
  const pModele = zoneEcriture.querySelector('[data-valeur="modele"] .apercu-police');
  pModele.style.fontFamily = theme.titre;
  pModele.style.textTransform = theme.majuscules ? "uppercase" : "none";

  afficherParties();
}

// ---------- Choix du modèle, du style et du métier ----------

for (const [id, m] of Object.entries(MODELES)) {
  const opt = document.createElement("option");
  opt.value = id;
  opt.textContent = `${m.icone} ${m.nom}`;
  selectModele.appendChild(opt);
}

selectModele.addEventListener("change", () => {
  // On garde tous les textes, photos et réglages : seul le modèle change
  modeleActuel = selectModele.value;
  const p = new URLSearchParams(location.search);
  p.set("modele", modeleActuel); p.delete("variante");
  history.replaceState(null, "", "?" + p.toString());
  choisirVariante(null, false);          // le 1er style du nouveau modèle
  document.getElementById("couleur").value = donnees.couleur;
  elementChoisi = null;
  afficherPanneauMain();
  rafraichirOptions();
  miseAJour(true);
});

// Les 5 styles du modèle actuel, sous forme de petites cartes
function afficherVariantes() {
  const zone = document.getElementById("variantes");
  zone.innerHTML = "";
  MODELES[modeleActuel].variantes.forEach(v => {
    const e = ECRITURES[v.ecriture] || ECRITURES.moderne;
    const b = document.createElement("button");
    b.type = "button";
    b.className = "variante" + (v.id === donnees.variante ? " actif" : "");
    b.title = v.nom;
    b.innerHTML = `<div class="ech" style="background:${v.fond};color:${v.encre}"><i style="background:${v.couleur}"></i><b style="font-family:${e.titre}">Aa</b></div><span>${v.nom}</span>`;
    b.addEventListener("click", () => choisirVariante(v.id));
    zone.appendChild(b);
  });
}

// ---------- Le métier : un champ où l'on tape, avec une liste qui se filtre ----------

const champMetier = document.getElementById("metier");
const listeMetiers = document.getElementById("liste-metiers");
let metiersAffiches = [];   // les métiers visibles dans la liste, dans l'ordre
let surligne = -1;          // celui qui est surligné (flèches du clavier)

// Enlève les accents et les majuscules : "Électricien" -> "electricien"
const simplifier = t => String(t || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
// Les mots d'un métier (son nom + ses mots-clés) : "Barbier / Coiffeur" -> ["barbier", "coiffeur", ...]
const motsDe = m => simplifier(m.nom + " " + (m.mots || "")).split(/[^a-z0-9]+/).filter(Boolean);

// Les métiers qui correspondent à ce qui est tapé (début d'un mot)
function chercherMetiers(texte) {
  // Le champ montre encore le métier actuel (on vient de cliquer) : on montre toute la liste
  if (METIERS[donnees.metier] && texte === METIERS[donnees.metier].nom) return null;
  const q = simplifier(texte).trim();
  const tous = Object.entries(METIERS).filter(([id]) => id !== "autre");
  if (!q) return null;   // rien de tapé : on montre tout, rangé par catégorie
  let trouves;
  if (q.length === 1) {
    // Une seule lettre : les métiers dont le nom (ou l'un des noms, ex. "Barbier / Coiffeur") commence par cette lettre
    trouves = tous.filter(([, m]) => simplifier(m.nom).split("/").some(n => n.trim().startsWith(q)));
  } else {
    // 2-3 lettres : un mot du NOM qui commence par ce qui est tapé
    // 4 lettres et plus : on cherche aussi dans les mots-clés (ex. "kine", "vtc", "fitness")
    const morceaux = q.split(/[^a-z0-9]+/).filter(Boolean);
    const motsDuNom = m => simplifier(m.nom).split(/[^a-z0-9]+/).filter(Boolean);
    trouves = tous.filter(([, m]) => {
      const mots = q.length >= 4 ? motsDe(m) : motsDuNom(m);
      return morceaux.every(p => mots.some(w => w.startsWith(p)));
    });
  }
  // Ceux dont le NOM commence par le texte passent en premier, puis par ordre alphabétique
  trouves.sort(([, a], [, b]) => {
    const debut = m => simplifier(m.nom).split("/").some(n => n.trim().startsWith(q)) ? 0 : 1;
    const pa = debut(a), pb = debut(b);
    return pa - pb || a.nom.localeCompare(b.nom, "fr");
  });
  return trouves;
}

function ligneMetier(id, m) {
  return `<li role="option" data-id="${id}" class="option-metier${id === donnees.metier ? " actuel" : ""}">
    <span class="ico">${m.icone}</span><span class="nom">${echapper(m.nom)}</span>${id === donnees.metier ? '<span class="coche">✓</span>' : ""}</li>`;
}

function afficherListeMetiers() {
  const trouves = chercherMetiers(champMetier.value);
  let html = ligneMetier("autre", METIERS.autre);   // "Autre" toujours en premier
  metiersAffiches = ["autre"];
  if (trouves === null) {
    for (const cat of CATEGORIES) {
      const dansCat = Object.entries(METIERS).filter(([, m]) => m.categorie === cat)
        .sort(([, a], [, b]) => a.nom.localeCompare(b.nom, "fr"));
      if (!dansCat.length) continue;
      html += `<li class="cat-metier" role="presentation">${cat}</li>`;
      dansCat.forEach(([id, m]) => { html += ligneMetier(id, m); metiersAffiches.push(id); });
    }
  } else if (trouves.length) {
    trouves.forEach(([id, m]) => { html += ligneMetier(id, m); metiersAffiches.push(id); });
  } else {
    html += `<li class="vide-metier" role="presentation">Aucun métier trouvé. Choisissez « Autre » ci-dessus : vous pourrez écrire vos propres textes.</li>`;
  }
  listeMetiers.innerHTML = html;
  surligne = trouves && trouves.length ? 1 : -1;   // le 1er résultat est surligné
  majSurlignage();
}

function majSurlignage() {
  listeMetiers.querySelectorAll(".option-metier").forEach(li =>
    li.classList.toggle("surligne", li.dataset.id === metiersAffiches[surligne]));
  const li = listeMetiers.querySelector(".surligne");
  if (li) li.scrollIntoView({ block: "nearest" });
}

function ouvrirListe() {
  afficherListeMetiers();
  listeMetiers.hidden = false;
  champMetier.setAttribute("aria-expanded", "true");
}
function fermerListe() {
  listeMetiers.hidden = true;
  champMetier.setAttribute("aria-expanded", "false");
}

// Affiche le métier actuel dans le champ
function afficherMetierActuel() {
  const m = METIERS[donnees.metier];
  champMetier.value = m ? m.nom : "";
  document.getElementById("icone-metier").textContent = m ? m.icone : "🔎";
}

// Le client a-t-il déjà changé les textes d'exemple ?
function textesModifies() {
  const ex = (METIERS[donnees.metier] || {}).defauts || {};
  return ["nom", "slogan", "description", "services", "horaires"].some(k => (donnees[k] || "") !== (ex[k] || ""));
}

function choisirMetier(id) {
  fermerListe();
  if (id === donnees.metier) { afficherMetierActuel(); return; }
  if (textesModifies() && !confirm(`Remplir le site avec les textes d'exemple « ${METIERS[id].nom} » ?\n\nVos textes actuels seront remplacés (vos photos et votre style sont gardés).`)) {
    afficherMetierActuel();
    return;
  }
  remplirAvecMetier(id);
  remplirFormulaire();
  miseAJour(true);
  champMetier.blur();
}

champMetier.addEventListener("focus", () => { champMetier.select(); ouvrirListe(); });
champMetier.addEventListener("click", () => { if (listeMetiers.hidden) ouvrirListe(); });
champMetier.addEventListener("input", () => {
  document.getElementById("icone-metier").textContent = "🔎";
  ouvrirListe();
  // Mot entier tapé : s'il correspond exactement à un seul métier, on le choisit tout seul
  const q = simplifier(champMetier.value).trim();
  if (q.length < 3) return;
  const exacts = Object.entries(METIERS).filter(([id, m]) =>
    id !== "autre" && (simplifier(m.nom) === q || motsDe(m).includes(q)));
  if (exacts.length === 1) {
    clearTimeout(champMetier._minuteur);
    // petite attente : si le client continue d'écrire, on ne choisit pas trop tôt
    champMetier._minuteur = setTimeout(() => {
      if (simplifier(champMetier.value).trim() === q) choisirMetier(exacts[0][0]);
    }, 700);
  }
});
champMetier.addEventListener("keydown", e => {
  if (listeMetiers.hidden && ["ArrowDown", "ArrowUp"].includes(e.key)) { ouvrirListe(); e.preventDefault(); return; }
  if (e.key === "ArrowDown") { surligne = Math.min(metiersAffiches.length - 1, surligne + 1); majSurlignage(); e.preventDefault(); }
  if (e.key === "ArrowUp") { surligne = Math.max(0, surligne - 1); majSurlignage(); e.preventDefault(); }
  if (e.key === "Enter") { e.preventDefault(); if (surligne >= 0) choisirMetier(metiersAffiches[surligne]); }
  if (e.key === "Escape") { fermerListe(); afficherMetierActuel(); champMetier.blur(); }
});
// Clic (ou doigt) sur un métier de la liste
listeMetiers.addEventListener("pointerdown", e => e.preventDefault());   // garde le champ actif
listeMetiers.addEventListener("click", e => {
  const li = e.target.closest(".option-metier");
  if (li) choisirMetier(li.dataset.id);
});
document.getElementById("ouvrir-metier").addEventListener("click", () => {
  if (listeMetiers.hidden) { champMetier.value = ""; champMetier.focus(); ouvrirListe(); }
  else { fermerListe(); afficherMetierActuel(); }
});
// Clic ailleurs : on ferme et on remet le nom du métier actuel
document.addEventListener("pointerdown", e => {
  if (!listeMetiers.hidden && !e.target.closest("#choix-metier")) { fermerListe(); afficherMetierActuel(); }
});

function remplirAvecMetier(idMetier) {
  const ex = METIERS[idMetier].defauts;
  ["nom", "slogan", "description", "telephone", "email", "adresse", "horaires", "services"].forEach(k => donnees[k] = ex[k] || "");
  donnees.metier = idMetier;
  donnees.titres = {};
}



// ---------- Photos ----------
// Les photos sont réduites pour que le site reste léger et rapide.

function reduirePhoto(fichier, tailleMax = 1400) {
  return new Promise((resoudre, rejeter) => {
    const lecteur = new FileReader();
    lecteur.onerror = rejeter;
    lecteur.onload = () => {
      const img = new Image();
      img.onerror = rejeter;
      img.onload = () => {
        const ratio = Math.min(1, tailleMax / Math.max(img.width, img.height));
        const canvas = document.createElement("canvas");
        canvas.width = Math.round(img.width * ratio);
        canvas.height = Math.round(img.height * ratio);
        canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
        resoudre(canvas.toDataURL("image/jpeg", 0.8));
      };
      img.src = lecteur.result;
    };
    lecteur.readAsDataURL(fichier);
  });
}

document.getElementById("photoHero").addEventListener("change", async e => {
  const f = e.target.files[0];
  if (!f) return;
  donnees.photoHero = await reduirePhoto(f, 1800);
  e.target.value = "";
  afficherVignettes();
  miseAJour();
});

document.getElementById("galerie").addEventListener("change", async e => {
  const fichiers = [...e.target.files];
  const nouvelles = await Promise.all(fichiers.map(f => reduirePhoto(f, 1000)));
  donnees.galerie = [...(donnees.galerie || []), ...nouvelles].slice(0, 6);
  e.target.value = "";
  afficherVignettes();
  afficherParties();
  miseAJour();
});

document.getElementById("retirer-hero").addEventListener("click", () => {
  donnees.photoHero = "";
  afficherVignettes();
  miseAJour();
});

document.getElementById("retirer-galerie").addEventListener("click", () => {
  donnees.galerie = [];
  afficherVignettes();
  afficherParties();
  miseAJour();
});

function afficherVignettes() {
  const vh = document.getElementById("vignette-hero");
  const vg = document.getElementById("vignettes-galerie");
  vh.innerHTML = donnees.photoHero ? `<img src="${donnees.photoHero}" alt="">` : "";
  vg.innerHTML = (donnees.galerie || []).map(src => `<img src="${src}" alt="">`).join("");
  document.getElementById("retirer-hero").hidden = !donnees.photoHero;
  document.getElementById("retirer-galerie").hidden = !(donnees.galerie || []).length;
}

// ---------- Aperçu en direct ----------

let minuteur = null;
function miseAJour(immediat = false) {
  clearTimeout(minuteur);
  const faire = () => {
    // On garde la position de défilement pour que l'aperçu ne "saute" pas
    let y = 0;
    try { y = apercu.contentWindow.scrollY; } catch (e) {}
    apercu.srcdoc = genererSite(modeleActuel, donnees, { edition: modeMain });
    apercu.onload = () => { try { apercu.contentWindow.scrollTo(0, y); } catch (e) {} };
    sauvegarder();
  };
  immediat ? faire() : (minuteur = setTimeout(faire, 250));
}

document.querySelectorAll(".bascule button").forEach(b => {
  b.addEventListener("click", () => {
    document.querySelectorAll(".bascule button").forEach(x => x.classList.remove("actif"));
    b.classList.add("actif");
    document.getElementById("cadre").classList.toggle("mobile", b.dataset.vue === "mobile");
  });
});

document.getElementById("plein-ecran").addEventListener("click", () => {
  const blob = new Blob([genererSite(modeleActuel, donnees)], { type: "text/html" });
  window.open(URL.createObjectURL(blob), "_blank");
});

document.getElementById("reinitialiser").addEventListener("click", () => {
  if (!confirm("Remettre tous les textes d'exemple du métier « " + METIERS[donnees.metier].nom + " » ?")) return;
  remplirAvecMetier(donnees.metier);
  remplirFormulaire();
  miseAJour(true);
});

// ---------- Le "projet" = tout ce que le client a rempli ----------
// C'est un petit fichier .json qui contient le modèle, les textes et les photos.

function creerProjet(infosClient = {}) {
  return {
    format: "vitrine-express",
    version: 2,
    date: new Date().toISOString(),
    modele: modeleActuel,
    client: infosClient,
    donnees
  };
}

function nomFichierProjet() {
  const slug = String(donnees.nom || "site").toLowerCase()
    .normalize("NFD").replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "site";
  return "projet-" + slug + ".json";
}

function telechargerFichier(contenu, nom, type) {
  const blob = new Blob([contenu], { type });
  const lien = document.createElement("a");
  lien.href = URL.createObjectURL(blob);
  lien.download = nom;
  document.body.appendChild(lien);
  lien.click();
  lien.remove();
  setTimeout(() => URL.revokeObjectURL(lien.href), 1000);
}

// ---------- "Je veux ce site" (côté client) ----------

const fenetre = document.getElementById("fenetre");
const formDemande = document.getElementById("form-demande");
const vueEnvoye = document.getElementById("vue-envoye");
const vueMail = document.getElementById("vue-mail");
let infosClient = {};

document.querySelectorAll(".email-contact").forEach(el => el.textContent = CONFIG.emailContact);

function afficherVue(vue) {
  [formDemande, vueEnvoye, vueMail].forEach(v => v.hidden = v !== vue);
}

document.getElementById("je-le-veux").addEventListener("click", () => {
  // On pré-remplit avec ce que le client a déjà tapé
  document.getElementById("d-tel").value ||= donnees.telephone || "";
  document.getElementById("d-email").value ||= donnees.email || "";
  afficherVue(formDemande);
  fenetre.classList.add("ouverte");
});

document.querySelectorAll("[data-fermer]").forEach(b =>
  b.addEventListener("click", () => fenetre.classList.remove("ouverte")));
fenetre.addEventListener("click", e => { if (e.target === fenetre) fenetre.classList.remove("ouverte"); });

formDemande.addEventListener("submit", async e => {
  e.preventDefault();
  infosClient = {
    nom: document.getElementById("d-nom").value.trim(),
    telephone: document.getElementById("d-tel").value.trim(),
    email: document.getElementById("d-email").value.trim(),
    message: document.getElementById("d-message").value.trim()
  };
  const bouton = document.getElementById("bouton-envoyer");
  bouton.disabled = true;
  bouton.textContent = "Envoi en cours…";

  const envoye = await envoyerAvecNetlify();

  bouton.disabled = false;
  bouton.textContent = "Envoyer ma demande";
  if (envoye) {
    afficherVue(vueEnvoye);
  } else {
    preparerMail();
    afficherVue(vueMail);
  }
});

// Envoi automatique : marche seulement quand le site est en ligne sur Netlify
async function envoyerAvecNetlify() {
  if (!location.protocol.startsWith("http")) return false; // fichier ouvert sur l'ordi
  try {
    const projet = JSON.stringify(creerProjet(infosClient));
    if (projet.length > 7.5 * 1024 * 1024) return false; // trop lourd pour Netlify (photos)
    const fd = new FormData();
    fd.append("form-name", "demande-site");
    fd.append("nom-client", infosClient.nom);
    fd.append("telephone", infosClient.telephone);
    fd.append("email", infosClient.email);
    fd.append("commerce", donnees.nom || "");
    fd.append("modele", MODELES[modeleActuel].nom + " — style " + varianteDe(modeleActuel, donnees).nom);
    fd.append("message", infosClient.message);
    fd.append("projet", new File([projet], nomFichierProjet(), { type: "application/json" }));
    const rep = await fetch("/", { method: "POST", body: fd });
    return rep.ok;
  } catch (err) {
    return false;
  }
}

// Solution de secours : le client télécharge son projet et l'envoie par e-mail
function preparerMail() {
  const sujet = `Demande de site : ${donnees.nom}`;
  const corps =
`Bonjour,

Je souhaite obtenir mon site internet. Mon projet est en pièce jointe (${nomFichierProjet()}).

Nom : ${infosClient.nom}
Téléphone : ${infosClient.telephone}
E-mail : ${infosClient.email || "-"}
Commerce : ${donnees.nom}
Modèle : ${MODELES[modeleActuel].nom} (style ${varianteDe(modeleActuel, donnees).nom})

${infosClient.message}`;
  document.getElementById("lien-mail").href =
    `mailto:${CONFIG.emailContact}?subject=${encodeURIComponent(sujet)}&body=${encodeURIComponent(corps)}`;
}

document.getElementById("telecharger-projet").addEventListener("click", () => {
  telechargerFichier(JSON.stringify(creerProjet(infosClient)), nomFichierProjet(), "application/json");
});

// ---------- Mode admin (pour toi) ----------
// Ouvre editeur.html?admin=TON_CODE (le code est dans config.js)

const modeAdmin = params.get("admin") && params.get("admin") === CONFIG.codeAdmin;
if (modeAdmin) {
  document.getElementById("barre-admin").hidden = false;
  document.title = "🔧 Admin — " + document.title;
}

// Ouvre le projet envoyé par un client : tout se remplit automatiquement
document.getElementById("importer").addEventListener("change", async e => {
  const fichier = e.target.files[0];
  e.target.value = "";
  if (!fichier) return;
  try {
    const projet = JSON.parse(await fichier.text());
    if (projet.format !== "vitrine-express") throw new Error("format");
    // Anciens projets : le "modèle" était un métier (barbier, garage…)
    const ancien = !MODELES[projet.modele] && METIERS[projet.modele];
    if (!MODELES[projet.modele] && !ancien) throw new Error("format");
    modeleActuel = ancien ? "classique" : projet.modele;
    history.replaceState(null, "", `?modele=${modeleActuel}&admin=${encodeURIComponent(params.get("admin"))}`);
    donnees = { ...copieOptions(), photoHero: "", galerie: [], ...projet.donnees };
    if (ancien) donnees.metier = projet.modele;
    if (!METIERS[donnees.metier]) donnees.metier = MODELES[modeleActuel].exemple;
    if (!donnees.variante) donnees.variante = varianteDe(modeleActuel, donnees).id;
    if (donnees.entete === "degrade" && ancien) donnees.entete = "auto";
    remplirFormulaire();
    miseAJour(true);
    const c = projet.client || {};
    alert(`Projet ouvert ✅\n\nClient : ${c.nom || "?"}\nTéléphone : ${c.telephone || "?"}\nE-mail : ${c.email || "-"}\n${c.message ? "\nMessage : " + c.message : ""}`);
  } catch (err) {
    alert("Ce fichier n'est pas un projet Vitrine Express valide.");
  }
});

// Sauvegarde le projet en cours (pour le reprendre plus tard)
document.getElementById("exporter-projet").addEventListener("click", () => {
  telechargerFichier(JSON.stringify(creerProjet()), nomFichierProjet(), "application/json");
});

// Télécharge le site terminé en un seul fichier index.html
// (c'est ce fichier que tu mets en ligne sur Netlify pour le client)
document.getElementById("telecharger-site").addEventListener("click", () => {
  telechargerFichier(genererSite(modeleActuel, donnees), "index.html", "text/html");
});

// ---------- Démarrage ----------
charger();
// On retire le style de l'adresse : sinon, en rechargeant la page, il effacerait les réglages du client
{ const p = new URLSearchParams(location.search); p.set("modele", modeleActuel); p.delete("variante"); history.replaceState(null, "", "?" + p.toString()); }
document.getElementById("couleur").value = donnees.couleur;
remplirFormulaire();
miseAJour(true);
