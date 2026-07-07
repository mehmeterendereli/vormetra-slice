# CHANGELOG — VORMETRA Slice

Format: [Keep a Changelog] esinli, tarih = ISO (YYYY-AA-GG). En yeni üstte.
Yukarı akış (OrcaSlicer) commit geçmişi ayrı tutulur — bu dosya yalnızca
VORMETRA katmanındaki değişiklikleri kaydeder.

## [0.1.0] — 2026-07-07

### Eklendi (Added)
- Fork başlatıldı: `github.com/OrcaSlicer/OrcaSlicer` tam git geçmişiyle
  klonlandı, `upstream` remote olarak eklendi (`git fetch upstream` ile
  gelecekte senkron edilebilir), `origin` bu repoya (private) işaret ediyor.
- `resources/profiles/VORMETRA/` — G1000 vendor profili: makine (1000×1000×1000mm,
  Ø5.0 nozül, Klipper gcode_flavor), 2 malzeme (PETG — OQ-03 önerilen ilk
  malzeme, PLA), process profili. **Resmi OrcaSlicer v2.4.2 ile uçtan uca
  gerçek dilimleme testiyle doğrulandı** (200×200×100mm test küpü → doğru
  katman sayısı, doğru ekstrüzyon genişliği, doğru pellet flow matematiği,
  doğru bed_shape). 4 gerçek CLI/profil hatası bulunup düzeltildi — detay:
  `resources/profiles/VORMETRA/README.md`.
- `vera-control/` — AI-kontrol katmanı: `slicer_bridge.py` (CLI wrapper),
  `api.py` (stdlib HTTP API + Vera Console statik dosya sunumu), `mcp_server.py`
  (Claude Code + diğer MCP-uyumlu ajanlar için native araçlar:
  `list_filaments`/`get_machine_limits`/`validate_model`/`slice_stl`).
  14 test (pytest), gerçek motora karşı da doğrulandı. Web konsolu
  (`vera_control/console/index.html`) tarayıcıda canlı test edildi (health
  check, profil listesi, gerçek dilimleme çağrısı — hepsi uçtan uca çalıştı).
- Marka: `version.inc` (`SLIC3R_APP_NAME`/`SLIC3R_APP_KEY` → "VORMETRA Slice"),
  root `README.md` VORMETRA'ya özel yeniden yazıldı (orijinali
  `README.upstream.md`'de korundu). Native GUI (About dialog, splash) rebrand'i
  **henüz yapılmadı** — bilinçli kapsam dışı (bkz. CLAUDE.md).
- `CLAUDE.md`/`AGENTS.md` — bu reponun işletim tüzüğü (ana bilgi tabanı
  reposundaki desenle aynı; C++ çekirdeği için yukarı akışın kendi
  derleme/test/kod-stili notları korunup entegre edildi).

### Devam eden (In progress)
- Kaynaktan tam derleme (`build_release_vs2022.bat`, VS2022 BuildTools +
  CMake 4.x) — ilk deps derlemesi arka planda çalışıyor (Boost/OCCT/CGAL/
  wxWidgets — uzun sürüyor, saatler alabilir).

### Bilinen eksikler / sonraki adımlar
- `pellet_flow_coefficient` gerçek G1000'de kalibre edilmedi (nötr "1"
  değerinde — TBD).
- Native GUI'ye gömülü Vera sohbet paneli yok (C++ işi, ayrı kapsam).
- `machine_start_gcode`'daki 4-bölge/vida-hacmi parametreli tam makro
  sadeleştirildi (vanilla OrcaSlicer'da özel değişken kaydı yok) — CTL-01
  (Klipper vs LinuxCNC) netleşince ve firmware makro tasarımı yapılınca
  genişletilecek.
- Vera Console'un LLM sohbet motoru henüz bağlı değil (API anahtarı §3,
  kurucuya ait — ADR-017 emsali).
