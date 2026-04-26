# 🚀 URMISSZIO

> *Pygame alapú top-down űrkaland beépített arcade shoot'em up minijátékkal*

---

## 🎮 A játékról

Az **Urmisszio** egy 2D top-down kalandjáték, amelynek helyszíne egy elhagyatott űrállomás. Egy asztronautát irányítasz szobáról szobára — tárgyakat gyűjtesz, kombinálsz, ajtókat nyitsz ki, és megpróbálsz életben maradni.

Ha elegánsan unat a túlélés, ugorj át az **ARCADE módba** a főmenüből — és lőj le mindent ami mozog.

---

## ✨ Főbb funkciók

- 🗺️ **Tile-alapú szobárendszer** animált mozgással és mélységrendezéssel
- 🧪 **Tárgy- és receptrendszer** — kombinálj tárgyakat újak létrehozásához
- 👾 **Arcade shooter minijáték** — 4 ellenségtípus, hullámrendszer, pontszám
- 🎨 **CRT / glitch effektek** a főmenüben
- 🔊 **Többcsatornás hangrendszer** dedikált csatornákkal
- 🌌 **Parallax háttér** — ugyanaz a stílus a menüben és a játékban
- 🧑‍🚀 **AstronautV2 spritek** — külön animáció mind a 4 irányhoz + árnyékok

---

## 🕹️ Vezérlők

| Billentyű | Funkció |
|-----------|---------|
| `WASD` / Nyilak | Mozgás |
| `G` | Tárgy felvétele |
| `TAB` | Következő tárgy |
| `D` | Tárgy elejtése |
| `SPACE` | Vizsgálat / interakció |
| `U` | Tárgy használata |
| `ESC` | Kilépés |

**Shooter módban:** `WASD` mozgás, `SPACE` lövés, `ESC` vissza a menübe.

---

## ⚙️ Telepítés

**Követelmények:** Python 3.10+, Pygame 2.x

```bash
git clone https://github.com/Rodimark/urmisszio.git
cd urmisszio
pip install pygame
python main.py
```

---

## 📁 Struktúra

```
urmisszio/
├── main.py          # Belépési pont
├── mainmenu.py      # Főmenü + CRT effektek
├── shooter.py       # Arcade minijáték
├── player.py        # Játékos animációk
├── hud.py           # HUD, bárok, párbeszédablak
├── room.py          # Szobagenerátor
├── data.py          # Globális adatok és konstansok
├── inventory.py     # Tárgyrendszer
├── doors.py         # Ajtólogika
├── hazards.py       # Veszélyek
├── loadscreen.py    # Vezérlők képernyő
└── assets/          # Képek, hangok, zenék, betűtípusok
```

---

## 👨‍💻 Fejlesztő

**Rodenbucher Márk** — 2026
