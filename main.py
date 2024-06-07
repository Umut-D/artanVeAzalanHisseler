# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
import datetime
import locale
import requests
from bs4 import BeautifulSoup

locale.setlocale(locale.LC_ALL, 'TR-tr.UTF-8')
BUTUN_HISSELER = "https://www.getmidas.com/canli-borsa/en-cok-artan-hisseler"


def _web_sayfasini_indir() -> str:
    with requests.get(BUTUN_HISSELER, timeout=5) as web_sayfasi:
        if web_sayfasi.status_code != 200:
            raise requests.RequestException("Web sayfası indirilemedi! İnternetiniz var mı?")

    return web_sayfasi.text


def _verileri_duzenle() -> zip:
    beautiful_soup = BeautifulSoup(_web_sayfasini_indir(), "html.parser")
    tum_hisseler = beautiful_soup.select("a.title.stock-code")
    gunluk_degisim_orani = beautiful_soup.select("td.dailyChangePercent")

    return zip(tum_hisseler, gunluk_degisim_orani)


def _ondalikli_sayiya_donustur(oran: str) -> float:
    ondalikli_oran = oran.replace('%', '').replace(",", ".")
    try:
        return float(ondalikli_oran)
    except ValueError:
        return 0.0


def _verileri_sirala(veriler, oran) -> list:
    return sorted(veriler, key=lambda x: x["Oran"], reverse=oran >= 0)


def _verileri_indeksle(oran: float):
    veriler = []
    for hisse, degisim in _verileri_duzenle():
        degisim_orani = _ondalikli_sayiya_donustur(degisim.text.strip())
        if (0 < oran <= degisim_orani) or (0 > oran >= degisim_orani):
            sozluk = {"Hisse": hisse.text, "Oran": degisim_orani}
            veriler.append(sozluk)

    return _verileri_sirala(veriler, oran)


def _bugun():
    mevcut_gun = datetime.date.today()
    gun = mevcut_gun

    if mevcut_gun.weekday() == 5:
        gun = mevcut_gun - datetime.timedelta(days=1)
    elif mevcut_gun.weekday() == 6:
        gun = mevcut_gun - datetime.timedelta(days=2)

    return gun.strftime("%d.%m.%Y %A")


def hisseleri_yazdir(oran: float):
    bugun = _bugun()
    ek_bilgi = "Veriler 15 dakika gecikmelidir"

    if oran > 0:
        print(f"[{bugun}] En Çok Artan Hisseler (* {ek_bilgi})")
    else:
        print(f"[{bugun}] En Çok Düşen Hisseler (* {ek_bilgi})")

    for hisse in _verileri_indeksle(oran):
        print(f"{hisse['Hisse']}: %{hisse['Oran']}")


if __name__ == "__main__":
    hisseleri_yazdir(-5)
