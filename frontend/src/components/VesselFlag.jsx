// src/components/VesselFlag.jsx
import React from 'react';

// MID (Maritime Identification Digits) to ISO country code map
const MID_TO_ISO = {
  201: 'al', 202: 'ad', 203: 'at', 204: 'pt', 205: 'be', 206: 'by', 207: 'bg', 208: 'va',
  209: 'cy', 210: 'cy', 211: 'de', 212: 'cy', 213: 'ge', 214: 'md', 215: 'mt', 216: 'am',
  218: 'de', 219: 'dk', 220: 'dk', 224: 'es', 225: 'es', 226: 'fr', 227: 'fr', 228: 'fr',
  229: 'mt', 230: 'fi', 231: 'fo', 232: 'gb', 233: 'gb', 234: 'gb', 235: 'gb', 236: 'gi',
  237: 'gr', 238: 'hr', 239: 'gr', 240: 'gr', 241: 'gr', 242: 'ma', 243: 'hu', 244: 'nl',
  245: 'nl', 246: 'nl', 247: 'it', 248: 'mt', 249: 'mt', 250: 'ie', 251: 'is', 252: 'li',
  253: 'lu', 254: 'mc', 255: 'pt', 256: 'mt', 257: 'no', 258: 'no', 259: 'no', 261: 'pl',
  262: 'me', 263: 'sk', 264: 'si', 265: 'se', 266: 'se', 267: 'ba', 268: 'cs', 269: 'cz',
  270: 'ua', 271: 'mk', 272: 'ru', 273: 'ru', 274: 'mk', 275: 'lv', 276: 'ee', 277: 'lt',
  278: 'sk', 279: 'si', 301: 'ai', 303: 'us', 304: 'ag', 305: 'ag', 306: 'cw', 307: 'aw',
  308: 'bs', 309: 'bs', 310: 'bm', 311: 'bs', 312: 'bz', 314: 'bb', 316: 'ca', 319: 'ky',
  321: 'cr', 323: 'cu', 325: 'dm', 327: 'do', 329: 'gd', 331: 'gl', 332: 'gt', 334: 'hn',
  336: 'ht', 338: 'us', 339: 'jm', 341: 'kn', 343: 'lc', 345: 'vc', 347: 'mx', 348: 'mx',
  350: 'ni', 351: 'pa', 352: 'pa', 353: 'pa', 354: 'pa', 355: 'pa', 356: 'pa', 357: 'pa',
  358: 'pa', 359: 'pa', 361: 'pa', 362: 'sv', 364: 'tc', 366: 'us', 367: 'us', 368: 'us',
  369: 'us', 370: 'pa', 371: 'pa', 372: 'pa', 373: 'pa', 375: 'vc', 376: 'vc', 377: 'vc',
  378: 'vc', 379: 'vc', 401: 'af', 403: 'sa', 405: 'bd', 408: 'bh', 410: 'bt', 412: 'cn',
  413: 'cn', 414: 'cn', 415: 'lk', 416: 'cx', 417: 'cx', 419: 'in', 420: 'in', 422: 'ir',
  423: 'az', 425: 'iq', 428: 'il', 431: 'jp', 432: 'jp', 434: 'tm', 436: 'kz', 437: 'uz',
  438: 'jo', 440: 'kr', 441: 'kr', 443: 'ps', 445: 'kp', 447: 'kw', 450: 'lb', 451: 'kg',
  453: 'mo', 455: 'mv', 456: 'mn', 457: 'np', 459: 'om', 461: 'pk', 463: 'qa', 466: 'sy',
  467: 'tj', 470: 'ae', 472: 'uz', 473: 'ye', 475: 'et', 477: 'er', 478: 'fo', 480: 'ph',
  481: 'ph', 482: 'ph', 483: 'ph', 484: 'pk', 485: 'pk', 486: 'pk', 488: 'th', 489: 'th',
  490: 'jp', 493: 'vn', 494: 'vn', 495: 'vn', 496: 'id', 497: 'id', 498: 'id', 499: 'my',
  501: 'my', 503: 'au', 506: 'mm', 508: 'bn', 510: 'fm', 511: 'pw', 512: 'pg', 514: 'tl',
  515: 'nu', 516: 'nz', 518: 'ck', 520: 'fj', 523: 'ws', 525: 'nr', 529: 'to', 531: 'tv',
  533: 'vu', 536: 'as', 538: 'us', 542: 'eg', 544: 'dz', 546: 'ma', 548: 'tn', 550: 'ly',
  551: 'gm', 552: 'sn', 553: 'mr', 554: 'ml', 555: 'gn', 556: 'ci', 557: 'bf', 558: 'ne',
  559: 'tg', 560: 'bj', 561: 'mu', 563: 'sc', 564: 'tz', 565: 'ke', 566: 'ug', 567: 'bi',
  568: 'rw', 569: 'et', 570: 'so', 572: 'sh', 574: 'sd', 576: 'mg', 577: 're', 578: 'ao',
  579: 'cg', 580: 'ga', 581: 'gq', 582: 'cm', 583: 'cv', 584: 'st', 586: 'dz', 601: 'za',
  603: 'zm', 605: 'mz', 607: 'bw', 608: 'sz', 609: 'ls', 610: 'na', 611: 'mw', 612: 'cd',
  613: 'zw', 615: 'er', 616: 'mw', 701: 'ar', 710: 'br', 720: 'bo', 725: 'cl', 730: 'co',
  735: 'ec', 740: 'fk', 745: 'gf', 750: 'gy', 755: 'py', 760: 'pe', 765: 'sr', 770: 'uy',
  775: 've', 777: 'sr', 780: 've'
};

const VesselFlag = ({ mmsi }) => {
  const mid = parseInt(String(mmsi).slice(0, 3));
  const iso = MID_TO_ISO[mid];
  const flagUrl = iso ? `https://flagcdn.com/48x36/${iso}.png` : 'https://flagcdn.com/48x36/gb.png';

  return (
    <img
      src={flagUrl}
      alt={iso ? `Flag of ${iso.toUpperCase()}` : 'UK Flag'}
      style={{
        width: '32px',
        height: '24px',
        borderRadius: '3px',
        objectFit: 'contain',
        backgroundColor: '#fff',
        border: '1px solid #ccc',
        marginRight: '8px'
      }}
      onError={(e) => {
        e.target.onerror = null;
        e.target.src = 'https://flagcdn.com/48x36/gb.png';
      }}
    />
  );
};

export default VesselFlag;
