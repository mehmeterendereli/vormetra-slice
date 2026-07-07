# AGENTS.md — VORMETRA Slice

Bu depoda çalışan **tüm AI ajanları** için giriş noktası (Claude dışı araçlar dahil).

> **Asıl yönerge `CLAUDE.md`'dir — önce onu tam oku.** Bu dosya yalnızca
> vazgeçilmez kuralların özetidir.

## Vazgeçilmez kurallar

1. **AGPLv3:** fork yasal, ama dağıtımda kaynak açma yükümlülüğü var — ticari
   lansmandan önce §3 (hukuk) kararı gerekiyor. Detay: `CLAUDE.md`.
2. **İnce fork:** C++ çekirdeğini (`src/`, `deps/`, `cmake/`) gereksiz yere
   değiştirme — VORMETRA katmanı `resources/profiles/VORMETRA/` + `vera-control/`.
3. **Uydurma sayı yok:** G1000 verisi yoksa `TBD`, kaynağını belirt.
4. **Subagent sınırı:** aynı anda en fazla 3; küçük modellere "kendi
   alt-ajanını açma" talimatı ver.

## Kaynak

Ana bilgi tabanı: `github.com/mehmeterendereli/vormetra` (private,
`DECISIONS.md`/`CLAUDE.md`/`DIZIN_HARITASI.md`).
