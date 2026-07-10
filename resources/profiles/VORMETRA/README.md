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
- `machine_start_gcode`/`machine_end_gcode` (`START_PRINT`/`END_PRINT` makro çağrısı):
  Ginger'ın da kullandığı Klipper makro deseni — makro **gövdeleri** firmware
  (`printer.cfg`) tarafında yazılmalı, bu profilde yok (Ginger'ınki de public repoda
  yok — bu normal/beklenen bir ayrım). CTL-01 (Klipper vs LinuxCNC) netleşmeden
  kesinleşmez.
- PLA `hot_plate_temp: 50`: Ginger'ın gerçek pellet-PLA bed sıcaklığı; G1000 ısıtmalı
  tabla kararı (OQ-07) netleşene kadar geçici.

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
   4-bölge/vida-hacmi parametreli tam makro, Klipper `printer.cfg` tarafı netleşince
   ve/veya özel seçenek kaydı mekanizması bulununca eklenecek (CTL-01 bağımlı).
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
