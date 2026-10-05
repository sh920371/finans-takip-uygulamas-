
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
#import pyqtgraph as pg
import yfinance as yf
import pandas as pd

from PySide6.QtWidgets import (QTableWidgetItem,QHeaderView,QAbstractItemView,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QTextBrowser,QPushButton)

from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QColor


# ============================================================
# MATPLOTLIB
# ============================================================

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True

except ImportError:
    MATPLOTLIB_AVAILABLE = False


# ============================================================
# GENEL AYARLAR
# ============================================================

CACHE_SURESI = 60 * 5          # 5 dakika
DOWNLOAD_PERIOD = "5d"

# Veri çekilirken aynı anda en fazla bu kadar grup çalışır.
MAX_WORKERS = 4


# ============================================================
# BELLEK CACHE
# ============================================================

_DATA_CACHE = {}
_CACHE_LOCK = threading.Lock()


def cache_get(key):
    """
    Cache'deki veriyi getirir.
    Süresi geçmişse None döndürür.
    """

    with _CACHE_LOCK:

        if key not in _DATA_CACHE:
            return None

        timestamp, data = _DATA_CACHE[key]

        if time.time() - timestamp > CACHE_SURESI:
            del _DATA_CACHE[key]
            return None

        return data


def cache_set(key, data):
    """
    Veriyi bellekte cache'ler.
    """

    with _CACHE_LOCK:
        _DATA_CACHE[key] = (time.time(), data)


# ============================================================
# SEMBOL BİLGİLERİ
# ============================================================

SYMBOL_INFO = {}


def register_symbols(symbols, market, region):
    """
    Sembolleri arama/filtreleme için kayıt altına alır.
    """

    for symbol, name in symbols:

        SYMBOL_INFO[symbol.upper()] = {
            "name": name,
            "market": market,
            "region": region
        }


# ============================================================
# TÜRKİYE
# ============================================================

BIST_HISSELERI = [("THYAO.IS", "Türk Hava Yolları"),("GARAN.IS", "Garanti BBVA"),("EREGL.IS", "Ereğli Demir Çelik"),("AKBNK.IS", "Akbank"),("ISCTR.IS", "İş Bankası C"),("KCHOL.IS", "Koç Holding"),("SAHOL.IS", "Sabancı Holding"),("BIMAS.IS", "BİM Mağazalar"),("TUPRS.IS", "Tüpraş"),("ASELS.IS", "Aselsan"),("PETKM.IS", "Petkim"),("SISE.IS", "Şişecam"),("YKBNK.IS", "Yapı Kredi"),("ARCLK.IS", "Arçelik"),("TOASO.IS", "Tofaş"),("FROTO.IS", "Ford Otosan"),("PGSUS.IS", "Pegasus"),("HEKTS.IS", "Hektaş"),("SASA.IS", "Sasa Polyester"),("ENKAI.IS", "Enka İnşaat"), ("TCELL.IS", "Turkcell"),("TTKOM.IS", "Türk Telekom"),("KRDMD.IS", "Kardemir D"),("KOZAL.IS", "Koza Altın"),("ASTOR.IS", "Astor Enerji"),("EKGYO.IS", "Emlak Konut GYO"),("HALKB.IS", "Halkbank"),("VAKBN.IS", "Vakıfbank"),("MGROS.IS", "Migros"),("AKSEN.IS", "Aksa Enerji"),("ODAS.IS", "Odaş Elektrik"),("GUBRF.IS", "Gübre Fabrikaları"),("KOZAA.IS", "Koza Anadolu"),("IPEKE.IS", "İpek Doğal Enerji"),("BERA.IS", "Bera Holding"),("OYAKC.IS", "Oyak Çimento"),("ZOREN.IS", "Zorlu Enerji"),("GESAN.IS", "Girişim Elektrik"),("CWENE.IS", "CW Enerji"),("EUPWR.IS", "Europower Enerji"),("KONTR.IS", "Kontrolmatik"),("ALFAS.IS", "Alfa Solar"),("CANTE.IS", "Çan2 Termik"),("ENERY.IS", "Enerya Enerji"),("KBORU.IS", "Kuzuoğlu Boru"),("MEGMT.IS", "Mega Metal"),("OBAMS.IS", "Oba Makarnacılık"),("AGROT.IS", "Agrotech"),("BRYAT.IS", "Borusan Yatırım"),("CMBTN.IS", "Çimbeton"),("SMRTG.IS", "Smart Güneş"),("ALKLC.IS", "Alkim Kağıt"),("GENIL.IS", "Gen İlaç"),("BIOEN.IS", "Biotrend"),("YEOTK.IS", "Yeo Teknoloji"),("MIATK.IS", "Mia Teknoloji"),("LMKDC.IS", "Limak Doğu Anadolu"),("AGHOL.IS", "Anadolu Grubu Holding"),("TSKB.IS", "TSKB"),("SKBNK.IS", "Şekerbank"),("ENJSA.IS", "Enerjisa"),("MPARK.IS", "Medical Park"),("QUAGR.IS", "Qua Granite"),("SDTTR.IS", "SDT Uzay"),("GRTRK.IS", "Graıntürk"),("KCAER.IS", "Kocaer Çelik"),("PCILT.IS", "PC İletişim"),("ULUUN.IS", "Ulusoy Un"),("CLEBI.IS", "Çelebi"),("ALARK.IS", "Alarko Holding"),("ANSGR.IS", "Anadolu Sigorta"),("AKGRT.IS", "Aksigorta"),("BAGFS.IS", "Bagfaş"),("BRISA.IS", "Brisa"),("CCOLA.IS", "Coca-Cola İçecek"),("CEMTS.IS", "Çemtaş"),("CIMSA.IS", "Çimsa"),("DEVA.IS", "Deva Holding"),("EGEEN.IS", "Ege Endüstri"),("EGEPO.IS", "Nasmed"),("GEREL.IS", "Gersan Elektrik"),("GSDHO.IS", "GSD Holding"),("GWIND.IS", "Galata Wind"),("HATSG.IS", "Hat-San"),("IHLAS.IS", "İhlas Holding"),("INFO.IS", "İnfo Yatırım"),("INVES.IS", "Investco Holding"),("ISGYO.IS", "İş GYO"),("JANTS.IS", "Jantsa"),("KAYSE.IS", "Kayseri Şeker"),("KMPUR.IS", "Kimteks Poliüretan"),("KONYA.IS", "Konya Çimento"),("KUTPO.IS", "Kütahya Porselen"), ("LOGO.IS", "Logo Yazılım"),("MAVI.IS", "Mavi Giyim"),("OYAKC.IS", "Oyak Çimento"),("PENTA.IS", "Penta Teknoloji"),("REEDR.IS", "Reeder Teknoloji"),("SOKM.IS", "Şok Marketler"),("TABGD.IS", "Tab Gıda"),("TAVHL.IS", "TAV Havalimanları"),("TKFEN.IS", "Tekfen Holding"),("TRGYO.IS", "Torunlar GYO"),("ULKER.IS", "Ülker Bisküvi"),("VESBE.IS", "Vestel Beyaz"),("VESTL.IS", "Vestel"),("YATAS.IS", "Yataş"),("YEOTK.IS", "Yeo Teknoloji"),("ZRGYO.IS", "Ziraat GYO"),
]

register_symbols(
    BIST_HISSELERI,
    "BIST",
    "Türkiye"
)


# ============================================================
# ABD - TEKNOLOJİ / NASDAQ
# ============================================================

ABD_TECH = [

    ("AAPL", "Apple"),
    ("MSFT", "Microsoft"),
    ("NVDA", "NVIDIA"),
    ("GOOGL", "Alphabet"),
    ("GOOG", "Alphabet Class C"),
    ("AMZN", "Amazon"),
    ("META", "Meta Platforms"),
    ("TSLA", "Tesla"),
    ("AVGO", "Broadcom"),
    ("NFLX", "Netflix"),
    ("AMD", "AMD"),
    ("QCOM", "Qualcomm"),
    ("CSCO", "Cisco"),
    ("INTC", "Intel"),
    ("TXN", "Texas Instruments"),
    ("AMAT", "Applied Materials"),
    ("MU", "Micron"),
    ("LRCX", "Lam Research"),
    ("KLAC", "KLA Corporation"),
    ("ADI", "Analog Devices"),
    ("MRVL", "Marvell"),
    ("ARM", "Arm Holdings"),
    ("ANET", "Arista Networks"),
    ("PANW", "Palo Alto Networks"),
    ("CRWD", "CrowdStrike"),
    ("SNPS", "Synopsys"),
    ("CDNS", "Cadence Design"),
    ("ADBE", "Adobe"),
    ("CRM", "Salesforce"),
    ("ORCL", "Oracle"),
    ("NOW", "ServiceNow"),
    ("INTU", "Intuit"),
    ("ADP", "ADP"),
    ("PYPL", "PayPal"),
    ("PLTR", "Palantir"),
    ("APP", "AppLovin"),
    ("DDOG", "Datadog"),
    ("ZS", "Zscaler"),
    ("NET", "Cloudflare"),
    ("TEAM", "Atlassian"),
    ("WDAY", "Workday"),
    ("SNOW", "Snowflake"),
    ("MDB", "MongoDB"),
    ("SHOP", "Shopify"),
    ("MELI", "MercadoLibre"),
    ("DASH", "DoorDash"),
    ("ABNB", "Airbnb"),
    ("UBER", "Uber"),
    ("COIN", "Coinbase"),
    ("HOOD", "Robinhood"),
    ("RIVN", "Rivian"),
    ("LCID", "Lucid"),
    ("ROKU", "Roku"),
    ("EA", "Electronic Arts"),
    ("TTD", "The Trade Desk"),
    ("MCHP", "Microchip Technology"),
    ("ON", "ON Semiconductor"),
    ("NXPI", "NXP Semiconductors"),
    ("MRNA", "Moderna"),
    ("GILD", "Gilead Sciences"),
    ("VRTX", "Vertex Pharmaceuticals"),
    ("REGN", "Regeneron"),
    ("ISRG", "Intuitive Surgical"),
    ("DXCM", "DexCom"),
    ("IDXX", "IDEXX"),
]

register_symbols(
    ABD_TECH,
    "NASDAQ / ABD",
    "ABD"
)


# ============================================================
# ABD - S&P 500 / BÜYÜK ŞİRKETLER
# ============================================================

ABD_BLUE_CHIP = [

    ("JPM", "JPMorgan Chase"),
    ("BAC", "Bank of America"),
    ("WFC", "Wells Fargo"),
    ("C", "Citigroup"),
    ("GS", "Goldman Sachs"),
    ("MS", "Morgan Stanley"),
    ("V", "Visa"),
    ("MA", "Mastercard"),
    ("AXP", "American Express"),

    ("JNJ", "Johnson & Johnson"),
    ("LLY", "Eli Lilly"),
    ("PFE", "Pfizer"),
    ("MRK", "Merck"),
    ("ABBV", "AbbVie"),
    ("ABT", "Abbott"),
    ("UNH", "UnitedHealth"),
    ("TMO", "Thermo Fisher"),
    ("MDT", "Medtronic"),

    ("WMT", "Walmart"),
    ("COST", "Costco"),
    ("HD", "Home Depot"),
    ("LOW", "Lowe's"),
    ("MCD", "McDonald's"),
    ("NKE", "Nike"),
    ("SBUX", "Starbucks"),
    ("KO", "Coca-Cola"),
    ("PEP", "PepsiCo"),
    ("PG", "Procter & Gamble"),

    ("XOM", "Exxon Mobil"),
    ("CVX", "Chevron"),
    ("COP", "ConocoPhillips"),
    ("SLB", "Schlumberger"),
    ("CAT", "Caterpillar"),
    ("DE", "Deere"),
    ("GE", "GE Aerospace"),
    ("HON", "Honeywell"),
    ("RTX", "RTX"),
    ("LMT", "Lockheed Martin"),
    ("UPS", "UPS"),
    ("UNP", "Union Pacific"),

    ("DIS", "Walt Disney"),
    ("CMCSA", "Comcast"),
    ("T", "AT&T"),
    ("VZ", "Verizon"),
    ("TMUS", "T-Mobile"),

    ("IBM", "IBM"),
    ("ACN", "Accenture"),
    ("LIN", "Linde"),
    ("SPGI", "S&P Global"),
    ("BLK", "BlackRock"),
    ("SCHW", "Charles Schwab"),
]

register_symbols(
    ABD_BLUE_CHIP,
    "S&P 500 / ABD",
    "ABD"
)


# ============================================================
# ALMANYA - DAX
# ============================================================

DAX_HISSELERI = [

    ("SAP.DE", "SAP"),
    ("SIE.DE", "Siemens"),
    ("AIR.DE", "Airbus"),
    ("ALV.DE", "Allianz"),
    ("DTE.DE", "Deutsche Telekom"),
    ("MBG.DE", "Mercedes-Benz"),
    ("BMW.DE", "BMW"),
    ("BAS.DE", "BASF"),
    ("MUV2.DE", "Munich Re"),
    ("DB1.DE", "Deutsche Börse"),
    ("VOW3.DE", "Volkswagen"),
    ("MRK.DE", "Merck KGaA"),
    ("DHL.DE", "DHL Group"),
    ("ENR.DE", "Siemens Energy"),
    ("BEI.DE", "Beiersdorf"),
    ("HEI.DE", "Heidelberg Materials"),
    ("SY1.DE", "Symrise"),
    ("RWE.DE", "RWE"),
    ("EOAN.DE", "E.ON"),
    ("CON.DE", "Continental"),
    ("ADS.DE", "Adidas"),
    ("ZAL.DE", "Zalando"),
    ("SHL.DE", "Siemens Healthineers"),
    ("VNA.DE", "Vonovia"),
    ("IFX.DE", "Infineon"),
    ("DBK.DE", "Deutsche Bank"),
    ("HEN3.DE", "Henkel"),
    ("RHM.DE", "Rheinmetall"),
    ("FRE.DE", "Fresenius"),
    ("HNR1.DE", "Hannover Rück"),
    ("MTX.DE", "MTU Aero Engines"),
    ("FME.DE", "Fresenius Medical Care"),
    ("BAYN.DE", "Bayer"),
    ("1COV.DE", "Covestro"),
    ("PAH3.DE", "Porsche Automobil"),
]

register_symbols(
    DAX_HISSELERI,
    "DAX",
    "Almanya"
)


# ============================================================
# İNGİLTERE - FTSE
# ============================================================

FTSE_HISSELERI = [

    ("SHEL.L", "Shell"),
    ("AZN.L", "AstraZeneca"),
    ("HSBA.L", "HSBC"),
    ("ULVR.L", "Unilever"),
    ("BP.L", "BP"),
    ("GSK.L", "GSK"),
    ("RIO.L", "Rio Tinto"),
    ("REL.L", "RELX"),
    ("LSEG.L", "London Stock Exchange Group"),
    ("VOD.L", "Vodafone"),
    ("BARC.L", "Barclays"),
    ("LLOY.L", "Lloyds Banking"),
    ("NWG.L", "NatWest"),
    ("TSCO.L", "Tesco"),
    ("DGE.L", "Diageo"),
    ("PRU.L", "Prudential"),
    ("AAL.L", "Anglo American"),
    ("BATS.L", "British American Tobacco"),
    ("BA.L", "BAE Systems"),
    ("IAG.L", "International Airlines Group"),
    ("RR.L", "Rolls-Royce"),
    ("LGEN.L", "Legal & General"),
    ("HL.L", "Hargreaves Lansdown"),
    ("IMB.L", "Imperial Brands"),
    ("NXT.L", "Next"),
    ("MKS.L", "Marks & Spencer"),
    ("JD.L", "JD Sports"),
    ("AV.L", "Aviva"),
    ("NG.L", "National Grid"),
    ("SSE.L", "SSE"),
    ("STAN.L", "Standard Chartered"),
    ("CRH.L", "CRH"),
    ("EXPN.L", "Experian"),
    ("HLMA.L", "Halma"),
    ("IHG.L", "InterContinental Hotels"),
    ("FLTR.L", "Flutter Entertainment"),
]

register_symbols(
    FTSE_HISSELERI,
    "FTSE / İngiltere",
    "İngiltere"
)


# ============================================================
# FRANSA - CAC
# ============================================================

CAC_HISSELERI = [

    ("MC.PA", "LVMH"),
    ("OR.PA", "L'Oréal"),
    ("TTE.PA", "TotalEnergies"),
    ("SAN.PA", "Sanofi"),
    ("AIR.PA", "Airbus"),
    ("SU.PA", "Schneider Electric"),
    ("BNP.PA", "BNP Paribas"),
    ("KER.PA", "Kering"),
    ("EL.PA", "EssilorLuxottica"),
    ("SGO.PA", "Saint-Gobain"),
    ("VIE.PA", "Veolia"),
    ("DG.PA", "Vinci"),
    ("CS.PA", "AXA"),
    ("EN.PA", "Bouygues"),
    ("CA.PA", "Carrefour"),
    ("ML.PA", "Michelin"),
    ("STLA.PA", "Stellantis"),
    ("ORA.PA", "Orange"),
    ("RI.PA", "Pernod Ricard"),
    ("PUB.PA", "Publicis"),
    ("AI.PA", "Air Liquide"),
    ("BN.PA", "Danone"),
    ("ENGI.PA", "Engie"),
    ("RNO.PA", "Renault"),
    ("STM.PA", "STMicroelectronics"),
    ("URW.PA", "Unibail-Rodamco-Westfield"),
    ("VIV.PA", "Vivendi"),
    ("EDEN.PA", "Edenred"),
]

register_symbols(
    CAC_HISSELERI,
    "CAC 40 / Fransa",
    "Fransa"
)


# ============================================================
# JAPONYA
# ============================================================

JAPONYA_HISSELERI = [

    ("7203.T", "Toyota"),
    ("6758.T", "Sony"),
    ("9984.T", "SoftBank Group"),
    ("6861.T", "Keyence"),
    ("9432.T", "Nippon Telegraph & Telephone"),
    ("8306.T", "Mitsubishi UFJ"),
    ("6501.T", "Hitachi"),
    ("6902.T", "Denso"),
    ("7974.T", "Nintendo"),
    ("4502.T", "Takeda"),
    ("6098.T", "Recruit Holdings"),
    ("8035.T", "Tokyo Electron"),
    ("4063.T", "Shin-Etsu Chemical"),
    ("6301.T", "Komatsu"),
    ("8766.T", "Tokio Marine"),
    ("9433.T", "KDDI"),
    ("2914.T", "Japan Tobacco"),
    ("4543.T", "Terumo"),
    ("6981.T", "Murata Manufacturing"),
    ("8316.T", "Sumitomo Mitsui"),
    ("7267.T", "Honda"),
    ("7269.T", "Suzuki"),
    ("7751.T", "Canon"),
    ("3382.T", "Seven & i"),
    ("8802.T", "Mitsubishi Estate"),
    ("1925.T", "Daiwa House"),
    ("6594.T", "Nidec"),
    ("4519.T", "Chugai Pharmaceutical"),
    ("6146.T", "Disco"),
]

register_symbols(
    JAPONYA_HISSELERI,
    "Nikkei / Japonya",
    "Japonya"
)


# ============================================================
# HONG KONG
# ============================================================

HONG_KONG_HISSELERI = [

    ("0700.HK", "Tencent"),
    ("9988.HK", "Alibaba"),
    ("3690.HK", "Meituan"),
    ("1299.HK", "AIA Group"),
    ("0939.HK", "China Construction Bank"),
    ("0941.HK", "China Mobile"),
    ("2318.HK", "Ping An Insurance"),
    ("0005.HK", "HSBC"),
    ("1398.HK", "ICBC"),
    ("0388.HK", "Hong Kong Exchanges"),
    ("2020.HK", "ANTA Sports"),
    ("1044.HK", "Hengan International"),
    ("0823.HK", "Link REIT"),
    ("2382.HK", "Sunny Optical"),
    ("0011.HK", "Hang Seng Bank"),
    ("0016.HK", "Sun Hung Kai"),
    ("0027.HK", "Galaxy Entertainment"),
    ("0066.HK", "MTR Corporation"),
    ("0175.HK", "Geely Automobile"),
    ("0267.HK", "CITIC"),
    ("0960.HK", "Longfor Group"),
    ("1109.HK", "China Resources Land"),
    ("1928.HK", "Sands China"),
    ("2319.HK", "Mengniu Dairy"),
]

register_symbols(
    HONG_KONG_HISSELERI,
    "Hang Seng / Hong Kong",
    "Hong Kong"
)


# ============================================================
# ÇİN
# ============================================================

CIN_HISSELERI = [

    ("BABA", "Alibaba ADR"),
    ("JD", "JD.com"),
    ("PDD", "PDD Holdings"),
    ("BIDU", "Baidu"),
    ("NIO", "NIO"),
    ("XPEV", "XPeng"),
    ("LI", "Li Auto"),
    ("BEKE", "KE Holdings"),
    ("TME", "Tencent Music"),
    ("NTES", "NetEase"),
    ("ZTO", "ZTO Express"),
    ("EDU", "New Oriental"),
]

register_symbols(
    CIN_HISSELERI,
    "Çin",
    "Çin"
)


# ============================================================
# HİNDİSTAN
# ============================================================

HINDISTAN_HISSELERI = [

    ("RELIANCE.NS", "Reliance Industries"),
    ("TCS.NS", "Tata Consultancy Services"),
    ("HDFCBANK.NS", "HDFC Bank"),
    ("INFY.NS", "Infosys"),
    ("ICICIBANK.NS", "ICICI Bank"),
    ("HINDUNILVR.NS", "Hindustan Unilever"),
    ("ITC.NS", "ITC"),
    ("SBIN.NS", "State Bank of India"),
    ("BHARTIARTL.NS", "Bharti Airtel"),
    ("LT.NS", "Larsen & Toubro"),
    ("AXISBANK.NS", "Axis Bank"),
    ("KOTAKBANK.NS", "Kotak Mahindra Bank"),
    ("MARUTI.NS", "Maruti Suzuki"),
    ("SUNPHARMA.NS", "Sun Pharma"),
    ("TATAMOTORS.NS", "Tata Motors"),
]

register_symbols(
    HINDISTAN_HISSELERI,
    "Hindistan",
    "Hindistan"
)


# ============================================================
# GÜNEY KORE
# ============================================================

KORE_HISSELERI = [

    ("005930.KS", "Samsung Electronics"),
    ("000660.KS", "SK Hynix"),
    ("005380.KS", "Hyundai Motor"),
    ("035420.KS", "NAVER"),
    ("035720.KS", "Kakao"),
    ("051910.KS", "LG Chem"),
    ("006400.KS", "Samsung SDI"),
    ("207940.KS", "Samsung Biologics"),
    ("000270.KS", "Kia"),
    ("028260.KS", "Samsung C&T"),
]

register_symbols(
    KORE_HISSELERI,
    "KOSPI / Güney Kore",
    "Güney Kore"
)


# ============================================================
# KANADA
# ============================================================

KANADA_HISSELERI = [

    ("RY.TO", "Royal Bank of Canada"),
    ("TD.TO", "Toronto-Dominion Bank"),
    ("BMO.TO", "Bank of Montreal"),
    ("BNS.TO", "Bank of Nova Scotia"),
    ("SHOP.TO", "Shopify"),
    ("ENB.TO", "Enbridge"),
    ("CNQ.TO", "Canadian Natural Resources"),
    ("SU.TO", "Suncor Energy"),
    ("CNR.TO", "Canadian National Railway"),
    ("CP.TO", "Canadian Pacific Kansas City"),
]

register_symbols(
    KANADA_HISSELERI,
    "TSX / Kanada",
    "Kanada"
)


# ============================================================
# AVUSTRALYA
# ============================================================

AVUSTRALYA_HISSELERI = [

    ("BHP.AX", "BHP Group"),
    ("CBA.AX", "Commonwealth Bank"),
    ("CSL.AX", "CSL"),
    ("NAB.AX", "National Australia Bank"),
    ("WBC.AX", "Westpac"),
    ("ANZ.AX", "ANZ Group"),
    ("WDS.AX", "Woodside Energy"),
    ("RIO.AX", "Rio Tinto"),
    ("MQG.AX", "Macquarie Group"),
    ("FMG.AX", "Fortescue"),
]

register_symbols(
    AVUSTRALYA_HISSELERI,
    "ASX / Avustralya",
    "Avustralya"
)


# ============================================================
# TÜM HİSSELER
# ============================================================

TUM_HISSELER = []

for grup in [
    BIST_HISSELERI,
    ABD_TECH,
    ABD_BLUE_CHIP,
    DAX_HISSELERI,
    FTSE_HISSELERI,
    CAC_HISSELERI,
    JAPONYA_HISSELERI,
    HONG_KONG_HISSELERI,
    CIN_HISSELERI,
    HINDISTAN_HISSELERI,
    KORE_HISSELERI,
    KANADA_HISSELERI,
    AVUSTRALYA_HISSELERI
]:

    for item in grup:

        if item[0] not in [x[0] for x in TUM_HISSELER]:
            TUM_HISSELER.append(item)


# ============================================================
# DÜNYA ENDEKSLERİ
# ============================================================

ENDEKSLER = {

    # Türkiye
    "BIST 100": "^XU100.IS",
    "BIST 30": "^XU030.IS",

    # ABD
    "S&P 500": "^GSPC",
    "Nasdaq Composite": "^IXIC",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",

    # Almanya
    "DAX 40": "^GDAXI",
    "MDAX": "^MDAXI",

    # İngiltere
    "FTSE 100": "^FTSE",

    # Fransa
    "CAC 40": "^FCHI",

    # Avrupa
    "Euro Stoxx 50": "^STOXX50E",

    # İspanya
    "IBEX 35": "^IBEX",

    # İtalya
    "FTSE MIB": "FTSEMIB.MI",

    # Hollanda
    "AEX": "^AEX",

    # İsviçre
    "SMI": "^SSMI",

    # Japonya
    "Nikkei 225": "^N225",
    "TOPIX": "^TOPX",

    # Hong Kong
    "Hang Seng": "^HSI",

    # Çin
    "Shanghai Composite": "000001.SS",
    "Shenzhen Component": "399001.SZ",

    # Güney Kore
    "KOSPI": "^KS11",

    # Hindistan
    "Nifty 50": "^NSEI",
    "Sensex": "^BSESN",

    # Tayvan
    "Taiwan Weighted": "^TWII",

    # Kanada
    "S&P/TSX Composite": "^GSPTSE",

    # Avustralya
    "ASX 200": "^AXJO",

    # Brezilya
    "Bovespa": "^BVSP",

    # Meksika
    "IPC Mexico": "^MXX",

    # Güney Afrika
    "JSE All Share": "^JALSH",

    # Rusya
    "MOEX Russia": "IMOEX.ME",
}


# ============================================================
# DÜNYA TAHVİLLERİ / GETİRİ GÖSTERGELERİ
# ============================================================

TAHVILLER = {

    # ABD
    "ABD 1 Ay": "^IRX",
    "ABD 3 Ay": "^IRX",
    "ABD 2 Yıl": "^UST2YR",
    "ABD 5 Yıl": "^FVX",
    "ABD 10 Yıl": "^TNX",
    "ABD 30 Yıl": "^TYX",

    # Almanya
    "Almanya 10 Yıl": "TMBMKDE-10Y",
    "Almanya 2 Yıl": "TMBMKDE-02Y",

    # İngiltere
    "İngiltere 10 Yıl": "TMBMKGB-10Y",

    # Japonya
    "Japonya 10 Yıl": "^TNX",

    # Avrupa
    "İtalya 10 Yıl": "TMBMKIT-10Y",
    "Fransa 10 Yıl": "TMBMKFR-10Y",
}


# ============================================================
# GENEL VARLIK HARİTASI
# ============================================================

ALL_SYMBOLS = {}

for symbol, name in TUM_HISSELER:
    ALL_SYMBOLS[symbol] = name

for name, symbol in ENDEKSLER.items():
    ALL_SYMBOLS[symbol] = name

for name, symbol in TAHVILLER.items():
    ALL_SYMBOLS[symbol] = name


# ============================================================
# YAHOO FINANCE VERİ OKUMA
# ============================================================

def clean_download_data(data, symbol):
    """
    yfinance'ın farklı sürümlerinde oluşabilen MultiIndex
    ve tek sembol problemlerini temizler.
    """

    if data is None or data.empty:
        return None

    try:

        # MultiIndex ise ilgili sembolü almaya çalış.
        if isinstance(data.columns, pd.MultiIndex):

            if symbol in data.columns.get_level_values(-1):

                data = data.xs(
                    symbol,
                    axis=1,
                    level=-1
                )

            elif symbol in data.columns.get_level_values(0):

                data = data.xs(
                    symbol,
                    axis=1,
                    level=0
                )

        if "Close" not in data.columns:
            return None

        data = data.copy()

        data["Close"] = pd.to_numeric(
            data["Close"],
            errors="coerce"
        )

        data = data.dropna(
            subset=["Close"]
        )

        if len(data) < 2:
            return None

        return data

    except Exception:
        return None


def calculate_change(df):
    """
    Son iki kapanış arasındaki yüzde değişimi hesaplar.
    """

    try:

        today = float(df["Close"].iloc[-1])
        previous = float(df["Close"].iloc[-2])

        if previous == 0:
            return today, 0.0

        change = (
            (today - previous)
            / previous
        ) * 100

        return today, change

    except Exception:
        return 0.0, 0.0


# ============================================================
# TEK BATCH VERİ ÇEKME
# ============================================================

def download_batch(symbols):

    """
    Bir grup sembolü tek yfinance isteğiyle indirir.
    """

    if not symbols:
        return {}

    cache_key = "batch_" + "|".join(sorted(symbols))

    cached = cache_get(cache_key)

    if cached is not None:
        return cached

    result = {}

    try:

        data = yf.download(
            symbols,
            period=DOWNLOAD_PERIOD,
            interval="1d",
            group_by="ticker",
            auto_adjust=False,
            threads=True,
            progress=False
        )

        for symbol in symbols:

            try:

                df = clean_download_data(
                    data,
                    symbol
                )

                if df is None:
                    continue

                price, change = calculate_change(df)

                if price <= 0:
                    continue

                result[symbol] = {
                    "symbol": symbol,
                    "price": price,
                    "change": change,
                    "status": "Aktif",
                    "history": df
                }

            except Exception:
                continue

    except Exception:
        result = {}

    cache_set(
        cache_key,
        result
    )

    return result


# ============================================================
# THREAD İLE VERİ TOPLAMA
# ============================================================

class MarketDataFetcher(QThread):

    data_ready = Signal(str, list)
    status_ready = Signal(str)

    def __init__(self):
        super().__init__()

        self._running = True

    def stop(self):

        self._running = False

    def run(self):

        try:

            self.status_ready.emit(
                "Küresel piyasa verileri yükleniyor..."
            )

            # ------------------------------------------------
            # ENDEKSLER
            # ------------------------------------------------

            index_symbols = list(
                ENDEKSLER.values()
            )

            index_result = download_batch(
                index_symbols
            )

            endeks_listesi = []

            for name, symbol in ENDEKSLER.items():

                if symbol not in index_result:
                    continue

                info = index_result[symbol]

                endeks_listesi.append([
                    name,
                    f"{info['price']:.2f}",
                    "Aktif",
                    f"%{info['change']:+.2f}",
                    info["change"],
                    symbol
                ])

            self.data_ready.emit(
                "endeksler",
                endeks_listesi
            )


            # ------------------------------------------------
            # TAHVİLLER
            # ------------------------------------------------

            bond_symbols = list(
                set(TAHVILLER.values())
            )

            bond_result = download_batch(
                bond_symbols
            )

            tahvil_listesi = []

            for name, symbol in TAHVILLER.items():

                if symbol not in bond_result:
                    continue

                info = bond_result[symbol]

                tahvil_listesi.append([
                    name,
                    f"{info['price']:.2f}",
                    "Aktif",
                    f"%{info['change']:+.2f}",
                    info["change"],
                    symbol
                ])

            self.data_ready.emit(
                "tahviller",
                tahvil_listesi
            )


            # ------------------------------------------------
            # HİSSELER
            # ------------------------------------------------

            symbols = [
                symbol
                for symbol, name
                in TUM_HISSELER
            ]

            # Büyük listeyi küçük gruplara bölüyoruz.
            batch_size = 80

            batches = [
                symbols[i:i + batch_size]
                for i in range(
                    0,
                    len(symbols),
                    batch_size
                )
            ]

            hisse_sonuclari = {}

            # Aynı anda birkaç batch çalıştırılır.
            with ThreadPoolExecutor(
                max_workers=MAX_WORKERS
            ) as executor:

                future_map = {
                    executor.submit(
                        download_batch,
                        batch
                    ): batch
                    for batch in batches
                }

                for future in as_completed(
                    future_map
                ):

                    if not self._running:
                        break

                    try:

                        result = future.result()

                        hisse_sonuclari.update(
                            result
                        )

                        # Veri geldikçe tabloyu güncelle.
                        partial_list = []

                        for symbol, name in TUM_HISSELER:

                            if symbol not in hisse_sonuclari:
                                continue

                            info = hisse_sonuclari[
                                symbol
                            ]

                            partial_list.append([
                                symbol,
                                f"{info['price']:.2f}",
                                "Aktif",
                                f"%{info['change']:+.2f}",
                                info["change"],
                                name,
                                SYMBOL_INFO.get(
                                    symbol.upper(),
                                    {}
                                ).get(
                                    "market",
                                    ""
                                ),
                                SYMBOL_INFO.get(
                                    symbol.upper(),
                                    {}
                                ).get(
                                    "region",
                                    ""
                                )
                            ])

                        self.data_ready.emit(
                            "hisseler",
                            partial_list
                        )

                    except Exception:
                        continue

            self.status_ready.emit(
                "Küresel piyasa verileri hazır."
            )

        except Exception as e:

            self.status_ready.emit(
                f"Veri yükleme hatası: {str(e)}"
            )
# ============================================================
# TEKNİK ANALİZ FONKSİYONLARI
# ============================================================

def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def calculate_rsi(series, period=14):
    """
    RSI hesaplar.
    """
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, 1e-10)

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(series):
    """
    MACD + Signal + Histogram.
    """

    ema12 = series.ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = series.ewm(
        span=26,
        adjust=False
    ).mean()

    macd = ema12 - ema26

    signal = macd.ewm(
        span=9,
        adjust=False
    ).mean()

    histogram = macd - signal

    return macd, signal, histogram


def calculate_bollinger(series, period=20, std_multiplier=2):
    """
    Bollinger Bands.
    """

    middle = series.rolling(period).mean()

    std = series.rolling(period).std()

    upper = middle + (
        std * std_multiplier
    )

    lower = middle - (
        std * std_multiplier
    )

    return upper, middle, lower


def calculate_atr(hist, period=14):
    """
    ATR hesaplar.
    """

    if not all(
        column in hist.columns
        for column in ["High", "Low", "Close"]
    ):
        return None

    high = hist["High"]
    low = hist["Low"]
    close = hist["Close"]

    previous_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - previous_close).abs()
    tr3 = (low - previous_close).abs()

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = true_range.rolling(period).mean()

    return atr


def calculate_support_resistance(hist):
    """
    Basit fakat kullanışlı destek / direnç seviyeleri.
    """

    close = hist["Close"].dropna()

    if len(close) < 20:
        return None, None

    recent = close.tail(60)

    support = safe_float(
        recent.quantile(0.20)
    )

    resistance = safe_float(
        recent.quantile(0.80)
    )

    return support, resistance


# ============================================================
# GELİŞMİŞ TEKNİK ANALİZ
# ============================================================

def technical_analysis(hist):

    if hist is None or hist.empty:
        return {}

    close = hist["Close"].dropna()

    if len(close) < 2:
        return {}

    current = safe_float(close.iloc[-1])

    previous = safe_float(close.iloc[-2])

    daily_change = (
        ((current - previous) / previous) * 100
        if previous != 0
        else 0
    )

    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()

    ma20_value = safe_float(
        ma20.iloc[-1]
    )

    ma50_value = safe_float(
        ma50.iloc[-1]
    )

    ma200_value = (
        safe_float(ma200.iloc[-1])
        if len(close) >= 200
        else None
    )

    rsi_series = calculate_rsi(close)

    rsi = (
        safe_float(rsi_series.iloc[-1])
        if not pd.isna(rsi_series.iloc[-1])
        else 50
    )

    macd, signal, histogram = calculate_macd(
        close
    )

    macd_value = safe_float(
        macd.iloc[-1]
    )

    signal_value = safe_float(
        signal.iloc[-1]
    )

    histogram_value = safe_float(
        histogram.iloc[-1]
    )

    upper, middle, lower = calculate_bollinger(
        close
    )

    bb_upper = safe_float(
        upper.iloc[-1]
    )

    bb_middle = safe_float(
        middle.iloc[-1]
    )

    bb_lower = safe_float(
        lower.iloc[-1]
    )

    support, resistance = calculate_support_resistance(
        hist
    )

    atr_series = calculate_atr(hist)

    atr = (
        safe_float(atr_series.iloc[-1])
        if atr_series is not None
        and not pd.isna(atr_series.iloc[-1])
        else 0
    )

    # --------------------------------------------------------
    # TREND PUANI
    # --------------------------------------------------------

    trend_score = 0

    if current > ma20_value:
        trend_score += 1
    else:
        trend_score -= 1

    if current > ma50_value:
        trend_score += 1
    else:
        trend_score -= 1

    if ma200_value is not None:

        if current > ma200_value:
            trend_score += 2
        else:
            trend_score -= 2

    if macd_value > signal_value:
        trend_score += 1
    else:
        trend_score -= 1

    if trend_score >= 4:
        trend = "Güçlü Yükseliş"

    elif trend_score >= 2:
        trend = "Yükseliş"

    elif trend_score <= -4:
        trend = "Güçlü Düşüş"

    elif trend_score <= -2:
        trend = "Düşüş"

    else:
        trend = "Yatay / Kararsız"

    # --------------------------------------------------------
    # MOMENTUM
    # --------------------------------------------------------

    if rsi >= 70:
        momentum = "Aşırı Alım"

    elif rsi >= 60:
        momentum = "Güçlü Pozitif"

    elif rsi >= 50:
        momentum = "Pozitif"

    elif rsi >= 40:
        momentum = "Zayıf"

    elif rsi >= 30:
        momentum = "Negatif"

    else:
        momentum = "Aşırı Satım"

    # --------------------------------------------------------
    # HACİM
    # --------------------------------------------------------

    volume_ratio = None

    if "Volume" in hist.columns:

        volume = pd.to_numeric(
            hist["Volume"],
            errors="coerce"
        ).dropna()

        if len(volume) >= 20:

            avg_volume = (
                volume.tail(20).mean()
            )

            current_volume = (
                volume.iloc[-1]
            )

            if avg_volume > 0:

                volume_ratio = (
                    current_volume
                    / avg_volume
                )

    if volume_ratio is None:
        volume_status = "Veri yok"

    elif volume_ratio >= 1.5:
        volume_status = "Çok yüksek"

    elif volume_ratio >= 1.15:
        volume_status = "Yüksek"

    elif volume_ratio >= 0.85:
        volume_status = "Normal"

    else:
        volume_status = "Düşük"

    # --------------------------------------------------------
    # VOLATİLİTE
    # --------------------------------------------------------

    volatility = 0

    if len(close) >= 20:

        returns = close.pct_change().dropna()

        volatility = (
            returns.tail(20).std()
            * 100
        )

    if volatility >= 4:
        volatility_status = "Çok yüksek"

    elif volatility >= 2:
        volatility_status = "Yüksek"

    elif volatility >= 1:
        volatility_status = "Orta"

    else:
        volatility_status = "Düşük"

    return {
        "current": current,
        "daily_change": daily_change,
        "ma20": ma20_value,
        "ma50": ma50_value,
        "ma200": ma200_value,
        "rsi": rsi,
        "macd": macd_value,
        "macd_signal": signal_value,
        "macd_histogram": histogram_value,
        "bb_upper": bb_upper,
        "bb_middle": bb_middle,
        "bb_lower": bb_lower,
        "support": support,
        "resistance": resistance,
        "atr": atr,
        "trend_score": trend_score,
        "trend": trend,
        "momentum": momentum,
        "volume_ratio": volume_ratio,
        "volume_status": volume_status,
        "volatility": volatility,
        "volatility_status": volatility_status,
    }


# ============================================================
# AI / AKILLI YORUM MOTORU
# ============================================================

def generate_ai_comment(symbol, analysis):

    if not analysis:
        return (
            "<font color='#ef4444'>"
            "Yeterli veri bulunamadı."
            "</font>"
        )

    current = analysis["current"]
    change = analysis["daily_change"]

    trend = analysis["trend"]
    momentum = analysis["momentum"]

    rsi = analysis["rsi"]

    ma20 = analysis["ma20"]
    ma50 = analysis["ma50"]
    ma200 = analysis["ma200"]

    macd = analysis["macd"]
    macd_signal = analysis["macd_signal"]

    support = analysis["support"]
    resistance = analysis["resistance"]

    volume_status = analysis["volume_status"]

    volatility_status = analysis[
        "volatility_status"
    ]

    score = 0

    # --------------------------------------------------------
    # TREND
    # --------------------------------------------------------

    if current > ma20:
        score += 1
    else:
        score -= 1

    if current > ma50:
        score += 1
    else:
        score -= 1

    if ma200 is not None:

        if current > ma200:
            score += 2
        else:
            score -= 2

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------

    if 50 <= rsi < 70:
        score += 1

    elif rsi < 30:
        score += 1

    elif rsi > 75:
        score -= 1

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    if macd > macd_signal:
        score += 1
    else:
        score -= 1

    # --------------------------------------------------------
    # GENEL DURUM
    # --------------------------------------------------------

    if score >= 5:
        genel = "Pozitif görünüm"

    elif score >= 2:
        genel = "Ilımlı pozitif görünüm"

    elif score <= -5:
        genel = "Negatif görünüm"

    elif score <= -2:
        genel = "Ilımlı negatif görünüm"

    else:
        genel = "Kararsız / dengeli görünüm"

    # --------------------------------------------------------
    # RSI YORUMU
    # --------------------------------------------------------

    if rsi >= 75:

        rsi_comment = (
            "RSI oldukça yüksek seviyede. "
            "Kısa vadede aşırı alım nedeniyle "
            "kar realizasyonu riski artmış durumda."
        )

    elif rsi >= 65:

        rsi_comment = (
            "RSI güçlü momentum gösteriyor ancak "
            "aşırı alım bölgesine yaklaşılmış durumda."
        )

    elif rsi >= 50:

        rsi_comment = (
            "RSI 50 seviyesinin üzerinde ve momentum "
            "alıcılardan yana."
        )

    elif rsi >= 30:

        rsi_comment = (
            "RSI zayıf bölgede. Momentumun güçlenmesi "
            "için 50 seviyesinin üzerine çıkılması önemli."
        )

    else:

        rsi_comment = (
            "RSI aşırı satım bölgesinde. Tepki yükselişi "
            "ihtimali bulunmakla birlikte düşüş baskısı "
            "halen yüksek."
        )

    # --------------------------------------------------------
    # ORTALAMALAR
    # --------------------------------------------------------

    if current > ma20 and current > ma50:

        average_comment = (
            "Fiyat hem 20 hem de 50 günlük hareketli "
            "ortalamaların üzerinde. Kısa ve orta vadeli "
            "trend yapısı destekleyici."
        )

    elif current < ma20 and current < ma50:

        average_comment = (
            "Fiyat 20 ve 50 günlük ortalamaların altında. "
            "Kısa ve orta vadede satış baskısı öne çıkıyor."
        )

    else:

        average_comment = (
            "Fiyat hareketli ortalamalar arasında. "
            "Piyasa yön konusunda henüz net bir sinyal vermiyor."
        )

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------

    if macd > macd_signal:

        macd_comment = (
            "MACD sinyal çizgisinin üzerinde ve momentum "
            "pozitif tarafta."
        )

    else:

        macd_comment = (
            "MACD sinyal çizgisinin altında. Momentum "
            "aşağı yönlü baskı taşıyor."
        )

    # --------------------------------------------------------
    # HACİM
    # --------------------------------------------------------

    if volume_status == "Çok yüksek":

        volume_comment = (
            "İşlem hacmi olağan seviyelerin oldukça üzerinde. "
            "Fiyat hareketinin piyasa katılımıyla desteklendiği "
            "görülüyor."
        )

    elif volume_status == "Yüksek":

        volume_comment = (
            "Hacim ortalamanın üzerinde. Son fiyat hareketine "
            "olan piyasa ilgisi artmış durumda."
        )

    elif volume_status == "Düşük":

        volume_comment = (
            "Hacim zayıf. Fiyat hareketinin kalıcılığı "
            "konusunda daha fazla teyit gerekebilir."
        )

    else:

        volume_comment = (
            "Hacim normal seviyelerde seyrediyor."
        )

    # --------------------------------------------------------
    # DESTEK / DİRENÇ
    # --------------------------------------------------------

    level_comment = ""

    if support and resistance:

        support_distance = (
            (current - support)
            / current
            * 100
        )

        resistance_distance = (
            (resistance - current)
            / current
            * 100
        )

        level_comment = (
            f"Yaklaşık destek {support:.2f}, "
            f"direnç {resistance:.2f} seviyesinde. "
            f"Mevcut fiyat desteğin %{support_distance:.1f} "
            f"üzerinde ve direncin %{resistance_distance:.1f} "
            f"altında bulunuyor."
        )

    # --------------------------------------------------------
    # GÜNLÜK HAREKET
    # --------------------------------------------------------

    if change >= 3:

        daily_comment = (
            "Günlük fiyat hareketi güçlü pozitif. "
            "Kısa vadeli volatilite yükselmiş olabilir."
        )

    elif change <= -3:

        daily_comment = (
            "Günlük kayıp belirgin. Satış baskısının "
            "devam edip etmediği izlenmeli."
        )

    elif change > 0:

        daily_comment = (
            "Günlük fiyat hareketi pozitif ancak "
            "henüz güçlü bir kırılım sinyali oluşturmuyor."
        )

    elif change < 0:

        daily_comment = (
            "Günlük hareket negatif. Kısa vadede "
            "alıcılardan güçlü teyit gelmesi gerekiyor."
        )

    else:

        daily_comment = (
            "Günlük fiyat hareketi yatay."
        )

    # --------------------------------------------------------
    # SONUÇ
    # --------------------------------------------------------

    html = f"""
    <div style="font-size:13px; line-height:1.55;">

        <h3 style="color:#ffffff;">
            {symbol} — Akıllı Piyasa Analizi
        </h3>

        <p>
            <b>Genel değerlendirme:</b>
            {genel}
        </p>

        <hr>

        <p>
            <b>Trend:</b> {trend}<br>
            <b>Momentum:</b> {momentum}<br>
            <b>RSI:</b> {rsi:.2f}<br>
            <b>MACD:</b> {macd:.4f}<br>
            <b>Volatilite:</b> {volatility_status}<br>
            <b>Hacim:</b> {volume_status}
        </p>

        <p>
            {daily_comment}
        </p>

        <p>
            {average_comment}
        </p>

        <p>
            {rsi_comment}
        </p>

        <p>
            {macd_comment}
        </p>

        <p>
            {volume_comment}
        </p>

        <p>
            {level_comment}
        </p>

        <hr>

        <p style="color:#a1a1aa;">
            Bu analiz teknik göstergelere dayalı otomatik
            bir değerlendirmedir. Yatırım tavsiyesi değildir.
        </p>

    </div>
    """

    return html


# ============================================================
# DETAY PENCERESİ
# ============================================================

class DetailWindow(QDialog):

    def __init__(
        self,
        symbol,
        current_price,
        change_str,
        parent=None
    ):

        super().__init__(parent)

        self.symbol = symbol
        self.current_price = current_price
        self.change_str = change_str

        self.setWindowTitle(self.symbol)

        self.resize(1100, 800)

        self.hist = None
        self.analysis = None

        self.init_ui()

        self.load_historical_data()
    def add_to_watchlist(self, symbol, name, price, change):
        # Python'ın 'sys' modülü üzerinden uygulamanın ana penceresini direkt çekiyoruz.
        # Hiçbir arama/parent sorgusu yapmaz, hatasız çalışır.
        from PySide6.QtWidgets import QApplication
        
        main_win = None
        for win in QApplication.instance().topLevelWidgets():
            if win.__class__.__name__ == "MainWindow":
                main_win = win
                break
        
        if main_win and hasattr(main_win, 'izleme_listesi_yoneticisi'):
            main_win.izleme_listesi_yoneticisi.add_or_focus_symbol(symbol, name, price, change, "Hisse")
        else:
            print("Kritik: MainWindow veya izleme_listesi_yoneticisi sistemde yok!")
    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def init_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(15,15,15,15)

        main_layout.setSpacing(12)

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header_layout = QHBoxLayout()

        self.lbl_title = QLabel(f"<b>{self.symbol}</b> Detaylı Görünüm")

        self.star_btn = QPushButton(" ")
        self.star_btn.setCursor(Qt.PointingHandCursor)
        self.star_btn.setFixedSize(32, 32)
        # Butonu zaten oluşturduğuna göre, şununla bağlantısını yapalım:
        # 'symbol', 'name' gibi değişkenlerin zaten elinde olması lazım
        self.star_btn.clicked.connect(lambda: self.add_to_watchlist(self.symbol, self.symbol, self.current_price, self.change_str))

        # Stilini düzeltelim (çirkin çizgi gitsin):
        self.star_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;  /* Dairenin iç rengi (koyu gri) */
                border: 1px solid #27272a;   /* İnce çerçeve */
                border-radius: 16px;         /* Tam daire */
            }
            QPushButton:hover {
                background-color: #27272a;  /* Üzerine gelince hafif açılan renk */
                border-color: #3f3f46;
            }
            QPushButton:pressed {
                background-color: #141414;  /* Tıklanıldığında parlayan renk (altın sarısı) */
                border-color: #141414;
            }
        """)        
     

        self.lbl_title.setStyleSheet("font-size:20px; color:#ffffff;")

        self.lbl_price = QLabel(
            f"Fiyat: {self.current_price} | "
            f"Değişim: {self.change_str}"
        )

        if "+" in self.change_str:
            color = "#22c55e"
        else:
            color = "#ef4444"

        self.lbl_price.setStyleSheet(
            f"font-size:15px; color:{color};"
        )

        header_layout.addWidget(self.lbl_title)

        header_layout.addStretch()

        header_layout.addWidget(self.lbl_price)

        header_layout.addSpacing(10)
        header_layout.addWidget(self.star_btn)

        main_layout.addLayout(
            header_layout
        )

        # ----------------------------------------------------
        # GRAFİK
        # ----------------------------------------------------

        if MATPLOTLIB_AVAILABLE:

            self.figure = Figure(
                figsize=(10, 6),
                facecolor="#050505"
            )

            self.canvas = FigureCanvas(
                self.figure
            )
            # Mevcut FigureCanvas'ın (canvas) altına:
            self.toolbar = NavigationToolbar(self.canvas, self)
            main_layout.addWidget(self.toolbar)

            self.canvas.setStyleSheet(
                """
                background-color:#050505;
                border:1px solid #27272a;
                border-radius:6px;
                """
            )

            main_layout.addWidget(
                self.canvas,
                stretch=4
            )

        else:

            lbl_err = QLabel(
                "Matplotlib kütüphanesi bulunamadı."
            )

            lbl_err.setStyleSheet(
                "color:#ef4444;"
            )

            main_layout.addWidget(
                lbl_err
            )

        # ----------------------------------------------------
        # ANALİZ
        # ----------------------------------------------------

        lbl_comment_title = QLabel(
            "<b>Yapay Zeka & Teknik Yorum</b>"
        )

        lbl_comment_title.setStyleSheet(
            "color:#a1a1aa; font-size:13px;"
        )

        main_layout.addWidget(
            lbl_comment_title
        )

        self.text_browser = QTextBrowser()

        self.text_browser.setStyleSheet(
            """
            background-color:#09090b;
            color:#f8fafc;
            border:1px solid #27272a;
            border-radius:6px;
            padding:10px;
            font-size:13px;
            """
        )

        self.text_browser.setHtml(
            "<i>Veriler analiz ediliyor...</i>"
        )

        main_layout.addWidget(
            self.text_browser,
            stretch=2
        )

    # --------------------------------------------------------
    # VERİ
    # --------------------------------------------------------

    def load_historical_data(self):

        try:

            cached = cache_get(
                f"history_{self.symbol}"
            )

            if cached is not None:

                hist = cached

            else:

                ticker = yf.Ticker(
                    self.symbol
                )

                hist = ticker.history(
                    period="1y",
                    interval="1d",
                    auto_adjust=False
                )

                if hist is None or hist.empty:

                    self.text_browser.setHtml(
                        "<font color='#ef4444'>"
                        "Bu varlık için yeterli geçmiş "
                        "veri bulunamadı."
                        "</font>"
                    )

                    return

                cache_set(
                    f"history_{self.symbol}",
                    hist
                )

            self.hist = hist

            self.analysis = technical_analysis(
                hist
            )

            self.draw_professional_chart()

            self.text_browser.setHtml(
                generate_ai_comment(
                    self.symbol,
                    self.analysis
                )
            )

        except Exception as e:

            self.text_browser.setHtml(
                f"""
                <font color='#ef4444'>
                Analiz yüklenirken hata oluştu:
                {str(e)}
                </font>
                """
            )

    # --------------------------------------------------------
    # PROFESYONEL GRAFİK
    # --------------------------------------------------------

    def draw_professional_chart(self):

        if not MATPLOTLIB_AVAILABLE:
            return

        if self.hist is None:
            return

        hist = self.hist.copy()

        close = hist["Close"]

        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()

        ma200 = close.rolling(200).mean()

        upper, middle, lower = calculate_bollinger(
            close
        )

        rsi = calculate_rsi(
            close
        )

        macd, signal, histogram = calculate_macd(
            close
        )

        # ----------------------------------------------------
        # FIGURE
        # ----------------------------------------------------

        self.figure.clear()

        grid = self.figure.add_gridspec(
            4,
            1,
            height_ratios=[
                5,
                1.5,
                1.5,
                1.5
            ],
            hspace=0.05
        )

        ax_price = self.figure.add_subplot(
            grid[0]
        )

        ax_volume = self.figure.add_subplot(
            grid[1],
            sharex=ax_price
        )

        ax_rsi = self.figure.add_subplot(
            grid[2],
            sharex=ax_price
        )

        ax_macd = self.figure.add_subplot(
            grid[3],
            sharex=ax_price
        )

        # ----------------------------------------------------
        # DARK TEMA
        # ----------------------------------------------------

        axes = [
            ax_price,
            ax_volume,
            ax_rsi,
            ax_macd
        ]

        for ax in axes:

            ax.set_facecolor(
                "#050505"
            )

            ax.tick_params(
                colors="#a1a1aa",
                labelsize=8
            )

            ax.grid(
                True,
                color="#18181b",
                linestyle="--",
                alpha=0.45
            )

            for spine in ax.spines.values():

                spine.set_color(
                    "#27272a"
                )

        # ----------------------------------------------------
        # FİYAT
        # ----------------------------------------------------

        ax_price.plot(
            hist.index,
            close,
            color="#60a5fa",
            linewidth=2,
            label="Kapanış"
        )

        ax_price.plot(
            hist.index,
            ma20,
            color="#facc15",
            linewidth=1.2,
            label="MA20"
        )

        ax_price.plot(
            hist.index,
            ma50,
            color="#fb923c",
            linewidth=1.2,
            label="MA50"
        )

        if ma200.notna().any():

            ax_price.plot(
                hist.index,
                ma200,
                color="#8507ca",
                linewidth=1.1,
                label="MA200"
            )

        ax_price.plot(
            hist.index,
            upper,
            color="#94a3b8",
            linewidth=0.8,
            linestyle="--",
            alpha=0.7
        )

        ax_price.plot(
            hist.index,
            lower,
            color="#94a3b8",
            linewidth=0.8,
            linestyle="--",
            alpha=0.7
        )

        ax_price.fill_between(
            hist.index,
            lower.astype(float),
            upper.astype(float),
            alpha=0.08
        )

        if self.analysis:

            support = self.analysis.get(
                "support"
            )

            resistance = self.analysis.get(
                "resistance"
            )

            if support:

                ax_price.axhline(
                    support,
                    linestyle=":",
                    linewidth=1,
                    color="#22c55e",
                    label="Destek"
                )

            if resistance:

                ax_price.axhline(
                    resistance,
                    linestyle=":",
                    linewidth=1,
                    color="#ef4444",
                    label="Direnç"
                )

        ax_price.set_title(
            f"{self.symbol} - 1 Yıllık Teknik Görünüm",
            color="#ffffff",
            fontsize=11
        )

        ax_price.legend(
            loc="upper left",
            facecolor="#09090b",
            edgecolor="#27272a",
            labelcolor="#f8fafc",
            fontsize=7
        )

        # ----------------------------------------------------
        # HACİM
        # ----------------------------------------------------

        if "Volume" in hist.columns:

            volume = hist["Volume"].fillna(0)

            ax_volume.bar(
                hist.index,
                volume,
                alpha=0.55,
                width=1
            )

            ax_volume.set_ylabel(
                "Hacim",
                color="#a1a1aa",
                fontsize=8
            )

        # ----------------------------------------------------
        # RSI
        # ----------------------------------------------------

        ax_rsi.plot(
            hist.index,
            rsi,
            linewidth=1.2
        )

        ax_rsi.axhline(
            70,
            linestyle="--",
            linewidth=0.8,
            alpha=0.7
        )

        ax_rsi.axhline(
            30,
            linestyle="--",
            linewidth=0.8,
            alpha=0.7
        )

        ax_rsi.set_ylim(
            0,
            100
        )

        ax_rsi.set_ylabel(
            "RSI",
            color="#a1a1aa",
            fontsize=8
        )

        # ----------------------------------------------------
        # MACD
        # ----------------------------------------------------

        ax_macd.plot(
            hist.index,
            macd,
            linewidth=1.1,
            label="MACD"
        )

        ax_macd.plot(
            hist.index,
            signal,
            linewidth=1,
            linestyle="--",
            label="Signal"
        )

        ax_macd.bar(
            hist.index,
            histogram,
            alpha=0.35,
            width=1
        )

        ax_macd.axhline(
            0,
            linewidth=0.8,
            alpha=0.6
        )

        ax_macd.set_ylabel(
            "MACD",
            color="#a1a1aa",
            fontsize=8
        )

        ax_macd.legend(
            loc="upper left",
            facecolor="#09090b",
            edgecolor="#27272a",
            labelcolor="#f8fafc",
            fontsize=7
        )

        # ----------------------------------------------------
        # X AXIS
        # ----------------------------------------------------

        ax_price.tick_params(
            labelbottom=False
        )

        ax_volume.tick_params(
            labelbottom=False
        )

        ax_rsi.tick_params(
            labelbottom=False
        )

        self.figure.tight_layout()

        self.canvas.draw()
        

# ============================================================
# KÜRESEL BORSALAR MANAGER
# ============================================================

class KureselBorsalarManager:

    def __init__(self, main_window):

        self.window = main_window

        self.tables = {"hisseler": self.window.tableWidget_2,"endeksler": self.window.tableWidget_3,"tahviller": self.window.tableWidget_6
        }

        self.raw_data = {"hisseler": [],"endeksler": [],"tahviller": []
        }

        self.filtered_data = {"hisseler": [],"endeksler": [],"tahviller": []
        }

        self.setup_tables()

        self.setup_ui_elements()

        self.start_fetcher()

    # --------------------------------------------------------
    # TABLOLAR
    # --------------------------------------------------------

    def setup_tables(self):

        for name, table in self.tables.items():

            if table is None:
                continue

            table.verticalHeader().setVisible(False)

            table.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch
            )

            table.setShowGrid(False)

            table.setAlternatingRowColors(
                False
            )

            table.setSelectionBehavior(
                QAbstractItemView.SelectRows
            )

            table.setEditTriggers(
                QAbstractItemView.NoEditTriggers
            )

            table.setSortingEnabled(
                False
            )

            table.setColumnCount(4)

            table.setHorizontalHeaderLabels([
                "Sembol / Ad",
                "Fiyat",
                "Durum",
                "Değişim"
            ])

            table.itemDoubleClicked.connect(
                self.tablo_oge_tiklandi
            )

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def setup_ui_elements(self):

        # ----------------------------------------------------
        # YÜZDE MİN
        # ----------------------------------------------------

        if hasattr(
            self.window,
            "doubleSpinBox"
        ):

            self.window.doubleSpinBox.setRange(
                -100.0,
                1000.0
            )

            self.window.doubleSpinBox.setValue(
                -100.0
            )

            self.window.doubleSpinBox.valueChanged.connect(
                self.uygula_filtre
            )

        # ----------------------------------------------------
        # YÜZDE MAX
        # ----------------------------------------------------

        if hasattr(
            self.window,
            "doubleSpinBox_2"
        ):

            self.window.doubleSpinBox_2.setRange(
                -100.0,
                1000.0
            )

            self.window.doubleSpinBox_2.setValue(
                1000.0
            )

            self.window.doubleSpinBox_2.valueChanged.connect(
                self.uygula_filtre
            )

        # ----------------------------------------------------
        # ARAMA
        # ----------------------------------------------------

        if hasattr(
            self.window,
            "lineEdit"
        ):

            self.window.lineEdit.textChanged.connect(
                self.uygula_filtre
            )

        # ----------------------------------------------------
        # ENDEKS FİLTRESİ
        # ----------------------------------------------------

        if hasattr(
            self.window,
            "comboBox_2"
        ):

            self.window.comboBox_2.clear()

            self.window.comboBox_2.addItems([
                "Endeks Seçiniz",

                "BIST 100",
                "BIST 30",

                "NASDAQ / ABD Hisseleri",
                "S&P 500 / ABD",

                "DAX 40",
                "FTSE / İngiltere",
                "CAC 40 / Fransa",

                "Nikkei 225 / Japonya",
                "Hang Seng / Hong Kong",

                "Çin",
                "Hindistan",
                "KOSPI / Güney Kore",

                "TSX / Kanada",
                "ASX / Avustralya"
            ])

            self.window.comboBox_2.currentIndexChanged.connect(
                self.uygula_filtre
            )

        # ----------------------------------------------------
        # SEKTÖR
        # ----------------------------------------------------

        if hasattr(
            self.window,
            "comboBox_3"
        ):

            self.window.comboBox_3.clear()

            self.window.comboBox_3.addItems([
                "Sektör Seçiniz",
                "Teknoloji",
                "Bankacılık",
                "Sanayi",
                "Enerji",
                "Sağlık",
                "Otomotiv",
                "Finans",
                "Tüketim"
            ])

            self.window.comboBox_3.currentIndexChanged.connect(
                self.uygula_filtre
            )

        # ----------------------------------------------------
        # TAB DEĞİŞİMİ
        # ----------------------------------------------------

        if hasattr(
            self.window,
            "tabWidget"
        ):

            self.window.tabWidget.currentChanged.connect(
                lambda index: self.uygula_filtre()
            )

    # --------------------------------------------------------
    # VERİ MOTORU
    # --------------------------------------------------------

    def start_fetcher(self):

        self.fetcher = MarketDataFetcher()

        self.fetcher.data_ready.connect(
            self.veri_geldi
        )

        self.fetcher.status_ready.connect(
            self.durum_geldi
        )

        self.fetcher.start()

    def durum_geldi(self, message):

        # UI'da durum etiketi varsa kullan.
        for widget_name in [
            "label_status",
            "label_25",
            "statusLabel"
        ]:

            if hasattr(
                self.window,
                widget_name
            ):

                widget = getattr(
                    self.window,
                    widget_name
                )

                if widget is not None:

                    try:
                        widget.setText(
                            message
                        )
                    except Exception:
                        pass

                    break

    def veri_geldi(
        self,
        kategori,
        data
    ):

        self.raw_data[kategori] = data

        self.filtered_data[kategori] = data

        self.uygula_filtre()

    # --------------------------------------------------------
    # AKTİF TAB
    # --------------------------------------------------------

    def aktif_kategori_bul(self):

        if not hasattr(
            self.window,
            "tabWidget"
        ):

            return "hisseler"

        current_index = (
            self.window.tabWidget.currentIndex()
        )

        tab_map = {
            0: "hisseler",
            1: "endeksler",
            2: "tahviller"
        }

        return tab_map.get(
            current_index,
            "hisseler"
        )

    # --------------------------------------------------------
    # TABLO DOLDUR
    # --------------------------------------------------------

    def tabloyu_doldur(
        self,
        kategori,
        data
    ):

        table = self.tables.get(
            kategori
        )

        if table is None:
            return

        table.setUpdatesEnabled(
            False
        )

        try:

            table.setRowCount(
                len(data)
            )

            for row_idx, row_data in enumerate(
                data
            ):

                if len(row_data) < 4:
                    continue

                for col_idx in range(4):

                    val = row_data[
                        col_idx
                    ]

                    item = QTableWidgetItem(
                        str(val)
                    )

                    if col_idx == 3:

                        change_value = (
                            safe_float(
                                row_data[4]
                                if len(row_data) > 4
                                else 0
                            )
                        )

                        if change_value > 0:

                            item.setForeground(
                                QColor("#22c55e")
                            )

                        elif change_value < 0:

                            item.setForeground(
                                QColor("#ef4444")
                            )

                        else:

                            item.setForeground(
                                QColor("#a1a1aa")
                            )

                    table.setItem(
                        row_idx,
                        col_idx,
                        item
                    )

        finally:

            table.setUpdatesEnabled(
                True
            )

    # --------------------------------------------------------
    # ARAMA
    # --------------------------------------------------------

    def arama_eslesiyor(
        self,
        row,
        arama
    ):

        if not arama:
            return True

        # Sembol
        if arama in str(
            row[0]
        ).upper():

            return True

        # Şirket adı
        if len(row) > 5:

            if arama in str(
                row[5]
            ).upper():

                return True

        # Piyasa
        if len(row) > 6:

            if arama in str(
                row[6]
            ).upper():

                return True

        # Ülke
        if len(row) > 7:

            if arama in str(
                row[7]
            ).upper():

                return True

        return False

    # --------------------------------------------------------
    # ENDEKS FİLTRESİ
    # --------------------------------------------------------

    def endeks_filtresi_uygun(
        self,
        sembol,
        secim
    ):

        if secim == "Endeks Seçiniz":
            return True

        sembol = sembol.upper()

        filtreler = {

            "BIST 100":
                [".IS"],

            "BIST 30":
                [
                    "THYAO.IS","GARAN.IS","EREGL.IS","AKBNK.IS","ISCTR.IS","KCHOL.IS","SAHOL.IS","BIMAS.IS","TUPRS.IS","ASELS.IS","PETKM.IS","SISE.IS","YKBNK.IS","ARCLK.IS","TOASO.IS","FROTO.IS","PGSUS.IS","HEKTS.IS","SASA.IS","ENKAI.IS","TCELL.IS","TTKOM.IS","KRDMD.IS","KOZAL.IS","ASTOR.IS","EKGYO.IS","HALKB.IS","VAKBN.IS","MGROS.IS","AKSEN.IS"
                ],

            "NASDAQ / ABD Hisseleri":
                [
                    "NASDAQ / ABD"
                ],

            "S&P 500 / ABD":
                [
                    "S&P 500 / ABD"
                ],

            "DAX 40":
                [
                    ".DE"
                ],

            "FTSE / İngiltere":
                [
                    ".L"
                ],

            "CAC 40 / Fransa":
                [
                    ".PA"
                ],

            "Nikkei 225 / Japonya":
                [
                    ".T"
                ],

            "Hang Seng / Hong Kong":
                [
                    ".HK"
                ],

            "Çin":
                [
                    "Çin"
                ],

            "Hindistan":
                [
                    ".NS"
                ],

            "KOSPI / Güney Kore":
                [
                    ".KS"
                ],

            "TSX / Kanada":
                [
                    ".TO"
                ],

            "ASX / Avustralya":
                [
                    ".AX"
                ]
        }

        hedefler = filtreler.get(
            secim
        )

        if not hedefler:
            return True

        if secim == "BIST 30":

            return sembol in hedefler

        # Sembolün kendisinde kontrol
        for hedef in hedefler:

            if hedef in sembol:
                return True

        # Piyasa adı üzerinden kontrol
        info = SYMBOL_INFO.get(
            sembol,
            {}
        )

        market = str(
            info.get(
                "market",
                ""
            )
        ).upper()

        for hedef in hedefler:

            if hedef.upper() in market:
                return True

        return False

    # --------------------------------------------------------
    # SEKTÖR
    # --------------------------------------------------------

    def sektor_uygun(
        self,
        row,
        sektor
    ):

        if sektor == "Sektör Seçiniz":
            return True

        symbol = str(
            row[0]
        ).upper()

        # ----------------------------------------------------
        # BANKACILIK
        # ----------------------------------------------------

        bankalar = {
            "AKBNK.IS",
            "GARAN.IS",
            "ISCTR.IS",
            "YKBNK.IS",
            "HALKB.IS",
            "VAKBN.IS",
            "TSKB.IS",
            "SKBNK.IS",

            "JPM",
            "BAC",
            "WFC",
            "C",
            "GS",
            "MS",

            "HSBA.L",
            "BARC.L",
            "LLOY.L",

            "BNP.PA",
            "DBK.DE",
            "8306.T",
            "0005.HK"
        }

        if sektor == "Bankacılık":

            return symbol in bankalar

        # ----------------------------------------------------
        # TEKNOLOJİ
        # ----------------------------------------------------

        teknoloji = {"AAPL","MSFT","NVDA","GOOGL","GOOG","AMD","INTC","ADBE","CRM","ORCL","AVGO","QCOM","CSCO","PLTR","CRWD","DDOG","NET","SNOW","SAP.DE","IFX.DE","0700.HK","6758.T","005930.KS","TSM",
        }

        if sektor == "Teknoloji":

            return symbol in teknoloji

        # ----------------------------------------------------
        # SANAYİ
        # ----------------------------------------------------

        sanayi = {"EREGL.IS","KCHOL.IS","SAHOL.IS","TUPRS.IS","PETKM.IS","SISE.IS", "ARCLK.IS","TOASO.IS","FROTO.IS","SIE.DE", "AIR.DE","CAT","DE","GE","BA.L","AIR.PA"
        }

        if sektor == "Sanayi":

            return symbol in sanayi

        # ----------------------------------------------------
        # ENERJİ
        # ----------------------------------------------------

        enerji = {"TUPRS.IS","PETKM.IS","AKSEN.IS","ENJSA.IS","GWIND.IS","ZOREN.IS","XOM","CVX","COP","SLB","SHEL.L","BP.L","TTE.PA","RWE.DE","EOAN.DE"
        }

        if sektor == "Enerji":

            return symbol in enerji

        # ----------------------------------------------------
        # SAĞLIK
        # ----------------------------------------------------

        saglik = {"JNJ","LLY","PFE","MRK","ABBV","ABT","UNH","TMO","MRNA","VRTX","REGN","ISRG","AZN.L","GSK.L","SAN.PA"
        }

        if sektor == "Sağlık":

            return symbol in saglik

        # ----------------------------------------------------
        # OTOMOTİV
        # ----------------------------------------------------

        otomotiv = {"FROTO.IS","TOASO.IS","VOW3.DE","MBG.DE","BMW.DE","7203.T","7267.T","7269.T","TSLA","GM","F"
        }

        if sektor == "Otomotiv":

            return symbol in otomotiv

        # ----------------------------------------------------
        # FİNANS
        # ----------------------------------------------------

        finans = {"JPM","BAC","WFC","GS","MS","V","MA","AXP","BLK","SPGI","GARAN.IS","AKBNK.IS","ISCTR.IS","YKBNK.IS","KCHOL.IS","SAHOL.IS"
        }

        if sektor == "Finans":

            return symbol in finans

        # ----------------------------------------------------
        # TÜKETİM
        # ----------------------------------------------------

        tuketim = {
            "WMT","COST","MCD","KO","PEP","PG","NKE","SBUX","AMZN","BIMAS.IS","MGROS.IS","SOKM.IS","ULKER.IS","CCOLA.IS","MC.PA","OR.PA"
        }

        if sektor == "Tüketim":

            return symbol in tuketim

        return True

    # --------------------------------------------------------
    # FİLTRE
    # --------------------------------------------------------

    def uygula_filtre(self):

        kategori = (
            self.aktif_kategori_bul()
        )

        data = self.raw_data.get(
            kategori,
            []
        )

        if not data:

            self.tabloyu_doldur(
                kategori,
                []
            )

            return

        # ----------------------------------------------------
        # ARAMA
        # ----------------------------------------------------

        arama = ""

        if hasattr(
            self.window,
            "lineEdit"
        ):

            arama = (
                self.window.lineEdit.text()
                .strip()
                .upper()
            )

        # ----------------------------------------------------
        # ENDEKS
        # ----------------------------------------------------

        endeks_secimi = (
            "Endeks Seçiniz"
        )

        if hasattr(
            self.window,
            "comboBox_2"
        ):

            endeks_secimi = (
                self.window.comboBox_2.currentText()
            )

        # ----------------------------------------------------
        # SEKTÖR
        # ----------------------------------------------------

        sektor_secimi = (
            "Sektör Seçiniz"
        )

        if hasattr(
            self.window,
            "comboBox_3"
        ):

            sektor_secimi = (
                self.window.comboBox_3.currentText()
            )

        # ----------------------------------------------------
        # MIN / MAX
        # ----------------------------------------------------

        min_yuzde = -100.0

        if hasattr(
            self.window,
            "doubleSpinBox"
        ):

            min_yuzde = (
                self.window.doubleSpinBox.value()
            )

        max_yuzde = 1000.0

        if hasattr(
            self.window,
            "doubleSpinBox_2"
        ):

            max_yuzde = (
                self.window.doubleSpinBox_2.value()
            )

        # ----------------------------------------------------
        # FİLTRELE
        # ----------------------------------------------------

        filtrelenmis = []

        for row in data:

            if len(row) < 5:
                continue

            sembol = str(
                row[0]
            ).upper()

            degisim = safe_float(
                row[4]
            )

            # Arama
            if not self.arama_eslesiyor(
                row,
                arama
            ):
                continue

            # Yüzde
            if not (
                min_yuzde
                <= degisim
                <= max_yuzde
            ):
                continue

            # Hisse endeks filtresi
            if kategori == "hisseler":

                if not self.endeks_filtresi_uygun(
                    sembol,
                    endeks_secimi
                ):
                    continue

                if not self.sektor_uygun(
                    row,
                    sektor_secimi
                ):
                    continue

            filtrelenmis.append(
                row
            )

        # ----------------------------------------------------
        # SIRALAMA
        # ----------------------------------------------------

        filtrelenmis.sort(
            key=lambda x:
                safe_float(
                    x[4]
                ),
            reverse=True
        )

        self.filtered_data[
            kategori
        ] = filtrelenmis

        self.tabloyu_doldur(
            kategori,
            filtrelenmis
        )

# --------------------------------------------------------
    # ÇİFT TIK
    # --------------------------------------------------------

    def tablo_oge_tiklandi(self, item):
        try:
            row = item.row()
            table = item.tableWidget()
            if table is None:
                return

            symbol_text = table.item(row, 0).text()
            price = table.item(row, 1).text()
            change = table.item(row, 3).text()

            # 1. Önce Endekslerde ara
            real_symbol = None
            clean_target = symbol_text.strip().lower()

            for name, symbol in ENDEKSLER.items():
                if name.strip().lower() == clean_target:
                    real_symbol = symbol
                    break

            # 2. Endekslerde bulamadıysa Tahvillerde ara
            if real_symbol is None:
                for name, symbol in TAHVILLER.items():
                    if name.strip().lower() == clean_target:
                        real_symbol = symbol
                        break

            # 3. İkisinde de yoksa (veya eşleşme başarısızsa), 
            # asla rastgele bir son elemana düşme, doğrudan yazan metni (hisse kodunu) baz al!
            if real_symbol is None:
                real_symbol = symbol_text.strip()

            self.detail_dialog = DetailWindow(
                real_symbol,
                price,
                change
            )
            self.detail_dialog.exec()

        except Exception as e:
            print("Detay penceresi hatası:", e)