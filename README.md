# VORMETRA Slice

VORMETRA G1000 granül beslemeli (FGF/pellet), büyük format endüstriyel 3D
yazıcı için dilimleyici. Proje, [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer)
üzerine kurulmuş ince bir AGPLv3 forkudur.

> **VORMETRA kodunu mu arıyorsunuz?** Doğrudan
> [G1000 profillerine](resources/profiles/VORMETRA/),
> [Vera kontrol katmanına](vera-control/) veya
> [fork rehberine](FORK_NOTES.md) gidin. Depodaki diğer dosyaların çoğu
> derlenebilir OrcaSlicer motorudur.

**Durum:** Aktif geliştirme. G1000 vendor profili gerçek CLI dilimleme
testinden geçti. Native GUI marka dönüşümü ve gerçek makine kalibrasyonu
devam ediyor; yayımlanmış bir VORMETRA Slice sürümü henüz yoktur.

## Depo haritası

| Alan | Ne içerir? | Bakım modeli |
| --- | --- | --- |
| [`resources/profiles/VORMETRA/`](resources/profiles/VORMETRA/) | G1000 makine, pellet malzeme ve proses profilleri | VORMETRA |
| [`vera-control/`](vera-control/) | HTTP API, MCP sunucusu ve Vera Console | VORMETRA |
| [`src/`](src/), [`deps/`](deps/), [`deps_src/`](deps_src/) | OrcaSlicer motoru ve derleme bağımlılıkları | Mümkün olduğunca upstream |
| [`resources/`](resources/) | UI varlıkları, çeviriler ve üretici profilleri | Büyük ölçüde upstream |
| [`tests/`](tests/) | C++ motor testleri | Büyük ölçüde upstream |
| [`README.upstream.md`](README.upstream.md) | Orijinal OrcaSlicer README'si | Upstream kopyası |

## Bu depo neden büyük?

Bu yalnızca bir profil deposu değil, çalıştırılabilir masaüstü uygulamasının tam
kaynak forkudur. C++ motoru, platform bağımlılıkları, testler, çeviriler, UI
varlıkları ve desteklenen yazıcı profilleri kaynak ağacında bulunmalıdır.
Derleme çıktıları, loglar ve Python cache dosyaları Git tarafından izlenmez.

Dosyaları görünürde sadeleştirmek için motor klasörlerini silmek derlemeyi
bozar ve OrcaSlicer güncellemelerini birleştirmeyi zorlaştırır. VORMETRA
değişiklik sınırları ve upstream politikası için [`FORK_NOTES.md`](FORK_NOTES.md)
dosyasına bakın.

## Küçük indirme seçenekleri

Yalnızca VORMETRA profilleri ve Vera üzerinde çalışacaksanız:

```bash
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/mehmeterendereli/vormetra-slice.git
cd vormetra-slice
git sparse-checkout set resources/profiles/VORMETRA vera-control
```

Tam uygulamayı yalnızca derlemek istiyorsanız geçmişi indirmeden sığ klon
kullanabilirsiniz:

```bash
git clone --depth 1 \
  https://github.com/mehmeterendereli/vormetra-slice.git
```

Upstream senkronizasyonu yapacak geliştiriciler tam geçmişi klonlamalıdır.

## Geliştirme

- Profil geliştirmeden önce
  [`resources/profiles/VORMETRA/README.md`](resources/profiles/VORMETRA/README.md)
  dosyasındaki doğrulanmış CLI kısıtlarını okuyun.
- Vera kontrol katmanı için [`vera-control/README.md`](vera-control/README.md)
  talimatlarını izleyin.
- Motoru kaynaktan derlemek için [`README.upstream.md`](README.upstream.md) ve
  platform build script'lerini kullanın.
- Katkı sınırları ve test beklentileri için
  [`CONTRIBUTING.md`](CONTRIBUTING.md) dosyasına bakın.

## Lisans

- Motor, profiller ve aksi belirtilmeyen repo içeriği:
  [GNU AGPLv3](LICENSE.txt).
- `vera-control/`: [MIT](vera-control/LICENSE).

OrcaSlicer kredi ve topluluk bağlantıları
[`README.upstream.md`](README.upstream.md) içinde korunur.
