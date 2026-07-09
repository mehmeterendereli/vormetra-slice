# Fork rehberi

VORMETRA Slice, OrcaSlicer'ın tam kaynak kodunu taşıyan ince bir forkudur.
GitHub arayüzünde bir fork rozeti görünmese de upstream commit geçmişi
korunmuştur.

## Değişiklik sınırı

VORMETRA'ya özgü geliştirmelerin varsayılan yeri:

- `resources/profiles/VORMETRA/`
- `resources/profiles/VORMETRA.json`
- `vera-control/`
- `version.inc`
- VORMETRA'ya özgü root dokümantasyonu ve GitHub topluluk dosyaları

`src/`, `deps/`, `deps_src/` ve `cmake/` OrcaSlicer motorunun parçalarıdır.
Bir özellik bu alanlarda değişiklik gerektirmiyorsa çekirdeğe taşınmamalıdır.

## Neden upstream dosyalarını tutuyoruz?

Tam ağaç şu amaçlarla gereklidir:

- Windows, macOS ve Linux için yeniden üretilebilir kaynak derlemesi
- AGPLv3 kapsamında karşılık gelen kaynağın eksiksiz sunulması
- `.3mf`, profil ve G-code davranışının upstream ile uyumlu kalması
- OrcaSlicer güvenlik düzeltmeleri ve özelliklerinin düzenli alınabilmesi

Eski görünen bir klasör yalnızca dosya sayısını azaltmak amacıyla silinmez.
Budama ancak derleme, runtime paketleme ve üç platformdaki etkisi
doğrulandıktan sonra yapılır.

## Upstream senkronizasyonu

Yerel checkout'ta iki remote kullanılır:

```text
origin    https://github.com/mehmeterendereli/vormetra-slice.git
upstream  https://github.com/OrcaSlicer/OrcaSlicer.git
```

Senkronizasyon değişikliği ayrı bir branch ve PR'da yapılmalıdır. VORMETRA
değişiklikleriyle upstream güncellemesini aynı commit'e karıştırmayın. Çakışma
çözümünde önce profil ve proje formatı geriye uyumluluğunu, sonra üç platform
derlemesini doğrulayın.

Genel OrcaSlicer hataları ve motor iyileştirmeleri mümkünse önce upstream'e
bildirilir. VORMETRA profili, pellet davranışı veya `vera-control` sorunları bu
repoda ele alınır.

## Deponun boyutuyla çalışma

Kullanım amacına göre:

- Profil/Vera katkısı: sparse ve shallow clone
- Yalnızca build: shallow clone
- Upstream merge ve geçmiş analizi: tam clone

Komutlar root [`README.md`](README.md#küçük-indirme-seçenekleri) içinde
verilmiştir. Git geçmişini yeniden yazmak veya motor varlıklarını silmek,
ölçülebilir bir dağıtım gereksinimi olmadan uygulanmaz.
