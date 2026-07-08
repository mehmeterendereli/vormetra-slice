# CLAUDE.md — VORMETRA Slice

Bu repo = **VORMETRA Slice**, VORMETRA G1000 için dilimleyici (OrcaSlicer'ın
AGPLv3 fork'u). **Public** (2026-07-07'den beri, ADR-047 — kurucu kararı: AGPL
uyumunu netleştirmek için motor+profiller baştan açık kaynak). Ana bilgi
tabanı AYRI, **gizli** repodadır
(`github.com/mehmeterendereli/vormetra`: ürün/mühendislik/iş/fon/ADR'ler).

> ⚠️ **Buraya gizli bilgi (fon, finans, strateji, iç kararlar) KOYMA — bu repo
> herkese açık, geri dönüşü yok.**

## Rol & Yetki (ana bilgi tabanıyla aynı model)

Mehmet Eren Dereli'nin **sahip-mühendis zihniyetiyle** çalış; proaktif ol.
**§3 kurucuya aittir:** para, hukuk, geri dönüşü olmayan üretim, gerçek bir
"VORMETRA Slice v1.0" sürümünü müşteriye dağıtmak. Kod yazma/profil
geliştirme/dahili test §2 (Claude'un yetkisi) — bkz. ana repo `CLAUDE.md` §2/§3.

## 🔓 AGPLv3 + açık kaynak kararı (ADR-043/047'de tam kayıt)

Fork yasal ve yaygın (Bambu/Creality/Snapmaker aynısını yapıyor). Kurucu
2026-07-07'de **motor + profillerin baştan açık kaynak olmasına** karar
verdi — bu, AGPL'in dağıtımda kaynak-açma yükümlülüğünü baştan karşılıyor,
belirsizlik kalmadı. `vera-control/` ayrı bir program (motoru CLI üzerinden
çağırıyor, AGPL kapsamına girmiyor) — kurucu onu da açık kaynak (MIT) yapmayı
seçti, zorunluluktan değil, topluluk katkısı için. Detay: ana repo
`DECISIONS.md` ADR-014/043/047.

## Mimari ilkesi: "ince fork" (thin fork)

OrcaSlicer C++ çekirdeğini (`src/`, `deps/`, `cmake/`) mümkün olduğunca
DEĞİŞTİRME. VORMETRA katmanı:
- `resources/profiles/VORMETRA/` — G1000 makine + malzeme profilleri (veri, kod değil)
- `vera-control/` — AI/insan kontrol katmanı (ayrı Python paketi, çekirdeğe dokunmaz)
- `version.inc`, root `README.md` — marka kimliği (minimal, mekanik değişiklik;
  native GUI'deki (About dialog, splash) daha derin string rebrand'i henüz
  YAPILMADI — bilinçli kapsam dışı bırakıldı, bkz. `CHANGELOG.md`)

Delta küçük tutulursa upstream merge'leri kolay kalır, küçük ekiple
sürdürülebilir. Upstream'e gerçek pellet iyileştirmeleri PR olarak
gönderilebilir (moat kodda değil — donanım/malzeme/servis/marka, bkz. ADR-014).

## Profil geliştirirken

`resources/profiles/VORMETRA/README.md`'yi ÖNCE oku — orada CLI'nin doğrudan
dosya-yükleme yolundaki gerçek, doğrulanmış tuhaflıkları var (leaf dosyada
tekrarlanması gereken alanlar, Marlin/Klipper G92-E0 kontrolü,
`pellet_flow_coefficient` dönüşümü CLI'de çalışmıyor vb.) — bunları tekrar
keşfetmeye çalışmadan önce oku. Uydurma sayı yok (CLAUDE.md §4, ana repo) —
gerçek G1000 verisi yoksa `TBD` bırak, kaynağı belirt.

## vera-control geliştirirken

`vera-control/README.md`'yi oku. Testler `python -m pytest` ile
`vera-control/` içinden çalışır; gerçek motor testi `VERA_SLICER_BIN` set
edilmezse otomatik atlanır (CI/offline için güvenli varsayılan).

## Subagent / Paralel Ajan Sınırı

Agent/Task/Workflow ile **aynı anda en fazla 3 subagent** — ana repo ADR-019.
Haiku gibi küçük modellere görev verirken **"kendi alt-ajanını AÇMA, aracı
doğrudan sen çağır"** talimatını baştan ver — bu depoda gerçek bir olay
yaşandı (ADR-043'te kayıtlı), aynı hatayı tekrarlama.

## C++ çekirdeği üzerinde çalışırken (yukarı akıştan devralınan referans)

- **Derleme:** Windows: `build_release_vs2022.bat` (bu depoya özel) veya
  `cmake --build . --config Release --target ALL_BUILD -- -m` (build/ içinden,
  deps zaten derlenmişse). macOS: `cmake --build build/arm64 --config
  RelWithDebInfo --target all --`. Linux: `cmake --build build --config
  RelWithDebInfo --target all --`.
- **Test:** Catch2, `tests/` altında. `cd build && ctest --output-on-failure`
  (tümü) veya `ctest --test-dir ./tests/libslic3r` (tek suite).
- **Kod stili:** C++17 (kısmen C++20), PascalCase sınıflar, snake_case
  fonksiyon/değişken, `#pragma once`, akıllı pointer/RAII tercih edilir, TBB
  paralelleştirme (paylaşılan state'e dikkat).
- **Kritik giriş noktaları:** uygulama başlangıcı `src/OrcaSlicer.cpp`;
  dilimleme hattı `src/libslic3r/Print.cpp`; tüm baskı/yazıcı/malzeme
  ayarları `src/libslic3r/PrintConfig.cpp`; GUI `src/slic3r/GUI/`; çekirdek
  algoritmalar `src/libslic3r/{GCode,Fill,Support,Geometry,Format,Arachne}/`;
  üretici profilleri `resources/profiles/[üretici].json`.
- **Kritik kısıtlar:** `.3mf` proje dosyaları ve yazıcı profilleri için **geri
  uyumluluk** şart; **çapraz platform** (Windows/macOS/Linux) tüm
  değişikliklerde geçerli olmalı; profil/format değişiklikleri sürüm göçü
  (migration) gerektirir; bağımlılıklar ayrı derlenip (`deps/build/`) ana
  uygulamaya bağlanır.

## Kaynak

Ana bilgi tabanı + işletim tüzüğü: `github.com/mehmeterendereli/vormetra`
(private). Dijital ekip (Rector/Augur/Nuntia/Faber) + çağırma komutları: o
repodaki `DIZIN_HARITASI.md`.
