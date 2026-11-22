// Le plan d'éclairage réglementaire de la rue des Trois-Soleils (ILE_03_COLONIE.md, G2).
// Une seule affiche, déchirée en trois : chaque page plan_eclairage_<a|b|c>.html la dessine en entier
// puis n'en garde que son morceau (clip-path). Rendu : 1100 × 1300, feuille de 1060 × 1260.
(function () {
  var morceau = document.body.getAttribute("data-morceau");
  // Motif des Trois-Soleils : rangée du haut = la plus proche de la porte.
  var motif = ["101", "000", "010"];
  var colonnes = [310, 530, 750], rangees = [530, 745, 960], r = 56;
  var decoupes = {
    A: "0 0,640 0,655 90,628 180,662 300,640 400,665 470,648 560,668 628,560 640,450 622,330 646,210 624,100 642,0 628",
    B: "680 440,800 428,930 446,1060 432,1060 858,940 842,820 866,700 840,580 864,460 838,340 862,220 840,100 858,0 842,0 672,110 660,220 682,340 662,460 684,575 664,690 676,672 600,692 520",
    C: "0 900,120 886,250 908,380 884,520 896,650 888,780 898,900 890,1060 906,1060 1260,0 1260"
  };
  var poly = decoupes[morceau].split(",").map(function (p) {
    var xy = p.trim().split(" ");
    return xy[0] + "px " + xy[1] + "px";
  }).join(", ");

  var svg = '<svg class="dessin" viewBox="0 0 1060 1260" xmlns="http://www.w3.org/2000/svg">' +
    '<defs><filter id="plume" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="4" result="b"/><feDisplacementMap in="SourceGraphic" in2="b" scale="2.2"/></filter>' +
    '<radialGradient id="soleil" cx=".45" cy=".4"><stop offset="0" stop-color="#ffe3a0"/><stop offset=".65" stop-color="#e6b85a"/><stop offset="1" stop-color="#c8923a"/></radialGradient></defs>' +
    '<g filter="url(#plume)" stroke-linecap="round" stroke-linejoin="round">';
  // La façade de la maison commune, en haut : on sait d'un coup d'œil où est la porte.
  svg += '<path d="M360 420 V300 L530 236 L700 300 V420" fill="#efe1c2" stroke="#4f3624" stroke-width="3"/>' +
    '<path d="M480 420 V340 Q530 300 580 340 V420" fill="#c89a3f" fill-opacity=".35" stroke="#4f3624" stroke-width="3"/>' +
    '<path d="M530 312 V420" stroke="#4f3624" stroke-width="2"/>' +
    '<circle cx="530" cy="276" r="9" fill="none" stroke="#c89a3f" stroke-width="2.5"/>' +
    '<path d="M330 420 H730" stroke="#4f3624" stroke-width="3"/>';
  // Les gaines : de chaque lanterne vers la porte, en pointillé.
  for (var i = 0; i < 3; i++) for (var j = 0; j < 3; j++) {
    svg += '<path d="M' + colonnes[j] + ' ' + (rangees[i] - r) + ' Q' + colonnes[j] + ' 450 ' + (515 + j * 15) + ' 424" fill="none" stroke="#8a6a4f" stroke-width="1.6" stroke-dasharray="3 7" opacity=".7"/>';
  }
  // Les neuf lanternes : un soleil doré si elle doit être allumée, un rond d'encre sinon.
  for (var i = 0; i < 3; i++) for (var j = 0; j < 3; j++) {
    var x = colonnes[j], y = rangees[i];
    if (motif[i][j] === "1") {
      for (var k = 0; k < 8; k++) {
        var a = k * Math.PI / 4;
        svg += '<path d="M' + (x + Math.cos(a) * (r + 10)) + ' ' + (y + Math.sin(a) * (r + 10)) + ' L' + (x + Math.cos(a) * (r + 30)) + ' ' + (y + Math.sin(a) * (r + 30)) + '" stroke="#c8923a" stroke-width="6"/>';
      }
      svg += '<circle cx="' + x + '" cy="' + y + '" r="' + r + '" fill="url(#soleil)" stroke="#9a6a2a" stroke-width="3.5"/>';
    } else {
      svg += '<circle cx="' + x + '" cy="' + y + '" r="' + r + '" fill="#f4ead3" stroke="#4f3624" stroke-width="3.5"/>' +
        '<circle cx="' + x + '" cy="' + y + '" r="' + (r - 14) + '" fill="none" stroke="#4f3624" stroke-width="1.4" opacity=".45"/>';
    }
  }
  svg += '</g></svg>';

  var html =
    '<div class="feuille" style="clip-path: polygon(' + poly + ')">' +
    '<svg class="grain" xmlns="http://www.w3.org/2000/svg"><filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" seed="12"/><feColorMatrix values="0 0 0 0 0.45  0 0 0 0 0.36  0 0 0 0 0.25  0 0 0 0.3 0"/></filter><rect width="100%" height="100%" filter="url(#g)"/></svg>' +
    '<div class="cadre"></div>' +
    '<div class="titre">Éclairage réglementaire</div>' +
    '<div class="rue">de la rue des Trois-Soleils</div>' +
    '<div class="porte">porte de la maison commune</div>' +
    svg +
    '<div class="legende"><span class="s">☀</span> allumée &nbsp;·&nbsp; <span class="o">○</span> éteinte</div>' +
    '<div class="signe">par ordre de la Commandante <span>Ysolde</span></div>' +
    '<div class="age"></div>' +
    '</div>';
  document.body.insertAdjacentHTML("beforeend", html);
})();
