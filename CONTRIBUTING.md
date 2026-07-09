# Katkı rehberi

Katkı göndermeden önce değişikliğin doğru projeye ait olduğunu belirleyin:

- G1000, pellet/FGF profilleri ve Vera: bu repo
- Genel OrcaSlicer motor hatası veya tüm yazıcıları ilgilendiren özellik:
  mümkünse [OrcaSlicer upstream](https://github.com/OrcaSlicer/OrcaSlicer)

## Temel kurallar

1. `CLAUDE.md` ve değiştirdiğiniz alanın README dosyasını okuyun.
2. Gizli bilgi, finans, fon, müşteri verisi, erişim anahtarı veya iç strateji
   eklemeyin. Bu repo herkese açıktır.
3. Kaynağı olmayan G1000 değeri uydurmayın. Bilinmiyorsa `TBD` bırakın ve
   gereken veri kaynağını yazın.
4. `src/`, `deps/`, `deps_src/` ve `cmake/` değişikliklerini zorunlu olan en
   küçük delta ile sınırlayın.
5. Mevcut `.3mf` projeleri ve yazıcı profilleri için geriye uyumluluğu koruyun.

## Test

Değiştirdiğiniz alan için en dar anlamlı testi çalıştırın:

- `vera-control/`: dizin içinden `python -m pytest`
- Profil: `resources/profiles/VORMETRA/README.md` içindeki doğrulama akışı
- C++ motoru: build dizininden `ctest --output-on-failure`

Gerçek motor gerektiren Vera testi `VERA_SLICER_BIN` tanımlı değilse otomatik
atlanır. PR açıklamasında çalıştırılan testleri ve atlanan kontrolleri açıkça
yazın.

## Pull request kapsamı

Tek PR'da mümkün olduğunca tek amaç taşıyın. Upstream senkronizasyonu,
VORMETRA özelliği ve mekanik format değişikliklerini ayrı tutun. Profil
değişikliklerinde değerin kaynağını veya kalibrasyon durumunu belirtin.

Katkılar, değiştirilen alana göre bu reponun mevcut lisansı altında sunulur:
motor ve profiller AGPLv3, `vera-control/` MIT.
