# CHANGELOG — VORMETRA Slice

Format: [Keep a Changelog] esinli, tarih = ISO (YYYY-AA-GG). En yeni üstte.
Yukarı akış (OrcaSlicer) commit geçmişi ayrı tutulur — bu dosya yalnızca
VORMETRA katmanındaki değişiklikleri kaydeder.

## [0.1.3] — 2026-07-16

### Düzeltildi (Fixed) — CTL-01 (Klipper vs LinuxCNC) zincir kırığı kapatıldı
- Kontrol platformu ADR-060 (2026-07-09) ile LinuxCNC'ye kilitlendiği hâlde profil
  hâlâ Ginger Additive'in Klipper şablonunu taşıyordu (`gcode_flavor: klipper` +
  `START_PRINT`/`PRINT_START`/`END_PRINT`/`PRINT_END` makro çağrıları +
  `enable_pressure_advance` → `SET_PRESSURE_ADVANCE`). Harici CAD reposundaki
  post-processor (`fgf_post.py`, salt-okunur okundu) girdi sözleşmesini açıkça
  "Marlin lehçesi" olarak belgeliyor; makro satırları onun G-code kelime
  ayrıştırıcısına uymadığı için **sessizce düşüyordu** — ön-ısıtma sıcaklığı hiçbir
  zaman `.ngc` çıktısına taşınmıyordu.
- `gcode_flavor: klipper → marlin` (3 machine JSON'u); `machine_start_gcode`/
  `machine_end_gcode` makro yerine düz M104/M109/G92 E0; `machine_pause_gcode`
  (Klipper `PAUSE`) boşaltıldı (LinuxCNC pause sözleşmesi henüz tasarlanmadı, TBD);
  `enable_pressure_advance: 1 → 0` (her iki filament — Klipper'a özgü, koordineli U
  ekseni mimarisinde anlamsız/yanıltıcı).
- Uçtan uca doğrulandı: resmi CLI ile 200×200×100mm test küpü yeniden dilimlendi
  (50 katman, 2026-07-07 sonucuyla birebir), sıfır Klipper makro izi, gerçek
  M104/M109 satırları; çıktı doğrudan `fgf_post.py`'den geçirildi — hatasız `.ngc`
  (M68 E0 Q245/Q240/Q0 + koordineli U hareketleri). +2 kalıcı regresyon testi
  (`test_slicer_bridge.py`, biri `VERA_FGF_POST_PATH` yoksa skip). Tam suite
  **30 passed**. Detay: `resources/profiles/VORMETRA/README.md` "CTL-01 KAPANDI"
  bölümü, ana repo `DECISIONS.md` ADR-129, `ACTION_PLAN.md`.

## [0.1.2] — 2026-07-10

### Düzeltildi (Fixed) — bug-hunt turunda doğrulanan 5 gerçek bug (vera-control)
- **Güvenlik — localhost drive-by CSRF (`api.py`):** kimliksiz yerel API + wildcard
  `Access-Control-Allow-Origin: *` yüzünden herhangi bir kötücül web sayfası
  `POST /slice` ile keyfi `stl_path`'i yerel subprocess+disk'e geçirebiliyordu.
  Wildcard CORS kaldırıldı + `do_POST`'a Origin/Host loopback kontrolü (CSRF +
  DNS-rebinding). Aynı-origin Vera Console etkilenmez.
- **`slicer_bridge._pid_is_running`:** Windows'ta `os.kill(pid, 0)` canlılık kontrolü
  değil (CTRL_C_EVENT==0 → ölü PID'e True); ölü `slice.lock` asla temizlenmiyordu
  (kalıcı sahte-meşgul 409). `OpenProcess`+`GetExitCodeProcess` dalı eklendi.
- **`_slice_lock_is_active`:** bozuk/eksik kilit dosyasında koşulsuz `True` → kilit
  asla temizlenmiyordu. Bozuk kilit temizlenir; yabancı-OS kilidi için mtime-TTL failsafe.
- **`slice_model`:** `subprocess.run` `TimeoutExpired`'i yakalanmıyordu → "her hata
  VeraSlicerError döner" sözleşmesi büyük modelde bozuluyordu. `→ VeraSlicerError` (API 422).
- **`_read_slice_lock`:** `except OSError` `UnicodeDecodeError`'ı kaçırıp ASCII-dışı
  baytlı kilitte `is_slice_running()`/`GET /health`'i çökertiyordu. `→ except (OSError,
  UnicodeDecodeError)`.
- Testler: +8 yeni test (gerçek ölü-PID, bozuk/non-ASCII kilit, timeout→hata, cross-origin/
  DNS-rebind 403). Tam suite **27 passed, 1 skipped**. Kaynak: ana repo
  `docs/BUG_HUNT_SATELLITE_20260710.md`. Lisans değişmez (motor AGPLv3, vera-control MIT).

## [0.1.1] — 2026-07-08

### Değiştirildi (Changed) — Açık kaynak yapıldı (ADR-047, ana repo)
- Bu repo **public** yapıldı. Motor + `resources/profiles/VORMETRA/` AGPLv3
  altında kalıyor (yukarı akıştan devralınan lisans) — repo public olduğu
  için dağıtımda kaynak-açma yükümlülüğü baştan karşılanmış durumda.
- `vera-control/` ayrıca **MIT** ile lisanslandı (`vera-control/LICENSE`) —
  AGPL bunu zorunlu kılmıyordu, kurucu topluluk katkısı için tercih etti.
- `README.md`/`CLAUDE.md`/`AGENTS.md` bu kararı yansıtacak şekilde güncellendi.

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
  CMake 4.x): deps derlemesi (Boost/OCCT/CGAL/wxWidgets, ~saatler sürdü)
  **tamamlandı**; ana uygulama `cmake configure` adımı **OpenSSL bulunamadı**
  hatasıyla durdu (`FindOpenSSL.cmake`). Kök neden: **NASM (Netwide
  Assembler) bu makinede kurulu değil** — OpenSSL'in Windows derlemesi
  assembly optimizasyonları için gerektiriyor (Perl kurulu, o sorun değil).
  **Sonraki adım:** NASM kur (`choco install nasm` veya
  nasm.us'tan indir, PATH'e ekle), `deps` klasörünü temizleyip
  `build_release_vs2022.bat` yeniden çalıştır. `vera-control` bu blokajdan
  bağımsız çalışıyor (resmi v2.4.2 binary'sine karşı test edildi).

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
