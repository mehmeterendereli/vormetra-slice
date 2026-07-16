# VORMETRA vendor profile — kaynak notu

Bu profil OrcaSlicer'ın mevcut pellet altyapısı (PR #4836, `pellet_flow_coefficient`,
`pellet_modded_printer`) ve ana depodaki `Ginger Additive` vendor'ı (gerçek, üretimde
bir FGF/pellet makinesi, aynı 5.0mm nozül varyantına sahip) şablon alınarak
oluşturuldu. CLAUDE.md/WORKING_PROTOCOL "uydurma değer yok" kuralı gereği, hangi
alanın nereden geldiği burada açıkça ayrılıyor.

## Gerçek G1000 kaynaklı değerler (ana repo: `software/slicer/g1000-profile-spec.md`,
`TECHNICAL_REQUIREMENTS.md`, CAD_SYNC.md)
- `printable_area` / `printable_height`: 1000×1000×1000 mm (GEN-01 hedef)
- `nozzle_diameter`: 5.0 mm (spec §1)
- `max_layer_height` / `min_layer_height`: 3.75 / 1.5 mm (spec §4, 0.3–0.75×nozül)
- `line_width` başlangıcı: 6.0 mm, `layer_height` başlangıcı: 2.0 mm (spec §4)
- `machine_max_speed_x/y`: 333 mm/s, `machine_max_speed_z`: 145 mm/s (MOT-04, CAD FE V2R3)
- `machine_max_acceleration_x/y`: 2000 mm/s² (tasarım ivmesi 2.0 m/s², MOT-04)
- `filament_max_volumetric_speed` (PLA 1024, PETG 1015 mm³/s): spec §3 tablosu, 90 rpm
  ekstrüder tavanı. **Not:** bu bir tavan değeridir — mevcut (Faz-1, yükseltilmemiş)
  tahrikle sürdürülebilir debi daha düşük (~2.5–3 kg/h, bkz. ADR-016) — OQ-12
  (gearmotor tedarikçi seçimi) kapanana kadar sürekli baskıda bu tavana güvenilmemeli.
- `filament_density`: PLA 1.24, PETG 1.27 g/cm³ (spec §3 tablosu)
- PETG `hot_plate_temp: 0` (ısıtmasız): OQ-03 araştırma önerisi ("ısıtmalı tabla
  gerektirmiyor") — henüz kurucu onayı bekliyor, OQ-07 (ısıtmalı tabla/kabin gerekli mi)
  hâlâ genel olarak TBD.
- `multi_zone_number: 4`: CAD'deki "4 bölge bant ısıtıcı" (spec §5) — Ginger'ın kendi
  3 bölgeli tasarımından **kasıtlı olarak farklı**, bizim gerçek ekstrüder tasarımımıza
  uyarlandı.

## Ginger Additive'den (gerçek, üretimdeki referans pellet makine) alınan başlangıç
şablonu — G1000'de DOĞRULANMADI, ilk kalibrasyon noktası
- `retraction_length` 20mm / `retraction_speed` 200mm/s / `deretraction_speed` 200mm/s:
  Ginger'ın gerçek suck-back değerleri; ADR-011 (vida ters suck-back) davranışı için
  başlangıç noktası — G1000'de gerçek vida/nozül geometrisiyle kalibre edilmeli.
- PLA `hot_plate_temp: 50`: Ginger'ın gerçek pellet-PLA bed sıcaklığı; G1000 ısıtmalı
  tabla kararı (OQ-07) netleşene kadar geçici.

## CTL-01 (Klipper vs LinuxCNC) KAPANDI — profil LinuxCNC zincirine geçirildi (2026-07-16)

ADR-060 (2026-07-09) kontrol platformunu **LinuxCNC 2.9.4 + PCIe paralel-port I/O**
olarak kilitledi; harici CAD reposundaki post-processor sözleşmesi
(`dp-fgf-1000-v2-parametric\V2\slicer\fgf_post.py`, salt-okunur okundu) zinciri açıkça
**"STL -> PrusaSlicer/OrcaSlicer (Marlin lehçesi, E'li) -> fgf_post.py -> LinuxCNC
.ngc"** olarak tanımlıyor — Klipper değil. Bu profil o karardan sonra hâlâ Ginger'ın
Klipper şablonunu taşıyordu (`gcode_flavor: klipper` + `START_PRINT`/`PRINT_START`/
`END_PRINT`/`PRINT_END` makro çağrıları + `enable_pressure_advance` Klipper'a özgü
`SET_PRESSURE_ADVANCE` üretiyordu) — bu, gerçek bir zincir kırığıydı: `fgf_post.py`'nin
G-code kelime ayrıştırıcısı bu makro satırlarını (harf+rakam kalıbına uymadıkları için)
**sessizce düşürüyordu**, yani ön-ısıtma sıcaklığı .ngc çıktısına hiç taşınmıyordu.

**Düzeltme (bu oturum, uçtan uca gerçek CLI + fgf_post.py çalıştırılarak doğrulandı):**
- `gcode_flavor`: `klipper` → `marlin` (üç dosyada: `fdm_machine_common.json`,
  `VORMETRA_G1000_common.json`, `VORMETRA G1000 5.0 nozzle.json`).
- `machine_start_gcode`/`machine_end_gcode`: makro çağrıları yerine düz M104/M109/
  G92 E0 (Marlin, `fgf_post.py`'nin M68 E0 Q<sıcaklık> dönüşümünü tetikler).
- `machine_pause_gcode` (`fdm_machine_common.json`, Klipper `PAUSE` makrosu): boş
  string — LinuxCNC tarafı için pause sözleşmesi henüz tasarlanmadı, uydurma makro
  yazılmadı (TBD, kontrol tasarımı bekliyor).
- `enable_pressure_advance`: `1` → `0` (her iki filament profili) — Klipper'a özgü bir
  bead-genişliği ön-telafisi; `fgf_post.py`'nin docstring'i gereği koordineli U ekseni
  (joint 5) bunu zaten gereksiz kılıyor (LinuxCNC trajectory planner U'yu X/Y/Z ile
  otomatik senkronize eder) — `marlin` lehçesinde etkin bırakılsaydı `M900 K...`
  üretip yine sessizce düşürülecekti; kapatmak yanıltıcı/etkisiz bir komut üretmeyi
  engelliyor.
- **Doğrulama:** 200×200×100mm test küpü resmi CLI ile yeniden dilimlendi (50 katman,
  önceki 2026-07-07 doğrulamasıyla birebir), çıktıda Klipper makro izi **sıfır**,
  gerçek `M104 S245`/`M109 S245`/`M104 S0` satırları mevcut; bu G-code doğrudan
  `fgf_post.py`'den geçirildi — hatasız `.ngc` üretti (`M68 E0 Q245/Q240/Q0` +
  koordineli `U` hareketleri, zarf/yay/pozisyon fail-closed kontrollerinin hiçbiri
  tetiklenmedi). Kalıcı regresyon testleri:
  `vera-control/tests/test_slicer_bridge.py::test_slice_model_emits_marlin_gcode_not_klipper_macros`
  ve `::test_sliced_gcode_survives_fgf_post_linuxcnc_conversion` (ikincisi
  `VERA_FGF_POST_PATH`/harici CAD reposu bu makinede yoksa otomatik skip edilir).
- **Kapsam dışı kalan (ayrı, önceden bilinen TBD'ler):** 4-bölge bağımsız ısıtıcı
  kanalı (`multi_zone_1..4_*` hâlâ "TBD") — `fgf_post.py` şu an tek analog kanal
  (`M68 E0`) modelliyor, dört fiziksel bandı ayrı ayrı sürmüyor; bu Elektrik E1/OQ-05
  kapanışına bağlı, bu düzeltmenin kapsamında değildi.

## Genel malzeme literatürü (G1000'e özgü değil, ama uydurma da değil)
- PLA nozül sıcaklığı 180–220°C, PETG 230–250°C: yaygın commodity filament/pellet
  sıcaklık aralıkları (Ginger'ın kendi PLA profili de aynı PLA aralığını kullanıyor).

## Gerçek TBD — bilinçli olarak "TBD" string'i olarak bırakıldı (kalibrasyon öncesi
gerçek baskı denemesi gerektirir; sayı uydurmak yerine JSON'da görünür şekilde kırık
bırakıldı — makro bunu literal "TBD" olarak yayar, sessizce yanlış sayı kullanmaz)
- `pellet_flow_coefficient`: nötr taban değeri "1" bırakıldı (kalibre edilmemiş anlamına
  gelir) — gerçek değer spec §2'deki tartma yöntemiyle ölçülmeli.
- `extruder_rotation_volume`, `multi_zone_1..4_temperature/_initial_layer`: gerçek
  makine/vida kalibrasyonu ve 4-bölge termal profil testi bekliyor.

Detay ve tam kaynak: ana repo `software/slicer/g1000-profile-spec.md`,
`DECISIONS.md` ADR-011/014/043.

## Uçtan uca doğrulandı (2026-07-07, resmi v2.4.2 binary + CLI, gerçek test)

Bu profil resmi OrcaSlicer v2.4.2 taşınabilir (portable) sürümüyle, `--load-settings`/
`--load-filaments`/`--slice`/`--export-3mf` CLI yoluyla, 200×200×100mm test küpü
kullanılarak **gerçekten dilimlendi** (uydurma/varsayım değil, çalıştırılıp doğrulandı).
Çıkan G-code'da doğrulanan gerçek değerler: `filament_diameter: 1.12838` (pellet_flow_
coefficient=1'den doğru hesaplandı), `bed_shape: 0x0,1000x0,1000x1000,0x1000`, 50 katman
(100mm / 2.0mm), 6.00/6.50mm ekstrüzyon genişliği, `SET_PRESSURE_ADVANCE ADVANCE=0.3`,
`START_PRINT BED_TEMPERATURE=... EXTRUDER_TEMPERATURE=...` makro çağrısı.

**Bu süreçte bulunan ve düzeltilen gerçek CLI/profil hataları (gelecekte aynı
hataya düşmemek için not edildi — `vera-control/` katmanı da bunu hesaba katar):**
1. **Marlin G92-E0 kontrolü:** `gcode_flavor` "klipper" olmadan (varsayılan Marlin
   kabul ediliyor), OrcaSlicer relative-extruder G-code için `before_layer_change_gcode`
   içinde tam "G92 E0" ister. Artık hem common hem leaf dosyada var.
2. **🔴 En önemli bulgu — CLI `--load-settings` doğrudan dosya yolu ile inherits
   zincirini güvenilir şekilde çözmüyor:** `VORMETRA_G1000_common.json`'da tanımlı
   `printable_area`/`gcode_flavor`/`machine_start_gcode`/`pellet_modded_printer` gibi
   alanlar, yalnızca CLI'ye verilen (leaf, `instantiation:true`) dosyada YOKSA sessizce
   devreye girmiyor — bunun yerine bina 1000×1000×1000 yerine **nesnenin bounding
   box'unu** "bed" sanıyor (arrange sıfır marjla başarısız oluyor, sessiz hata).
   **Çözüm:** kritik alanlar hem common hem leaf dosyada AÇIKÇA tekrarlanıyor (gerçek
   Voron vendor'ının da yaptığı gibi — leaf dosyalar `printable_area`'yı tekrar
   tanımlıyor). GUI/PresetBundle modunda inherits muhtemelen düzgün çözülüyor; bu
   sadece CLI doğrudan-dosya-yükleme yoluna özgü bir davranış/kısıt.
3. **`pellet_flow_coefficient` otomatik `filament_diameter` dönüşümü CLI'de
   çalışmıyor** (GUI `Tab.cpp` olay işleyicisine bağlı görünüyor) — `filament_diameter`
   artık formülle (√(4×coef/π)) elle hesaplanıp doğrudan yazılıyor (coef=1 → 1.12838).
4. **Ginger'ın `{extruder_rotation_volume[0]}`/`{multi_zone_N_temperature[0]}` gibi
   makro parametreleri vanilla OrcaSlicer'da tanımlı değil** (placeholder parser
   "Not a variable name" hatası veriyor) — Ginger'ın gerçek dağıtımında ek bir özel
   seçenek kaydı olmalı (public repoda yok). `machine_start_gcode` bu yüzden şimdilik
   yalnızca standart, tanınan placeholder'ları kullanacak şekilde **sadeleştirildi**
   (`[bed_temperature_initial_layer]`, `[nozzle_temperature_initial_layer]`).
   4-bölge/vida-hacmi parametreli tam makro burada da eklenmedi — ama artık nedeni
   "Klipper `printer.cfg` netleşmedi" değil (CTL-01 KAPANDI, aşağıdaki bölüm): gerçek
   engel `fgf_post.py`'nin şu an yalnızca TEK analog ısıtıcı kanalı (`M68 E0`)
   modellemesi, 4 bağımsız bandı henüz ayrı sürmemesi (Elektrik E1/OQ-05'e bağlı TBD).

> **Not (2026-07-16):** Bu bölümdeki `SET_PRESSURE_ADVANCE`/`START_PRINT` örnek
> çıktısı 2026-07-07 tarihli, henüz `gcode_flavor: klipper` iken alınmış tarihsel bir
> kayıttır — güncel profil artık bunları üretmez, bkz. yukarıdaki "CTL-01 KAPANDI" bölümü.
5. **Kopyalanmış ağ adresi:** Ginger taban profilindeki `http://10.0.1.200/`
   VORMETRA'ya ait doğrulanmış bir endpoint değildi. GUI bunu gerçek yerel cihaz
   sanıp `Unsupported printer type: VORMETRA G1000` hatası üretiyordu. `print_host`
   artık boştur; makine kontrol endpoint'i firmware/protokol kararıyla birlikte
   doğrulanana kadar profile adres yazılmayacaktır.
6. **Geçersiz tabla dışlama alanı:** Tek noktadan oluşan `bed_exclude_area: ["0x0"]`
   GUI'de `Unable to create exclude triangles` hatasına yol açıyordu. G1000 için
   doğrulanmış bir dışlama poligonu olmadığından alan boş diziye çevrildi.
7. **Headless thumbnail:** CLI, OpenGL bağlamı yokken 3MF ilişkilerine thumbnail
   yollarını yazıyor fakat PNG dosyalarını üretemiyor. `vera-control` eksik
   `plate_1.png` ve `plate_1_small.png` hedeflerini geçerli nötr PNG'lerle
   tamamlayarak GUI Preview arşivini tutarlı hale getiriyor.

**Doğrulanmamış kalan:** `hot_plate_temp` (PETG için 0 istendi, çıkan G-code'da 35
görüldü — alan adı eşleşmesi teyit edilmeli, düşük öncelik, sonraki geçişte bakılacak).
