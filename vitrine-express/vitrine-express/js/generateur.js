// ============================================================
//  LE GÉNÉRATEUR : fabrique le site final (un seul fichier HTML)
//  à partir du modèle choisi (modeles.js), de son style, du métier
//  (metiers.js) et de la personnalisation du client.
//  Tu n'as normalement pas besoin de toucher à ce fichier.
// ============================================================

// Textes utilisés si le métier n'en précise pas d'autres
const LIBELLES_PAR_DEFAUT = {
  menuServices: "Tarifs",
  titreServices: "Prestations & tarifs",
  voirServices: "Voir les tarifs",
  boutonAppel: "Appeler"
};

// ---------- Les réglages que le client peut changer ----------

const OPTIONS_PAR_DEFAUT = {
  ordre: ["apropos", "services", "galerie", "infos", "plan"], // ordre des rubriques
  cache: [],                // rubriques masquées
  titres: {},               // noms des rubriques choisis par le client
  alignement: "gauche",     // gauche | centre
  fondStyle: "modele",      // "modele" = celui du style choisi, sinon voir FONDS
  ecriture: "modele",       // "modele" = celle du style choisi, sinon voir ECRITURES
  entete: "auto",           // auto (celui du modèle) | degrade | uni | pale
  hauteur: "grand",         // grand | moyen | compact
  tailleTexte: "normal",    // normal | grand
  boutons: "arrondis",      // arrondis | doux | carres
  ajustements: {}           // éléments déplacés / agrandis à la main : { id: { x, y, z } }
};

// Couleurs de fond que le client peut imposer (onglet Style)
const FONDS = {
  blanc:  { nom: "Blanc",       fond: "#ffffff", surface: "#f3f4f6", encre: "#111827", doux: "#5b6270" },
  creme:  { nom: "Crème",       fond: "#fbf7f0", surface: "#ffffff", encre: "#2b2118", doux: "#7a6a5a" },
  gris:   { nom: "Gris clair",  fond: "#eef0f3", surface: "#ffffff", encre: "#15191f", doux: "#5b6270" },
  teinte: { nom: "Teinté",      fond: "TEINTE",  surface: "#ffffff", encre: "#1a1a1a", doux: "#5a5a5a" },
  sombre: { nom: "Sombre",      fond: "#16181d", surface: "#20232a", encre: "#f3f4f6", doux: "#a4a9b3" },
  noir:   { nom: "Noir",        fond: "#0a0a0a", surface: "#161616", encre: "#f5f5f5", doux: "#a3a3a3" }
};

// Styles d'écriture (polices Google Fonts)
const ECRITURES = {
  moderne:     { nom: "Moderne",   polices: "family=Inter:wght@300;400;600;800", titre: "'Inter', sans-serif", texte: "'Inter', sans-serif", majuscules: false },
  elegant:     { nom: "Élégant",   polices: "family=Playfair+Display:wght@500;700&family=Lato:wght@400;700", titre: "'Playfair Display', serif", texte: "'Lato', sans-serif", majuscules: false },
  luxe:        { nom: "Luxe",      polices: "family=Cormorant+Garamond:wght@500;700&family=Nunito+Sans:wght@400;600", titre: "'Cormorant Garamond', serif", texte: "'Nunito Sans', sans-serif", majuscules: false },
  classique:   { nom: "Classique", polices: "family=Merriweather:wght@700&family=Source+Sans+3:wght@400;600", titre: "'Merriweather', serif", texte: "'Source Sans 3', sans-serif", majuscules: false },
  serif:       { nom: "Chic",      polices: "family=DM+Serif+Display&family=DM+Sans:wght@400;600", titre: "'DM Serif Display', serif", texte: "'DM Sans', sans-serif", majuscules: false },
  editorial:   { nom: "Éditorial", polices: "family=Fraunces:wght@600;800&family=Inter:wght@400;600", titre: "'Fraunces', serif", texte: "'Inter', sans-serif", majuscules: false },
  grotesk:     { nom: "Tech",      polices: "family=Space+Grotesk:wght@500;700&family=Inter:wght@400;600", titre: "'Space Grotesk', sans-serif", texte: "'Inter', sans-serif", majuscules: false },
  geometrique: { nom: "Design",    polices: "family=Syne:wght@600;800&family=Inter:wght@400;600", titre: "'Syne', sans-serif", texte: "'Inter', sans-serif", majuscules: false },
  solide:      { nom: "Solide",    polices: "family=Archivo:wght@600;800&family=Inter:wght@400;600", titre: "'Archivo', sans-serif", texte: "'Inter', sans-serif", majuscules: false },
  douce:       { nom: "Douce",     polices: "family=Manrope:wght@400;600;800", titre: "'Manrope', sans-serif", texte: "'Manrope', sans-serif", majuscules: false },
  arrondi:     { nom: "Arrondi",   polices: "family=Nunito:wght@400;700;800", titre: "'Nunito', sans-serif", texte: "'Nunito', sans-serif", majuscules: false },
  condense:    { nom: "Sport",     polices: "family=Oswald:wght@500;700&family=Inter:wght@400;600", titre: "'Oswald', sans-serif", texte: "'Inter', sans-serif", majuscules: true },
  impact:      { nom: "Impact",    polices: "family=Bebas+Neue&family=Inter:wght@400;600", titre: "'Bebas Neue', sans-serif", texte: "'Inter', sans-serif", majuscules: true },
  manuscrit:   { nom: "Manuscrit", polices: "family=Pacifico&family=Nunito:wght@400;700", titre: "'Pacifico', cursive", texte: "'Nunito', sans-serif", majuscules: false }
};

// Ambiances prêtes (onglet Style) : un clic change couleur + fond + écriture + en-tête
const AMBIANCES = [
  { nom: "Noir & or",       couleur: "#c9a227", fondStyle: "noir",   ecriture: "luxe",      entete: "degrade" },
  { nom: "Frais & moderne", couleur: "#2563eb", fondStyle: "blanc",  ecriture: "moderne",   entete: "uni" },
  { nom: "Nature",          couleur: "#3f7d3a", fondStyle: "creme",  ecriture: "classique", entete: "degrade" },
  { nom: "Pastel",          couleur: "#d9678a", fondStyle: "teinte", ecriture: "arrondi",   entete: "pale" },
  { nom: "Énergie",         couleur: "#ef4444", fondStyle: "sombre", ecriture: "impact",    entete: "uni" },
  { nom: "Chaleureux",      couleur: "#c2410c", fondStyle: "creme",  ecriture: "elegant",   entete: "degrade" }
];

// Comment chaque modèle est construit (voir aussi cssModele plus bas)
//  entetePage : standard | centre | minimal | pro
//  hero       : bandeau | centre | duo | editorial | minimal | carte | mosaique | pro
//  bandeau    : le style du grand bandeau par défaut (degrade | uni | pale)
const MISES_EN_PAGE = {
  classique: { entetePage: "standard", hero: "bandeau",   bandeau: "degrade" },
  elegance:  { entetePage: "centre",   hero: "centre",    bandeau: "pale" },
  duo:       { entetePage: "standard", hero: "duo",       bandeau: "uni" },
  magazine:  { entetePage: "minimal",  hero: "editorial", bandeau: "uni" },
  cartes:    { entetePage: "standard", hero: "carte",     bandeau: "degrade" },
  minimal:   { entetePage: "minimal",  hero: "minimal",   bandeau: "pale" },
  impact:    { entetePage: "standard", hero: "centre",    bandeau: "uni" },
  galerie:   { entetePage: "standard", hero: "mosaique",  bandeau: "degrade" },
  menu:      { entetePage: "centre",   hero: "centre",    bandeau: "degrade" },
  pro:       { entetePage: "pro",      hero: "pro",       bandeau: "degrade" }
};

// ---------- Petits outils partagés avec l'éditeur ----------

// Le modèle demandé (ou Classique s'il n'existe pas)
function modeleDe(idModele) { return MODELES[idModele] ? idModele : "classique"; }

// Le style (sous-modèle) choisi, ou le premier du modèle
function varianteDe(idModele, d) {
  const m = MODELES[modeleDe(idModele)];
  return m.variantes.find(v => v.id === (d && d.variante)) || m.variantes[0];
}

// Les mots du métier ("Carte" au lieu de "Tarifs", "Réserver"…)
function libellesDe(d) {
  const metier = (typeof METIERS !== "undefined" && METIERS[d.metier]) || {};
  return { ...LIBELLES_PAR_DEFAUT, ...(metier.libelles || {}) };
}

// Couleurs + écriture finales : celles du style, puis les choix du client par-dessus
function styleDe(idModele, d) {
  const v = varianteDe(idModele, d);
  const couleur = d.couleur || v.couleur;
  const t = { ...(ECRITURES[v.ecriture] || ECRITURES.moderne), fond: v.fond, surface: v.surface, encre: v.encre, doux: v.doux };
  if (FONDS[d.fondStyle]) Object.assign(t, FONDS[d.fondStyle]);
  if (t.fond === "TEINTE") t.fond = `color-mix(in srgb, ${couleur} 8%, #ffffff)`;
  if (ECRITURES[d.ecriture]) Object.assign(t, ECRITURES[d.ecriture]);
  return t;
}

// Des données d'exemple pour montrer un modèle (page d'accueil)
function donneesExemple(idModele, idVariante) {
  const m = MODELES[modeleDe(idModele)];
  const v = m.variantes.find(x => x.id === idVariante) || m.variantes[0];
  const metier = METIERS[m.exemple] || Object.values(METIERS)[0];
  return { ...metier.defauts, metier: m.exemple, variante: v.id, couleur: v.couleur };
}

// Les rubriques du site, avec leur titre de base
function titresDeBase(L) {
  return { apropos: "À propos", services: L.titreServices, galerie: "En images", infos: "Horaires & contact", plan: "Plan d'accès" };
}

// Les rubriques affichées, dans l'ordre choisi (sans les cachées ni les vides)
function rubriquesVisibles(d) {
  const toutes = OPTIONS_PAR_DEFAUT.ordre;
  const o = (d.ordre || []).filter(id => toutes.includes(id));
  const ordre = [...o, ...toutes.filter(id => !o.includes(id))];
  const aContenu = {
    apropos: !!String(d.description || "").trim(),
    services: lireServices(d.services).length > 0,
    galerie: (d.galerie || []).filter(Boolean).length > 0,
    infos: true,
    plan: !!String(d.adresse || "").trim()
  };
  return ordre.filter(id => !(d.cache || []).includes(id) && aContenu[id]);
}

// Empêche le texte tapé par le client de "casser" le HTML
function echapper(texte) {
  return String(texte || "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// "Coupe homme | 20 €" -> { nom: "Coupe homme", prix: "20 €" }
function lireServices(texte) {
  return String(texte || "").split("\n").map(l => l.trim()).filter(Boolean).map(l => {
    const [nom, prix] = l.split("|").map(s => (s || "").trim());
    return { nom, prix: prix || "" };
  });
}

// "Mardi - Vendredi : 9h - 19h" -> { jour, heures }
function lireHoraires(texte) {
  return String(texte || "").split("\n").map(l => l.trim()).filter(Boolean).map(l => {
    const i = l.indexOf(":");
    if (i === -1) return { jour: l, heures: "" };
    return { jour: l.slice(0, i).trim(), heures: l.slice(i + 1).trim() };
  });
}

// Vrai si la couleur est claire (le texte blanc serait illisible dessus)
function estClaire(hex) {
  const h = String(hex || "").replace("#", "");
  if (h.length !== 6) return false;
  const [r, g, b] = [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16) / 255)
    .map(c => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.4;
}

// ============================================================
//  FABRICATION DU SITE
// ============================================================

// options.edition = true : ajoute les outils pour déplacer / agrandir (seulement dans l'éditeur)
function genererSite(idModeleDemande, donneesClient, options = {}) {
  const idModele = modeleDe(idModeleDemande);
  const mp = MISES_EN_PAGE[idModele];
  const v = varianteDe(idModele, donneesClient || {});
  const d = { ...OPTIONS_PAR_DEFAUT, ...donneesClient };
  if (!d.couleur) d.couleur = v.couleur;
  const L = libellesDe(d);
  const t = styleDe(idModele, d);

  const services = lireServices(d.services);
  const horaires = lireHoraires(d.horaires);
  const galerie = (d.galerie || []).filter(Boolean);
  const telLien = String(d.telephone || "").replace(/[^\d+]/g, "");
  const carte = encodeURIComponent(d.adresse || "");
  const centre = d.alignement === "centre";

  // Noms des rubriques (ceux du client s'il les a changés)
  const base = titresDeBase(L);
  const perso = id => d.titres && d.titres[id] && d.titres[id].trim();
  const titre = id => perso(id) || base[id];
  const libelleMenu = {
    apropos: titre("apropos"),
    services: perso("services") || L.menuServices,
    galerie: perso("galerie") || "Photos",
    infos: titre("infos"),
    plan: titre("plan")
  };
  const visibles = rubriquesVisibles(d);

  // ---------- Couleurs ----------
  const accentClair = estClaire(d.couleur);
  const surAccent = accentClair ? "#111111" : "#ffffff";
  const fondPage = /^#/.test(t.fond) ? t.fond : "#ffffff";
  const fondSombre = !estClaire(fondPage);

  // Le grand bandeau du haut : photo, dégradé, couleur unie ou couleur pâle
  const modeBandeau = d.entete && d.entete !== "auto" ? d.entete : mp.bandeau;
  let fondBandeau, texteBandeau = "#ffffff";
  if (d.photoHero) {
    fondBandeau = `linear-gradient(rgba(0,0,0,.5), rgba(0,0,0,.5)), url('${d.photoHero}') center/cover`;
  } else if (modeBandeau === "uni") {
    fondBandeau = d.couleur;
    texteBandeau = surAccent;
  } else if (modeBandeau === "pale") {
    fondBandeau = `color-mix(in srgb, ${d.couleur} ${fondSombre ? 22 : 14}%, ${fondPage})`;
    texteBandeau = t.encre;
  } else {
    fondBandeau = accentClair
      ? `linear-gradient(135deg, color-mix(in srgb, ${d.couleur} 55%, #000), color-mix(in srgb, ${d.couleur} 25%, #000))`
      : `linear-gradient(135deg, ${d.couleur}, color-mix(in srgb, ${d.couleur} 40%, #000))`;
  }
  // Certains modèles gardent le fond de la page en haut (le visuel est à côté ou dessous)
  const bandeauSurPage = ["duo", "editorial", "minimal", "mosaique"].includes(mp.hero);
  const heroFond = bandeauSurPage ? "transparent" : fondBandeau;
  const heroTexte = bandeauSurPage ? t.encre : texteBandeau;

  const paddingHero = { grand: 112, moyen: 80, compact: 52 }[d.hauteur] || 112;
  const rayon = { arrondis: "999px", doux: "10px", carres: "0" }[d.boutons] || "999px";
  const rayonImages = { arrondis: "16px", doux: "10px", carres: "0" }[d.boutons] || "16px";

  // ---------- Les "blocs" déplaçables ----------
  const ajust = d.ajustements || {};
  const nombre = (x, defaut) => (typeof x === "number" && isFinite(x) ? Math.round(x * 100) / 100 : defaut);
  function bloc(id, contenu, classes = "") {
    const a = ajust[id] || {};
    const x = nombre(a.x, 0), y = nombre(a.y, 0), z = Math.min(3, Math.max(0.4, nombre(a.z, 1)));
    const style = (x || y ? `left:${x}%;top:${y}px;` : "");
    const styleZ = z !== 1 ? ` style="zoom:${z}"` : "";
    return `<div class="bloc" data-edit="${id}" data-x="${x}" data-y="${y}" data-z="${z}"${style ? ` style="${style}"` : ""}><div class="z ${classes}"${styleZ}>${contenu}</div></div>`;
  }
  const numerotees = visibles.filter(id => id !== "infos");   // "Horaires & contact" n'a pas de grand titre
  const numero = id => String(numerotees.indexOf(id) + 1).padStart(2, "0");
  const titrePartie = id => bloc(id + "-titre",
    `<span class="numero">${numero(id)}</span><div class="trait"></div><h2>${echapper(titre(id))}</h2>`, "titre-partie");

  // ---------- En-tête du site (logo + menu) ----------
  const liensMenu = visibles.map(id => `<a href="#${id}">${echapper(libelleMenu[id])}</a>`).join("");
  const boutonAppel = telLien ? `<a class="bouton" href="tel:${telLien}">${L.boutonAppel}</a>` : "";
  const premierHoraire = horaires[0] ? `${horaires[0].jour} ${horaires[0].heures}` : "";
  let entetePage;
  if (mp.entetePage === "centre") {
    entetePage = `
<header class="entete-centre">
  <div class="conteneur">
    <a class="logo" href="#">${echapper(d.nom)}</a>
    <nav>${liensMenu}</nav>
    ${telLien ? `<a class="lien-appel" href="tel:${telLien}">📞 ${echapper(d.telephone)}</a>` : ""}
  </div>
</header>`;
  } else if (mp.entetePage === "minimal") {
    entetePage = `
<header class="entete-minimal">
  <div class="conteneur">
    <a class="logo" href="#">${echapper(d.nom)}</a>
    <nav>${liensMenu}${telLien ? `<a class="lien-appel" href="tel:${telLien}">${L.boutonAppel} →</a>` : ""}</nav>
  </div>
</header>`;
  } else {
    entetePage = `
${mp.entetePage === "pro" ? `<div class="barre-infos"><div class="conteneur">
  ${d.telephone ? `<span>📞 ${echapper(d.telephone)}</span>` : ""}
  ${d.adresse ? `<span>📍 ${echapper(d.adresse)}</span>` : ""}
  ${premierHoraire ? `<span class="masque-tel">🕒 ${echapper(premierHoraire)}</span>` : ""}
</div></div>` : ""}
<header class="entete-standard">
  <div class="conteneur">
    <a class="logo" href="#">${echapper(d.nom)}</a>
    <nav>${liensMenu}</nav>
    ${boutonAppel}
  </div>
</header>`;
  }

  // ---------- Le grand bandeau du haut ----------
  const blocsHero = `
      ${bloc("hero-titre", `<h1>${echapper(d.nom)}</h1>`)}
      ${bloc("hero-texte", `<p>${echapper(d.slogan)}</p>`)}
      ${bloc("hero-boutons", `
        ${telLien ? `<a class="bouton" href="tel:${telLien}">📞 ${echapper(d.telephone)}</a>` : ""}
        ${visibles.includes("services") ? `<a class="bouton contour" href="#services">${L.voirServices}</a>` : ""}`, "actions")}`;

  const initiale = echapper((String(d.nom || "?").trim()[0] || "?").toUpperCase());
  let coteHero = "";
  if (mp.hero === "duo") {
    coteHero = `<div class="hero-visuel" style="background:${fondBandeau}">${d.photoHero ? "" : `<span class="initiale">${initiale}</span>`}</div>`;
  } else if (mp.hero === "editorial" || mp.hero === "minimal") {
    coteHero = d.photoHero ? `<div class="hero-visuel" style="background:url('${d.photoHero}') center/cover"></div>` : `<div class="hero-ligne"></div>`;
  } else if (mp.hero === "pro") {
    coteHero = bloc("hero-infos", `<div class="carte-contact">
        <div class="cc-titre">Contactez-nous</div>
        ${d.telephone ? `<div class="cc-ligne"><span>📞</span><a href="tel:${telLien}">${echapper(d.telephone)}</a></div>` : ""}
        ${d.adresse ? `<div class="cc-ligne"><span>📍</span><span>${echapper(d.adresse)}</span></div>` : ""}
        ${horaires.slice(0, 2).map(h => `<div class="cc-ligne"><span>🕒</span><span>${echapper(h.jour)} : ${echapper(h.heures)}</span></div>`).join("")}
        ${telLien ? `<a class="bouton plein" href="tel:${telLien}">${L.boutonAppel} maintenant</a>` : ""}
      </div>`, "plein");
  }
  // Mosaïque (Galerie photo) : les photos du client, ou des carrés de couleur s'il n'y en a pas encore
  let mosaique = "";
  if (mp.hero === "mosaique") {
    const photos = [d.photoHero, ...galerie].filter(Boolean).slice(0, 5);
    const tuiles = Array.from({ length: 5 }, (_, i) => photos[i]
      ? `<div class="tuile" style="background:url('${photos[i]}') center/cover"></div>`
      : `<div class="tuile" style="background:color-mix(in srgb, ${d.couleur} ${[85, 55, 30, 65, 40][i]}%, ${fondSombre ? "#000" : "#fff"})"></div>`).join("");
    mosaique = `<div class="mosaique">${tuiles}</div>`;
  }

  const hero = `
<section class="hero hero-${mp.hero}">
  ${mosaique}
  <div class="conteneur hero-grille">
    <div class="hero-texte">${mp.hero === "centre" && idModele !== "impact" ? `<div class="ornement">✦</div>` : ""}${blocsHero}
    </div>
    ${coteHero}
  </div>
</section>`;

  // ---------- Les rubriques ----------
  const parties = {
    apropos: `
<section class="apropos" id="apropos">
  <div class="conteneur">
    ${titrePartie("apropos")}
    ${bloc("apropos-texte", `<p>${echapper(d.description).replace(/\n/g, "<br>")}</p>`, "contenu")}
  </div>
</section>`,

    services: `
<section class="services" id="services">
  <div class="conteneur">
    ${titrePartie("services")}
    ${bloc("services-liste", `<div class="liste-services">
      ${services.map(s => `<div class="service"><span class="nom">${echapper(s.nom)}</span><span class="points"></span><span class="prix">${echapper(s.prix)}</span></div>`).join("")}
    </div>`, "plein contenu")}
  </div>
</section>`,

    galerie: `
<section class="galerie" id="galerie">
  <div class="conteneur">
    ${titrePartie("galerie")}
    ${bloc("galerie-photos", `<div class="galerie-grille">
      ${galerie.map(src => `<img src="${src}" alt="Photo ${echapper(d.nom)}" loading="lazy">`).join("")}
    </div>`, "plein contenu")}
  </div>
</section>`,

    infos: `
<section class="infos" id="infos">
  <div class="conteneur">
    <div class="infos-grille">
      ${bloc("horaires", `<div class="trait"></div><h2>Horaires</h2>
        ${horaires.map(h => `<div class="horaire"><span>${echapper(h.jour)}</span><span>${echapper(h.heures)}</span></div>`).join("")}`, "plein")}
      ${bloc("contact", `<div class="contact"><div class="trait"></div><h2>Contact</h2>
        ${d.adresse ? `<p>📍 ${echapper(d.adresse)}</p>` : ""}
        ${d.telephone ? `<p>📞 <a href="tel:${telLien}">${echapper(d.telephone)}</a></p>` : ""}
        ${d.email ? `<p>✉️ <a href="mailto:${echapper(d.email)}">${echapper(d.email)}</a></p>` : ""}
        ${telLien ? `<a class="bouton" href="tel:${telLien}">Appeler maintenant</a>` : ""}</div>`, "plein")}
    </div>
  </div>
</section>`,

    plan: `
<section class="plan" id="plan">
  <div class="conteneur">
    ${titrePartie("plan")}
    ${bloc("carte", `<iframe class="carte" title="Plan d'accès" src="https://www.google.com/maps?q=${carte}&output=embed"></iframe>`, "plein contenu")}
  </div>
</section>`
  };

  // Une rubrique sur deux a un fond légèrement différent
  const corps = visibles.map((id, i) =>
    parties[id].replace("<section", `<section data-alterne="${i % 2 === 0 ? "oui" : "non"}"`)).join("\n");

  return `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${echapper(d.nom)}</title>
<meta name="description" content="${echapper(d.slogan)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?${t.polices}&display=swap" rel="stylesheet">
<style>
  :root {
    --fond: ${t.fond}; --surface: ${t.surface}; --encre: ${t.encre}; --doux: ${t.doux};
    --accent: ${d.couleur}; --sur-accent: ${surAccent};
    --ligne: color-mix(in srgb, var(--encre) 12%, transparent);
    --hero-fond: ${heroFond}; --hero-texte: ${heroTexte};
    --bandeau: ${fondBandeau}; --bandeau-texte: ${texteBandeau};
    --hero-pad: ${paddingHero}px; --rayon: ${rayon}; --rayon-img: ${rayonImages};
    --police-titre: ${t.titre}; --police-texte: ${t.texte};
  }
  html { font-size: ${d.tailleTexte === "grand" ? "112.5%" : "100%"}; }
${CSS_BASE}
  h1, h2, h3, .logo { ${t.majuscules ? "text-transform: uppercase; letter-spacing: .03em;" : ""} }
${cssModele(idModele)}
${centre ? CSS_CENTRE : ""}
</style>
</head>
<body class="modele-${idModele}">
${entetePage}
${hero}
${corps}

<footer>
  <div class="conteneur">© ${new Date().getFullYear()} ${echapper(d.nom)}${d.adresse ? ` · ${echapper(d.adresse)}` : ""}</div>
</footer>

<script>
  // Les liens du menu font défiler la page jusqu'à la bonne rubrique
  document.querySelectorAll('a[href^="#"]').forEach(function (lien) {
    lien.addEventListener("click", function (e) {
      e.preventDefault();
      var id = lien.getAttribute("href").slice(1);
      var cible = id ? document.getElementById(id) : null;
      if (cible) cible.scrollIntoView({ behavior: "smooth" });
      else window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });
</script>
${options.edition ? `<script>(${scriptEdition.toString()})();</script>` : ""}
</body>
</html>`;
}

// ============================================================
//  LE STYLE COMMUN À TOUS LES MODÈLES
// ============================================================
const CSS_BASE = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  html, body { overflow-x: clip; }
  body { font-family: var(--police-texte); background: var(--fond); color: var(--encre); line-height: 1.65; -webkit-font-smoothing: antialiased; }
  h1, h2, h3, .logo { font-family: var(--police-titre); line-height: 1.12; font-weight: 700; overflow-wrap: anywhere; hyphens: auto; }
  .service .nom { min-width: 0; }
  a { color: inherit; }
  img { max-width: 100%; }
  .conteneur { width: min(1120px, 100% - 40px); margin-inline: auto; }
  .bloc { position: relative; }
  .z { display: inline-block; max-width: 100%; vertical-align: top; }
  .z.plein { display: block; }

  /* En-tête */
  header { position: sticky; top: 0; z-index: 20; background: color-mix(in srgb, var(--fond) 92%, transparent); backdrop-filter: blur(10px); border-bottom: 1px solid var(--ligne); }
  header .conteneur { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 16px 0; }
  .logo { font-size: 1.3rem; text-decoration: none; white-space: nowrap; }
  nav { display: flex; gap: 26px; align-items: center; flex-wrap: wrap; justify-content: center; }
  nav a { text-decoration: none; color: var(--doux); font-size: .95rem; transition: color .2s; }
  nav a:hover { color: var(--encre); }
  .lien-appel { text-decoration: none; font-weight: 600; color: var(--encre) !important; white-space: nowrap; }
  .barre-infos { background: var(--encre); color: var(--fond); font-size: .85rem; }
  .barre-infos .conteneur { display: flex; gap: 28px; padding: 8px 0; flex-wrap: wrap; }

  /* Boutons */
  .bouton { display: inline-block; background: var(--accent); color: var(--sur-accent); padding: 13px 24px; border-radius: var(--rayon); text-decoration: none; font-weight: 600; white-space: nowrap; transition: transform .15s, box-shadow .15s; }
  .bouton:hover { transform: translateY(-2px); box-shadow: 0 8px 20px color-mix(in srgb, var(--accent) 35%, transparent); }
  .bouton.contour { background: transparent; border: 2px solid var(--hero-texte); color: var(--hero-texte); }
  .bouton.plein { display: block; text-align: center; margin-top: 18px; }

  /* Bandeau du haut */
  .hero { position: relative; background: var(--hero-fond); color: var(--hero-texte); padding: var(--hero-pad) 0; overflow: hidden; }
  .hero-grille { position: relative; display: grid; gap: 48px; align-items: center; }
  .hero h1 { font-size: clamp(2.4rem, 6vw, 4.4rem); max-width: 16ch; }
  .hero p { font-size: 1.18rem; margin: 18px 0 34px; max-width: 44ch; opacity: .9; }
  .hero .actions { display: inline-flex; gap: 12px; flex-wrap: wrap; }
  .ornement { display: none; }

  /* Rubriques */
  section[data-alterne] { padding: 96px 0; scroll-margin-top: 80px; }
  section[data-alterne="non"] { background: var(--surface); }
  .titre-partie { margin-bottom: 34px; }
  .titre-partie h2 { font-size: clamp(1.8rem, 4vw, 2.6rem); }
  .infos h2 { font-size: clamp(1.5rem, 3vw, 2rem); margin-bottom: 20px; }
  .numero { display: none; }
  .trait { width: 56px; height: 4px; background: var(--accent); border-radius: 4px; margin-bottom: 18px; }
  .apropos p { font-size: 1.14rem; max-width: 65ch; color: var(--doux); }

  .liste-services { display: grid; gap: 2px; max-width: 760px; }
  .service { display: flex; align-items: baseline; gap: 14px; padding: 17px 0; border-bottom: 1px dashed var(--ligne); }
  .service .nom { font-weight: 600; }
  .service .points { flex: 1; }
  .service .prix { color: var(--accent); font-weight: 700; white-space: nowrap; }

  .galerie-grille { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 14px; }
  .galerie-grille img { width: 100%; aspect-ratio: 4/3; object-fit: cover; border-radius: var(--rayon-img); display: block; }

  .infos-grille { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 48px; }
  .horaire { display: flex; justify-content: space-between; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--ligne); }
  .horaire span:last-child { color: var(--doux); text-align: right; }
  .contact p { margin-bottom: 10px; }
  .contact .bouton { margin-top: 12px; }
  .carte { display: block; width: 100%; height: 360px; border: 0; border-radius: var(--rayon-img); }

  footer { padding: 34px 0; text-align: center; color: var(--doux); font-size: .9rem; border-top: 1px solid var(--ligne); }

  @media (max-width: 760px) {
    header .conteneur { gap: 12px; }
    .logo { min-width: 0; overflow: hidden; text-overflow: ellipsis; font-size: 1.1rem !important; }
    header .bouton { padding: 9px 14px; font-size: .85rem; flex: none; }
    .bouton { white-space: normal; text-align: center; }
    .service .prix { white-space: normal; text-align: right; max-width: 45%; }
    nav a:not(.lien-appel) { display: none; }
    .masque-tel { display: none; }
    .hero { padding: calc(var(--hero-pad) * .65) 0; }
    section[data-alterne] { padding: 64px 0; }
    .hero-grille { grid-template-columns: 1fr !important; }
  }
`;

// Option "Textes au centre"
const CSS_CENTRE = `
  .hero-texte { text-align: center; }
  .hero h1, .hero p { margin-left: auto; margin-right: auto; }
  .hero .actions { justify-content: center; }
  .titre-partie { text-align: center; }
  .titre-partie .trait { margin-left: auto; margin-right: auto; }
  section .bloc { text-align: center; }
  .apropos p { margin-inline: auto; }
  .liste-services { margin-inline: auto; text-align: left; }
  .infos .bloc { text-align: left; }
`;

// ============================================================
//  LE STYLE PROPRE À CHAQUE MODÈLE
// ============================================================
function cssModele(id) {
  switch (id) {

    // ---------- 1. CLASSIQUE ----------
    case "classique": return `
  .hero::after { content: ""; position: absolute; right: -120px; top: -120px; width: 420px; height: 420px; border-radius: 50%; background: rgba(255,255,255,.07); }
  .hero::before { content: ""; position: absolute; right: 120px; bottom: -160px; width: 300px; height: 300px; border-radius: 50%; background: rgba(255,255,255,.05); }
`;

    // ---------- 2. ÉLÉGANCE ----------
    case "elegance": return `
  .entete-centre .conteneur { flex-direction: column; gap: 10px; padding: 22px 0 14px; position: relative; }
  .entete-centre .logo { font-size: 2rem; font-weight: 500; letter-spacing: .02em; }
  .entete-centre nav { gap: 30px; }
  .entete-centre nav a { text-transform: uppercase; letter-spacing: .16em; font-size: .75rem; }
  .entete-centre .lien-appel { position: absolute; right: 0; top: 30px; font-size: .9rem; }
  .hero-texte { text-align: center; }
  .hero-grille { border: 1px solid color-mix(in srgb, var(--hero-texte) 25%, transparent); padding: 70px 30px; outline: 1px solid color-mix(in srgb, var(--hero-texte) 12%, transparent); outline-offset: 10px; }
  .hero h1 { margin: 0 auto; font-weight: 500; font-size: clamp(2.6rem, 7vw, 5rem); }
  .hero p { margin: 22px auto 34px; font-style: italic; }
  .hero .actions { justify-content: center; }
  .ornement { display: block; color: var(--accent); font-size: 1.2rem; letter-spacing: 1em; margin-bottom: 18px; padding-left: 1em; }
  section[data-alterne="non"] { background: transparent; }
  section[data-alterne] + section[data-alterne] .conteneur { border-top: 1px solid var(--ligne); padding-top: 96px; }
  section[data-alterne] + section[data-alterne] { padding-top: 0; }
  .titre-partie { text-align: center; }
  .titre-partie .trait { display: none; }
  .titre-partie h2 { font-weight: 500; font-size: clamp(2rem, 5vw, 3rem); display: flex; align-items: center; justify-content: center; gap: 18px; }
  .titre-partie h2::before, .titre-partie h2::after { content: "◆"; color: var(--accent); font-size: .35em; }
  .apropos .bloc, .galerie .bloc, .plan .bloc, .services .bloc { text-align: center; }
  .apropos p { margin-inline: auto; font-size: 1.2rem; }
  .liste-services { margin-inline: auto; text-align: left; }
  .service { border-bottom: 0; padding: 12px 0; }
  .service .points { border-bottom: 1px dotted color-mix(in srgb, var(--encre) 35%, transparent); transform: translateY(-5px); }
  .service .nom { font-weight: 500; font-size: 1.08rem; }
  .infos .trait { width: 30px; height: 1px; }
  .infos h2 { font-weight: 500; }
  @media (max-width: 760px) { .entete-centre .lien-appel { display: none; } .hero-grille { padding: 44px 18px; } section[data-alterne] + section[data-alterne] .conteneur { padding-top: 64px; } }
`;

    // ---------- 3. DUO (écran partagé) ----------
    case "duo": return `
  .hero { padding: 0; }
  .hero > .conteneur { width: 100%; }
  .hero-grille { grid-template-columns: 1.05fr 1fr; gap: 0; min-height: calc(420px + var(--hero-pad) * 2); }
  .hero-texte { padding: var(--hero-pad) 56px var(--hero-pad) max(20px, calc((100vw - 1120px) / 2)); }
  .hero h1 { font-size: clamp(2.6rem, 6vw, 4.8rem); }
  .hero-visuel { align-self: stretch; min-height: 320px; position: relative; display: grid; place-items: center; overflow: hidden; }
  .initiale { font-family: var(--police-titre); font-size: clamp(10rem, 28vw, 22rem); line-height: 1; color: var(--bandeau-texte); opacity: .9; font-weight: 700; }
  .hero-visuel::after { content: ""; position: absolute; inset: 24px; border: 2px solid color-mix(in srgb, var(--bandeau-texte) 40%, transparent); }
  section[data-alterne] .conteneur { display: grid; grid-template-columns: 1fr 2fr; gap: 56px; align-items: start; }
  section[data-alterne] .conteneur > .bloc[data-edit$="-titre"] { position: sticky; top: 100px; }
  section[data-alterne] .conteneur > .bloc:not([data-edit$="-titre"]) { grid-column: 2; }
  .infos .conteneur { grid-template-columns: 1fr !important; }
  .titre-partie h2 { font-size: clamp(1.8rem, 3.4vw, 2.6rem); }
  .trait { width: 40px; height: 6px; border-radius: 0; }
  @media (max-width: 760px) {
    .hero-texte { padding: 56px 20px; }
    .hero-visuel { min-height: 240px; }
    section[data-alterne] .conteneur { grid-template-columns: 1fr; gap: 0; }
    section[data-alterne] .conteneur > .bloc { grid-column: 1 !important; position: relative !important; top: 0 !important; }
  }
`;

    // ---------- 4. MAGAZINE ----------
    case "magazine": return `
  .entete-minimal { background: var(--fond); border-bottom: 2px solid var(--encre); }
  .entete-minimal .logo { font-size: 1.5rem; font-weight: 800; }
  .entete-minimal nav a { text-transform: uppercase; letter-spacing: .08em; font-size: .78rem; color: var(--encre); }
  .hero { padding: calc(var(--hero-pad) * .7) 0 calc(var(--hero-pad) * .5); }
  .hero-grille { gap: 36px; }
  .hero h1 { font-size: clamp(3.2rem, 11vw, 8.5rem); max-width: none; line-height: .95; font-weight: 800; letter-spacing: -.02em; }
  .hero p { font-size: 1.35rem; max-width: 38ch; border-left: 4px solid var(--accent); padding-left: 18px; }
  .hero .bouton.contour { border-color: var(--encre); color: var(--encre); }
  .hero-ligne { height: 10px; background: var(--accent); }
  .hero-visuel { height: clamp(260px, 42vw, 520px); }
  section[data-alterne="non"] { background: transparent; }
  section[data-alterne] { padding: 72px 0; }
  section[data-alterne] .conteneur { border-top: 2px solid var(--encre); padding-top: 28px; }
  .titre-partie { display: grid; grid-template-columns: auto 1fr; align-items: baseline; gap: 22px; }
  .titre-partie .z { display: grid; }
  .numero { display: block; font-family: var(--police-titre); font-size: clamp(2.6rem, 6vw, 4.5rem); color: var(--accent); line-height: 1; font-weight: 800; }
  .titre-partie .trait { display: none; }
  .titre-partie h2 { font-size: clamp(2.2rem, 5.5vw, 4rem); font-weight: 800; letter-spacing: -.01em; }
  .apropos p { font-size: 1.3rem; color: var(--encre); columns: 2 280px; column-gap: 48px; max-width: none; }
  .service { padding: 20px 0; border-bottom: 1px solid var(--ligne); }
  .service .nom { font-family: var(--police-titre); font-size: 1.25rem; }
  .service .prix { font-size: 1.15rem; }
  .galerie-grille { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
  .galerie-grille img { aspect-ratio: 3/4; }
  .infos .trait { display: none; }
`;

    // ---------- 5. CARTES ----------
    case "cartes": return `
  header { background: var(--fond); border: 0; }
  .hero { background: transparent; padding: 12px 0 0; color: var(--bandeau-texte); }
  .hero-grille { background: var(--bandeau); border-radius: 32px; padding: var(--hero-pad) clamp(28px, 6vw, 72px); box-shadow: 0 20px 50px rgba(0,0,0,.12); }
  .hero .bouton.contour { border-color: var(--bandeau-texte); color: var(--bandeau-texte); }
  section[data-alterne], section[data-alterne="non"] { background: transparent; padding: 14px 0; }
  section[data-alterne] > .conteneur { background: var(--surface); border-radius: 28px; padding: clamp(32px, 5vw, 60px); box-shadow: 0 8px 30px rgba(0,0,0,.06); }
  section[data-alterne]:last-of-type { padding-bottom: 60px; }
  .titre-partie .trait { width: auto; height: auto; background: none; margin-bottom: 10px; }
  .titre-partie .trait::before { content: "●"; color: var(--accent); font-size: .9rem; }
  .liste-services { grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; max-width: none; }
  .service { flex-direction: column; gap: 6px; background: var(--fond); border: 0; border-radius: 18px; padding: 20px 22px; }
  .service .points { display: none; }
  .service .prix { font-size: 1.25rem; }
  .galerie-grille img { border-radius: 20px; }
  .infos .trait { width: 36px; }
  footer { border: 0; }
  @media (max-width: 760px) { section[data-alterne] { padding: 10px 0; } }
`;

    // ---------- 6. MINIMAL ----------
    case "minimal": return `
  .entete-minimal { background: var(--fond); border-bottom: 0; }
  .entete-minimal .conteneur { padding: 26px 0; }
  .entete-minimal .logo { font-size: 1.05rem; font-weight: 600; letter-spacing: .02em; }
  .entete-minimal nav a { font-size: .88rem; }
  .hero { padding: calc(var(--hero-pad) * .9) 0 calc(var(--hero-pad) * .6); }
  .hero h1 { font-size: clamp(2.6rem, 7vw, 5.4rem); font-weight: 300; letter-spacing: -.03em; max-width: 14ch; }
  .hero p { color: var(--doux); opacity: 1; font-size: 1.15rem; }
  .hero .bouton { background: var(--encre); color: var(--fond); }
  .hero .bouton.contour { background: transparent; color: var(--encre); border: 1px solid var(--ligne); }
  .hero-ligne { height: 1px; background: var(--ligne); margin-top: 20px; }
  .hero-visuel { height: clamp(240px, 40vw, 480px); margin-top: 10px; filter: grayscale(.2); }
  section[data-alterne="non"] { background: transparent; }
  section[data-alterne] { padding: 80px 0; }
  section[data-alterne] .conteneur { display: grid; grid-template-columns: 220px 1fr; gap: 40px; border-top: 1px solid var(--ligne); padding-top: 40px; }
  section[data-alterne] .conteneur > .bloc:not([data-edit$="-titre"]) { grid-column: 2; }
  .infos .conteneur { grid-template-columns: 1fr !important; }
  .titre-partie .trait, .infos .trait { display: none; }
  .titre-partie h2 { font-size: .85rem !important; font-weight: 600; text-transform: uppercase; letter-spacing: .14em; color: var(--doux); }
  .infos h2 { font-size: .85rem; text-transform: uppercase; letter-spacing: .14em; color: var(--doux); font-weight: 600; }
  .apropos p { font-size: 1.35rem; color: var(--encre); font-weight: 300; line-height: 1.6; }
  .service { border-bottom: 1px solid var(--ligne); padding: 18px 0; }
  .service .nom { font-weight: 400; }
  .service .prix { color: var(--encre); font-weight: 600; }
  .galerie-grille img { filter: grayscale(1); transition: filter .4s; }
  .galerie-grille img:hover { filter: none; }
  .bouton { background: var(--encre); color: var(--fond); }
  @media (max-width: 760px) {
    section[data-alterne] .conteneur { grid-template-columns: 1fr; gap: 14px; }
    section[data-alterne] .conteneur > .bloc { grid-column: 1 !important; }
  }
`;

    // ---------- 7. IMPACT ----------
    case "impact": return `
  header { background: var(--fond); }
  .logo { font-size: 1.6rem; }
  .hero { padding: calc(var(--hero-pad) * 1.1) 0 calc(var(--hero-pad) * 1.4); clip-path: polygon(0 0, 100% 0, 100% 88%, 0 100%); }
  .hero-texte { text-align: center; }
  .hero h1 { font-size: clamp(3.6rem, 13vw, 10rem); max-width: none; line-height: .9; margin: 0 auto; }
  .hero p { margin: 20px auto 36px; font-size: 1.3rem; font-weight: 600; }
  .hero .actions { justify-content: center; }
  .hero .bouton { background: var(--encre); color: var(--fond); font-size: 1.1rem; padding: 16px 30px; }
  .hero .bouton.contour { background: transparent; border-color: var(--hero-texte); color: var(--hero-texte); }
  section[data-alterne] { padding: 110px 0; }
  section[data-alterne="non"] { background: var(--accent); color: var(--sur-accent); }
  section[data-alterne="non"] .prix, section[data-alterne="non"] .horaire span:last-child, section[data-alterne="non"] .apropos p { color: var(--sur-accent); }
  section[data-alterne="non"] .trait { background: var(--sur-accent); }
  section[data-alterne="non"] .bouton { background: var(--encre); color: var(--fond); }
  section[data-alterne="non"] .service, section[data-alterne="non"] .horaire { border-color: color-mix(in srgb, var(--sur-accent) 30%, transparent); }
  .titre-partie h2 { font-size: clamp(3rem, 9vw, 6.5rem); line-height: .95; }
  .infos h2 { font-size: clamp(2.2rem, 6vw, 3.6rem); }
  .trait { height: 8px; width: 90px; border-radius: 0; }
  .apropos p { font-size: 1.35rem; color: var(--encre); font-weight: 500; }
  .service { padding: 22px 0; }
  .service .nom { font-family: var(--police-titre); font-size: 1.7rem; text-transform: uppercase; font-weight: 400; letter-spacing: .03em; }
  .service .prix { font-family: var(--police-titre); font-size: 1.7rem; font-weight: 400; }
  .galerie-grille img { border-radius: 0; }
  @media (max-width: 760px) {
    section[data-alterne] { padding: 70px 0; }
    .hero h1 { font-size: clamp(3rem, 15vw, 5rem); }
    .titre-partie h2 { font-size: clamp(2.3rem, 11vw, 3.4rem); }
    .service { gap: 10px; }
    .service .nom, .service .prix { font-size: 1.2rem; }
  }
`;

    // ---------- 8. GALERIE PHOTO ----------
    case "galerie": return `
  .hero { padding: 0; min-height: calc(460px + var(--hero-pad) * 1.6); display: grid; align-items: end; }
  .mosaique { position: absolute; inset: 0; display: grid; grid-template-columns: 2fr 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 6px; }
  .mosaique .tuile:first-child { grid-row: span 2; }
  .mosaique .tuile:nth-child(5) { display: none; }
  .hero-grille { padding: var(--hero-pad) 0 48px; }
  .hero-texte { background: var(--fond); color: var(--encre); padding: 38px 42px; border-radius: var(--rayon-img); max-width: 620px; box-shadow: 0 24px 60px rgba(0,0,0,.25); }
  .hero h1 { font-size: clamp(2.2rem, 5vw, 3.6rem); }
  .hero p { color: var(--doux); opacity: 1; margin: 14px 0 26px; }
  .hero .bouton.contour { border-color: var(--encre); color: var(--encre); }
  .galerie-grille { grid-template-columns: repeat(4, 1fr); grid-auto-rows: 220px; gap: 10px; }
  .galerie-grille img { height: 100%; aspect-ratio: auto; }
  .galerie-grille img:first-child { grid-column: span 2; grid-row: span 2; }
  .galerie-grille img:nth-child(4) { grid-column: span 2; }
  @media (max-width: 760px) {
    .mosaique { grid-template-columns: 1fr 1fr; }
    .mosaique .tuile:first-child { grid-row: span 1; grid-column: span 2; }
    .hero-texte { padding: 26px 22px; }
    .galerie-grille { grid-template-columns: 1fr 1fr; grid-auto-rows: 150px; }
  }
`;

    // ---------- 9. CARTE & MENU ----------
    case "menu": return `
  body { background-image: radial-gradient(color-mix(in srgb, var(--encre) 7%, transparent) 1px, transparent 1px); background-size: 22px 22px; }
  .entete-centre { background: var(--fond); }
  .entete-centre .conteneur { flex-direction: column; gap: 8px; padding: 20px 0 14px; position: relative; }
  .entete-centre .logo { font-size: 2.1rem; }
  .entete-centre nav a { font-style: italic; }
  .entete-centre .lien-appel { position: absolute; right: 0; top: 28px; }
  .hero-texte { text-align: center; }
  .hero h1 { margin: 0 auto; font-size: clamp(2.8rem, 8vw, 5.4rem); }
  .hero p { margin: 18px auto 32px; font-style: italic; font-size: 1.3rem; }
  .hero .actions { justify-content: center; }
  .ornement { display: block; font-size: 1.6rem; margin-bottom: 12px; color: var(--hero-texte); opacity: .7; }
  section[data-alterne="non"] { background: transparent; }
  section[data-alterne] { padding: 60px 0; }
  section[data-alterne] > .conteneur { max-width: 860px; background: var(--surface); padding: clamp(34px, 6vw, 64px); border: 1px solid var(--ligne); outline: 1px solid var(--ligne); outline-offset: -10px; }
  .titre-partie { text-align: center; }
  .titre-partie .z { display: block; }
  .titre-partie .trait { display: none; }
  .titre-partie h2 { display: flex; align-items: center; gap: 20px; font-size: clamp(1.9rem, 5vw, 2.8rem); }
  .titre-partie h2::before, .titre-partie h2::after { content: ""; flex: 1; height: 1px; background: color-mix(in srgb, var(--accent) 60%, transparent); }
  .apropos .bloc { text-align: center; }
  .apropos p { margin-inline: auto; font-size: 1.15rem; }
  .liste-services { max-width: none; }
  .service { border: 0; padding: 12px 0; }
  .service .points { border-bottom: 2px dotted color-mix(in srgb, var(--encre) 30%, transparent); transform: translateY(-5px); }
  .service .nom { font-family: var(--police-titre); font-size: 1.15rem; }
  .infos .trait { width: 30px; height: 2px; }
  @media (max-width: 760px) { .entete-centre .lien-appel { display: none; } section[data-alterne] { padding: 30px 0; } }
`;

    // ---------- 10. PRO ----------
    case "pro": return `
  .barre-infos { background: var(--accent); color: var(--sur-accent); }
  .hero-grille { grid-template-columns: 1.4fr 1fr; }
  .hero h1 { font-size: clamp(2.3rem, 5vw, 3.8rem); }
  .carte-contact { background: var(--fond); color: var(--encre); border-radius: var(--rayon-img); padding: 30px; box-shadow: 0 24px 60px rgba(0,0,0,.25); }
  .cc-titre { font-family: var(--police-titre); font-weight: 700; font-size: 1.3rem; margin-bottom: 14px; }
  .cc-ligne { display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--ligne); font-size: .95rem; }
  .cc-ligne a { text-decoration: none; font-weight: 700; color: var(--accent); }
  .titre-partie .trait { width: 44px; }
  .titre-partie h2 { font-size: clamp(1.8rem, 3.6vw, 2.4rem); }
  .liste-services { max-width: none; border: 1px solid var(--ligne); border-radius: var(--rayon-img); overflow: hidden; gap: 0; background: var(--fond); }
  .service { padding: 18px 24px; border-bottom: 1px solid var(--ligne); }
  .service:last-child { border-bottom: 0; }
  .service:nth-child(even) { background: color-mix(in srgb, var(--accent) 5%, var(--fond)); }
  .service .nom::before { content: "✓"; color: var(--accent); font-weight: 800; margin-right: 12px; }
  .infos-grille > .bloc { background: var(--fond); border: 1px solid var(--ligne); border-radius: var(--rayon-img); padding: 30px; }
`;
  }
  return "";
}

// ============================================================
//  MODE "DÉPLACER / AGRANDIR"
//  Ce script est ajouté dans l'aperçu seulement quand le mode est
//  activé dans l'éditeur. Il n'est JAMAIS dans le site final.
//  Il marche à la souris ET au doigt (téléphone, tablette).
// ============================================================
function scriptEdition() {
  var envoyer = function (msg) { msg.source = "vitrine-edit"; window.parent.postMessage(msg, "*"); };
  var BLEU = "#2f6bff";

  // ---------- Style : juste un cadre bleu autour de l'élément choisi ----------
  var css = document.createElement("style");
  css.textContent = [
    "body { -webkit-user-select: none; user-select: none; }",
    "header { position: static !important; }",
    "[data-edit] { cursor: pointer; }",
    ".carte { pointer-events: none; }",   // le plan Google ne "vole" plus les clics
    "@media (hover: hover) { [data-edit]:not(.choisi):hover > .z { outline: 2px dashed " + BLEU + "99; outline-offset: 4px; } }",
    "[data-edit].choisi { touch-action: none; cursor: move; }",
    "#cadre-edit { position: absolute; z-index: 9998; pointer-events: none; border: 3px solid " + BLEU + "; border-radius: 6px; display: none; box-shadow: 0 0 0 4px " + BLEU + "33; }",
    "#cadre-edit .poignee { position: absolute; right: -16px; bottom: -16px; width: 32px; height: 32px; border-radius: 50%; background: #fff; border: 3px solid " + BLEU + "; pointer-events: auto; cursor: nwse-resize; touch-action: none; box-shadow: 0 2px 8px rgba(0,0,0,.3); display: grid; place-items: center; font: 700 15px sans-serif; color: " + BLEU + "; }"
  ].join("\n");
  document.head.appendChild(css);

  // Dans l'éditeur, les liens ne doivent pas partir ailleurs
  document.addEventListener("click", function (e) {
    if (e.target.closest("a")) e.preventDefault();
  }, true);

  var cadre = document.createElement("div");
  cadre.id = "cadre-edit";
  cadre.innerHTML = '<div class="poignee" title="Tirer pour agrandir">↘</div>';
  document.body.appendChild(cadre);
  var poignee = cadre.querySelector(".poignee");

  var choisi = null;

  function interieur(bloc) { return bloc.querySelector(":scope > .z"); }
  function lire(bloc) {
    return { x: parseFloat(bloc.dataset.x) || 0, y: parseFloat(bloc.dataset.y) || 0, z: parseFloat(bloc.dataset.z) || 1 };
  }
  function appliquer(bloc, e) {
    bloc.style.left = e.x + "%";
    bloc.style.top = e.y + "px";
    interieur(bloc).style.zoom = e.z;
    bloc.dataset.x = e.x; bloc.dataset.y = e.y; bloc.dataset.z = e.z;
  }

  function placerCadre() {
    if (!choisi) { cadre.style.display = "none"; return; }
    var r = interieur(choisi).getBoundingClientRect();
    cadre.style.display = "block";
    cadre.style.left = (r.left + window.scrollX - 7) + "px";
    cadre.style.top = (r.top + window.scrollY - 7) + "px";
    cadre.style.width = (r.width + 14) + "px";
    cadre.style.height = (r.height + 14) + "px";
    // Le rond reste toujours dans l'écran (important sur téléphone)
    var deborde = (r.right + 7 + 16) - (document.documentElement.clientWidth - 4);
    poignee.style.right = (deborde > 0 ? -16 + deborde : -16) + "px";
  }

  // Dit à l'éditeur ce qui est choisi (pour afficher les bons boutons)
  function choisir(bloc, defiler) {
    if (choisi) choisi.classList.remove("choisi");
    choisi = bloc;
    var info = null;
    if (bloc) {
      bloc.classList.add("choisi");
      var section = bloc.closest("section[data-alterne]");
      var toutes = Array.prototype.slice.call(document.querySelectorAll("section[data-alterne]"));
      var i = section ? toutes.indexOf(section) : -1;
      info = {
        id: bloc.dataset.edit,
        partie: section ? section.id : null,
        premiere: i === 0,
        derniere: i === toutes.length - 1
      };
      if (defiler) {
        var r = interieur(bloc).getBoundingClientRect();
        if (r.top < 0 || r.bottom > window.innerHeight) window.scrollTo(0, r.top + window.scrollY - 80);
      }
    }
    placerCadre();
    envoyer({ type: "choisi", info: info });
  }

  window.addEventListener("scroll", placerCadre, { passive: true });
  window.addEventListener("resize", placerCadre);

  // L'éditeur envoie des ordres : choisir un élément, appliquer une taille/position
  window.addEventListener("message", function (e) {
    var m = e.data || {};
    if (m.source !== "vitrine-editeur") return;
    if (m.type === "choisir") {
      var bloc = document.querySelector('[data-edit="' + m.id + '"]');
      choisir(bloc, true);
    }
    if (m.type === "appliquer" && choisi && choisi.dataset.edit === m.id) {
      appliquer(choisi, m);
      placerCadre();
    }
    if (m.type === "deselectionner") choisir(null);
  });

  // ---------- Toucher pour choisir, glisser pour déplacer ----------
  var glisse = null;

  document.addEventListener("pointerdown", function (e) {
    if (e.target.closest("#cadre-edit")) return;
    var bloc = e.target.closest("[data-edit]");
    if (!bloc || bloc !== choisi) {
      // Premier toucher : on choisit seulement (la page peut encore défiler au doigt)
      glisse = { aChoisir: bloc, sx: e.clientX, sy: e.clientY };
      return;
    }
    e.preventDefault();
    glisse = { bloc: bloc, sx: e.clientX, sy: e.clientY, depart: lire(bloc), largeur: bloc.parentElement.clientWidth || 1, bouge: false };
    try { bloc.setPointerCapture(e.pointerId); } catch (err) {}
  });

  document.addEventListener("pointermove", function (e) {
    if (!glisse || !glisse.bloc) return;
    var dx = e.clientX - glisse.sx, dy = e.clientY - glisse.sy;
    if (!glisse.bouge && Math.abs(dx) + Math.abs(dy) < 4) return;
    glisse.bouge = true;
    var x = glisse.depart.x + (dx / glisse.largeur) * 100;
    var y = glisse.depart.y + dy;
    if (Math.abs(x) < 1.5) x = 0;   // aimant : revient pile à sa place d'origine
    if (Math.abs(y) < 6) y = 0;
    appliquer(glisse.bloc, { x: Math.round(x * 100) / 100, y: Math.round(y), z: glisse.depart.z });
    placerCadre();
  });

  document.addEventListener("pointerup", function (e) {
    if (!glisse) return;
    if (!glisse.bloc) {
      if (Math.abs(e.clientX - glisse.sx) + Math.abs(e.clientY - glisse.sy) < 10) choisir(glisse.aChoisir);
    } else if (glisse.bouge) {
      var a = lire(glisse.bloc);
      envoyer({ type: "ajuster", id: glisse.bloc.dataset.edit, x: a.x, y: a.y, z: a.z });
    }
    glisse = null;
  });
  document.addEventListener("pointercancel", function () { glisse = null; });

  // ---------- Tirer le rond pour agrandir ----------
  poignee.addEventListener("pointerdown", function (e) {
    if (!choisi) return;
    e.preventDefault(); e.stopPropagation();
    var r = interieur(choisi).getBoundingClientRect();
    var depart = lire(choisi);
    var sx = e.clientX, sy = e.clientY;
    try { poignee.setPointerCapture(e.pointerId); } catch (err) {}
    function bouger(ev) {
      var gx = (r.width + (ev.clientX - sx)) / r.width;
      var gy = (r.height + (ev.clientY - sy)) / r.height;
      var g = Math.abs(gx - 1) > Math.abs(gy - 1) ? gx : gy;
      var z = Math.min(3, Math.max(0.4, depart.z * g));
      if (Math.abs(z - 1) < 0.04) z = 1;
      appliquer(choisi, { x: depart.x, y: depart.y, z: Math.round(z * 100) / 100 });
      placerCadre();
    }
    function fin() {
      poignee.removeEventListener("pointermove", bouger);
      poignee.removeEventListener("pointerup", fin);
      poignee.removeEventListener("pointercancel", fin);
      var a = lire(choisi);
      envoyer({ type: "ajuster", id: choisi.dataset.edit, x: a.x, y: a.y, z: a.z });
    }
    poignee.addEventListener("pointermove", bouger);
    poignee.addEventListener("pointerup", fin);
    poignee.addEventListener("pointercancel", fin);
  });

  envoyer({ type: "pret" });
}
