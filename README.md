# VORMETRA Slice

Dilimleyici (slicer) yazılımı, **VORMETRA G1000** — granül beslemeli (FGF/pellet)
büyük format endüstriyel 3D yazıcı — için. [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer)'ın
AGPLv3 fork'u (kararı: ana bilgi tabanı reposundaki `DECISIONS.md` ADR-014/043).

**Durum:** Aktif geliştirme. G1000 vendor profili (`resources/profiles/VORMETRA/`)
uçtan uca doğrulandı (gerçek dilimleme testi). Native GUI rebrand'i sürüyor.

## Bu depoda ne var

- `resources/profiles/VORMETRA/` — G1000 makine profili + PLA/PETG pellet malzeme
  profilleri. Hangi değerin gerçek G1000 verisinden geldiği, hangisinin referans
  makineden (Ginger Additive) alınmış kalibre-edilecek başlangıç noktası olduğu
  o klasörün kendi `README.md`'sinde açıkça ayrılmıştır.
- `vera-control/` — slicer'ı **programatik olarak** kontrol eden katman: Claude
  Code / diğer AI ajanları için MCP sunucusu, herhangi bir istemci için HTTP API,
  ve web tabanlı "Vera Console" arayüzü. Detay: `vera-control/README.md`.
- Geri kalan her şey (`src/`, `deps/`, `cmake/`, build script'leri...) yukarı akış
  (upstream) OrcaSlicer kod tabanı — "ince fork" ilkesiyle mümkün olduğunca az
  değiştirilmiştir (bkz. `CLAUDE.md`).

## Başlarken

**Profil geliştirme / kontrol katmanı** (C++ derlemesi gerekmez): resmi
OrcaSlicer sürümünü indirin, `vera-control/README.md`'deki talimatları izleyin.

**Motoru kaynaktan derlemek:** yukarı akışın kendi `README.upstream.md` /
GitHub wiki talimatları geçerli (VS2022 + "Desktop development with C++" +
CMake 4.x). Bu depoda `build_release_vs2022.bat` kullanılır.

## Yönetişim

Bu repo `github.com/mehmeterendereli/vormetra-slice` (**public**, 2026-07-07'den
beri — ADR-047) — ana bilgi tabanı ve işletim tüzüğü ayrı, gizli bir repoda:
`github.com/mehmeterendereli/vormetra` (`DECISIONS.md`, `CLAUDE.md`,
`software/slicer/`). Bu reponun kendi `CLAUDE.md`/`AGENTS.md`/`CHANGELOG.md`'si
var — `vormetra-web` reposuyla aynı desen.

## Lisans

**İki ayrı lisans, bilinçli olarak:**
- **Motor + profiller** (`src/`, `resources/`, geri kalan her şey): **AGPLv3**
  (yukarı akıştan devralındı — `LICENSE.txt`). Repo public olduğu için kaynak
  açma yükümlülüğü baştan karşılanmış durumda — belirsizlik yok.
- **`vera-control/`**: **MIT** (`vera-control/LICENSE`) — ayrı bir program,
  motoru CLI/subprocess üzerinden çağırıyor, AGPL'in kapsamına girmiyor;
  topluluk katkısına açık olsun diye bilinçli olarak MIT seçildi.

Karar + gerekçe: ana bilgi tabanı reposunda `DECISIONS.md` ADR-047. Orijinal
OrcaSlicer README'si (kredi/topluluk bağlantıları dahil) `README.upstream.md`'de
korunmuştur.
