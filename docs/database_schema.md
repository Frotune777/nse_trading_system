# Project Database Schemas

## Database: trading.db

### Table: jio_1d_ohlc

```sql
CREATE TABLE "jio_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: adanient_1d_ohlc

```sql
CREATE TABLE "adanient_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
, "SMA_5" REAL, "SMA_10" REAL, "SMA_50" REAL, "SMA_100" REAL, "SMA_200" REAL, "EMA_9" REAL, "EMA_12" REAL, "EMA_20" REAL, "EMA_26" REAL, "EMA_50" REAL, "EMA_200" REAL, "WMA_20" REAL, "WMA_50" REAL, "DEMA_20" REAL, "TEMA_20" REAL, "TRIMA_20" REAL, "KAMA_20" REAL, "MAMA" REAL, "FAMA" REAL, "T3_20" REAL, "BB_UPPER" REAL, "BB_MIDDLE" REAL, "BB_LOWER" REAL, "SAR" REAL, "HT_TRENDLINE" REAL, "RSI_7" REAL, "RSI_21" REAL, "MACD" REAL, "MACD_SIGNAL" REAL, "MACD_HIST" REAL, "STOCH_K" REAL, "STOCH_D" REAL, "STOCHRSI_K" REAL, "STOCHRSI_D" REAL, "WILLR_14" REAL, "CCI_14" REAL, "CCI_20" REAL, "ROC_10" REAL, "ROC_20" REAL, "MOM_10" REAL, "ADX_14" REAL, "PLUS_DI" REAL, "MINUS_DI" REAL, "AROON_DOWN" REAL, "AROON_UP" REAL, "AROONOSC" REAL, "BOP" REAL, "ULTOSC" REAL, "MFI" REAL, "PPO" REAL, "TRIX" REAL, "OBV" REAL, "AD" REAL, "ADOSC" REAL, "VOLUME_SMA_10" REAL, "VOLUME_SMA_20" REAL, "VOLUME_SMA_50" REAL, "ATR_7" REAL, "ATR_14" REAL, "ATR_21" REAL, "NATR_14" REAL, "STDDEV_10" REAL, "STDDEV_20" REAL, "CDL_DOJI" INTEGER, "CDL_HAMMER" INTEGER, "CDL_SHOOTINGSTAR" INTEGER, "CDL_ENGULFING" INTEGER, "CDL_MORNINGSTAR" INTEGER, "CDL_EVENINGSTAR" INTEGER)
```

### Table: adaniports_1d_ohlc

```sql
CREATE TABLE "adaniports_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: apollohosp_1d_ohlc

```sql
CREATE TABLE "apollohosp_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: asianpaint_1d_ohlc

```sql
CREATE TABLE "asianpaint_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: axisbank_1d_ohlc

```sql
CREATE TABLE "axisbank_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: bajaj_auto_1d_ohlc

```sql
CREATE TABLE "bajaj_auto_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: bajfinance_1d_ohlc

```sql
CREATE TABLE "bajfinance_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
, "SMA_5" REAL, "SMA_10" REAL, "SMA_50" REAL, "SMA_100" REAL, "SMA_200" REAL, "EMA_9" REAL, "EMA_12" REAL, "EMA_20" REAL, "EMA_26" REAL, "EMA_50" REAL, "EMA_200" REAL, "WMA_20" REAL, "WMA_50" REAL, "DEMA_20" REAL, "TEMA_20" REAL, "TRIMA_20" REAL, "KAMA_20" REAL, "MAMA" REAL, "FAMA" REAL, "T3_20" REAL, "BB_UPPER" REAL, "BB_MIDDLE" REAL, "BB_LOWER" REAL, "SAR" REAL, "HT_TRENDLINE" REAL, "RSI_7" REAL, "RSI_21" REAL, "MACD" REAL, "MACD_SIGNAL" REAL, "MACD_HIST" REAL, "STOCH_K" REAL, "STOCH_D" REAL, "STOCHRSI_K" REAL, "STOCHRSI_D" REAL, "WILLR_14" REAL, "CCI_14" REAL, "CCI_20" REAL, "ROC_10" REAL, "ROC_20" REAL, "MOM_10" REAL, "ADX_14" REAL, "PLUS_DI" REAL, "MINUS_DI" REAL, "AROON_DOWN" REAL, "AROON_UP" REAL, "AROONOSC" REAL, "BOP" REAL, "ULTOSC" REAL, "MFI" REAL, "PPO" REAL, "TRIX" REAL, "OBV" REAL, "AD" REAL, "ADOSC" REAL, "VOLUME_SMA_10" REAL, "VOLUME_SMA_20" REAL, "VOLUME_SMA_50" REAL, "ATR_7" REAL, "ATR_14" REAL, "ATR_21" REAL, "NATR_14" REAL, "STDDEV_10" REAL, "STDDEV_20" REAL, "CDL_DOJI" INTEGER, "CDL_HAMMER" INTEGER, "CDL_SHOOTINGSTAR" INTEGER, "CDL_ENGULFING" INTEGER, "CDL_MORNINGSTAR" INTEGER, "CDL_EVENINGSTAR" INTEGER)
```

### Table: bajajfinsv_1d_ohlc

```sql
CREATE TABLE "bajajfinsv_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: bel_1d_ohlc

```sql
CREATE TABLE "bel_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: bhartiartl_1d_ohlc

```sql
CREATE TABLE "bhartiartl_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: cipla_1d_ohlc

```sql
CREATE TABLE "cipla_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: coalindia_1d_ohlc

```sql
CREATE TABLE "coalindia_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: drreddy_1d_ohlc

```sql
CREATE TABLE "drreddy_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: eichermot_1d_ohlc

```sql
CREATE TABLE "eichermot_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: eternal_1d_ohlc

```sql
CREATE TABLE "eternal_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: grasim_1d_ohlc

```sql
CREATE TABLE "grasim_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: hcltech_1d_ohlc

```sql
CREATE TABLE "hcltech_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: hdfcbank_1d_ohlc

```sql
CREATE TABLE "hdfcbank_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
, "SMA_5" REAL, "SMA_10" REAL, "SMA_50" REAL, "SMA_100" REAL, "SMA_200" REAL, "EMA_9" REAL, "EMA_12" REAL, "EMA_20" REAL, "EMA_26" REAL, "EMA_50" REAL, "EMA_200" REAL, "WMA_20" REAL, "WMA_50" REAL, "DEMA_20" REAL, "TEMA_20" REAL, "TRIMA_20" REAL, "KAMA_20" REAL, "MAMA" REAL, "FAMA" REAL, "T3_20" REAL, "BB_UPPER" REAL, "BB_MIDDLE" REAL, "BB_LOWER" REAL, "SAR" REAL, "HT_TRENDLINE" REAL, "RSI_7" REAL, "RSI_21" REAL, "MACD" REAL, "MACD_SIGNAL" REAL, "MACD_HIST" REAL, "STOCH_K" REAL, "STOCH_D" REAL, "STOCHRSI_K" REAL, "STOCHRSI_D" REAL, "WILLR_14" REAL, "CCI_14" REAL, "CCI_20" REAL, "ROC_10" REAL, "ROC_20" REAL, "MOM_10" REAL, "ADX_14" REAL, "PLUS_DI" REAL, "MINUS_DI" REAL, "AROON_DOWN" REAL, "AROON_UP" REAL, "AROONOSC" REAL, "BOP" REAL, "ULTOSC" REAL, "MFI" REAL, "PPO" REAL, "TRIX" REAL, "OBV" REAL, "AD" REAL, "ADOSC" REAL, "VOLUME_SMA_10" REAL, "VOLUME_SMA_20" REAL, "VOLUME_SMA_50" REAL, "ATR_7" REAL, "ATR_14" REAL, "ATR_21" REAL, "NATR_14" REAL, "STDDEV_10" REAL, "STDDEV_20" REAL, "CDL_DOJI" INTEGER, "CDL_HAMMER" INTEGER, "CDL_SHOOTINGSTAR" INTEGER, "CDL_ENGULFING" INTEGER, "CDL_MORNINGSTAR" INTEGER, "CDL_EVENINGSTAR" INTEGER)
```

### Table: hdfclife_1d_ohlc

```sql
CREATE TABLE "hdfclife_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: heromotoco_1d_ohlc

```sql
CREATE TABLE "heromotoco_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: hindalco_1d_ohlc

```sql
CREATE TABLE "hindalco_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: hindunilvr_1d_ohlc

```sql
CREATE TABLE "hindunilvr_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: icicibank_1d_ohlc

```sql
CREATE TABLE "icicibank_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
, "SMA_5" REAL, "SMA_10" REAL, "SMA_50" REAL, "SMA_100" REAL, "SMA_200" REAL, "EMA_9" REAL, "EMA_12" REAL, "EMA_20" REAL, "EMA_26" REAL, "EMA_50" REAL, "EMA_200" REAL, "WMA_20" REAL, "WMA_50" REAL, "DEMA_20" REAL, "TEMA_20" REAL, "TRIMA_20" REAL, "KAMA_20" REAL, "MAMA" REAL, "FAMA" REAL, "T3_20" REAL, "BB_UPPER" REAL, "BB_MIDDLE" REAL, "BB_LOWER" REAL, "SAR" REAL, "HT_TRENDLINE" REAL, "RSI_7" REAL, "RSI_21" REAL, "MACD" REAL, "MACD_SIGNAL" REAL, "MACD_HIST" REAL, "STOCH_K" REAL, "STOCH_D" REAL, "STOCHRSI_K" REAL, "STOCHRSI_D" REAL, "WILLR_14" REAL, "CCI_14" REAL, "CCI_20" REAL, "ROC_10" REAL, "ROC_20" REAL, "MOM_10" REAL, "ADX_14" REAL, "PLUS_DI" REAL, "MINUS_DI" REAL, "AROON_DOWN" REAL, "AROON_UP" REAL, "AROONOSC" REAL, "BOP" REAL, "ULTOSC" REAL, "MFI" REAL, "PPO" REAL, "TRIX" REAL, "OBV" REAL, "AD" REAL, "ADOSC" REAL, "VOLUME_SMA_10" REAL, "VOLUME_SMA_20" REAL, "VOLUME_SMA_50" REAL, "ATR_7" REAL, "ATR_14" REAL, "ATR_21" REAL, "NATR_14" REAL, "STDDEV_10" REAL, "STDDEV_20" REAL, "CDL_DOJI" INTEGER, "CDL_HAMMER" INTEGER, "CDL_SHOOTINGSTAR" INTEGER, "CDL_ENGULFING" INTEGER, "CDL_MORNINGSTAR" INTEGER, "CDL_EVENINGSTAR" INTEGER)
```

### Table: itc_1d_ohlc

```sql
CREATE TABLE "itc_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: indusindbk_1d_ohlc

```sql
CREATE TABLE "indusindbk_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: infy_1d_ohlc

```sql
CREATE TABLE "infy_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
, "SMA_5" REAL, "SMA_10" REAL, "SMA_50" REAL, "SMA_100" REAL, "SMA_200" REAL, "EMA_9" REAL, "EMA_12" REAL, "EMA_20" REAL, "EMA_26" REAL, "EMA_50" REAL, "EMA_200" REAL, "WMA_20" REAL, "WMA_50" REAL, "DEMA_20" REAL, "TEMA_20" REAL, "TRIMA_20" REAL, "KAMA_20" REAL, "MAMA" REAL, "FAMA" REAL, "T3_20" REAL, "BB_UPPER" REAL, "BB_MIDDLE" REAL, "BB_LOWER" REAL, "SAR" REAL, "HT_TRENDLINE" REAL, "RSI_7" REAL, "RSI_21" REAL, "MACD" REAL, "MACD_SIGNAL" REAL, "MACD_HIST" REAL, "STOCH_K" REAL, "STOCH_D" REAL, "STOCHRSI_K" REAL, "STOCHRSI_D" REAL, "WILLR_14" REAL, "CCI_14" REAL, "CCI_20" REAL, "ROC_10" REAL, "ROC_20" REAL, "MOM_10" REAL, "ADX_14" REAL, "PLUS_DI" REAL, "MINUS_DI" REAL, "AROON_DOWN" REAL, "AROON_UP" REAL, "AROONOSC" REAL, "BOP" REAL, "ULTOSC" REAL, "MFI" REAL, "PPO" REAL, "TRIX" REAL, "OBV" REAL, "AD" REAL, "ADOSC" REAL, "VOLUME_SMA_10" REAL, "VOLUME_SMA_20" REAL, "VOLUME_SMA_50" REAL, "ATR_7" REAL, "ATR_14" REAL, "ATR_21" REAL, "NATR_14" REAL, "STDDEV_10" REAL, "STDDEV_20" REAL, "CDL_DOJI" INTEGER, "CDL_HAMMER" INTEGER, "CDL_SHOOTINGSTAR" INTEGER, "CDL_ENGULFING" INTEGER, "CDL_MORNINGSTAR" INTEGER, "CDL_EVENINGSTAR" INTEGER)
```

### Table: jswsteel_1d_ohlc

```sql
CREATE TABLE "jswsteel_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: jiofin_1d_ohlc

```sql
CREATE TABLE "jiofin_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
, "SMA_5" REAL, "SMA_10" REAL, "SMA_50" REAL, "SMA_100" REAL, "SMA_200" REAL, "EMA_9" REAL, "EMA_12" REAL, "EMA_20" REAL, "EMA_26" REAL, "EMA_50" REAL, "EMA_200" REAL, "WMA_20" REAL, "WMA_50" REAL, "DEMA_20" REAL, "TEMA_20" REAL, "TRIMA_20" REAL, "KAMA_20" REAL, "MAMA" REAL, "FAMA" REAL, "T3_20" REAL, "BB_UPPER" REAL, "BB_MIDDLE" REAL, "BB_LOWER" REAL, "SAR" REAL, "HT_TRENDLINE" REAL, "RSI_7" REAL, "RSI_21" REAL, "MACD" REAL, "MACD_SIGNAL" REAL, "MACD_HIST" REAL, "STOCH_K" REAL, "STOCH_D" REAL, "STOCHRSI_K" REAL, "STOCHRSI_D" REAL, "WILLR_14" REAL, "CCI_14" REAL, "CCI_20" REAL, "ROC_10" REAL, "ROC_20" REAL, "MOM_10" REAL, "ADX_14" REAL, "PLUS_DI" REAL, "MINUS_DI" REAL, "AROON_DOWN" REAL, "AROON_UP" REAL, "AROONOSC" REAL, "BOP" REAL, "ULTOSC" REAL, "MFI" REAL, "PPO" REAL, "TRIX" REAL, "OBV" REAL, "AD" REAL, "ADOSC" REAL, "VOLUME_SMA_10" REAL, "VOLUME_SMA_20" REAL, "VOLUME_SMA_50" REAL, "ATR_7" REAL, "ATR_14" REAL, "ATR_21" REAL, "NATR_14" REAL, "STDDEV_10" REAL, "STDDEV_20" REAL, "CDL_DOJI" INTEGER, "CDL_HAMMER" INTEGER, "CDL_SHOOTINGSTAR" INTEGER, "CDL_ENGULFING" INTEGER, "CDL_MORNINGSTAR" INTEGER, "CDL_EVENINGSTAR" INTEGER)
```

### Table: kotakbank_1d_ohlc

```sql
CREATE TABLE "kotakbank_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
, "SMA_5" REAL, "SMA_10" REAL, "SMA_50" REAL, "SMA_100" REAL, "SMA_200" REAL, "EMA_9" REAL, "EMA_12" REAL, "EMA_20" REAL, "EMA_26" REAL, "EMA_50" REAL, "EMA_200" REAL, "WMA_20" REAL, "WMA_50" REAL, "DEMA_20" REAL, "TEMA_20" REAL, "TRIMA_20" REAL, "KAMA_20" REAL, "MAMA" REAL, "FAMA" REAL, "T3_20" REAL, "BB_UPPER" REAL, "BB_MIDDLE" REAL, "BB_LOWER" REAL, "SAR" REAL, "HT_TRENDLINE" REAL, "RSI_7" REAL, "RSI_21" REAL, "MACD" REAL, "MACD_SIGNAL" REAL, "MACD_HIST" REAL, "STOCH_K" REAL, "STOCH_D" REAL, "STOCHRSI_K" REAL, "STOCHRSI_D" REAL, "WILLR_14" REAL, "CCI_14" REAL, "CCI_20" REAL, "ROC_10" REAL, "ROC_20" REAL, "MOM_10" REAL, "ADX_14" REAL, "PLUS_DI" REAL, "MINUS_DI" REAL, "AROON_DOWN" REAL, "AROON_UP" REAL, "AROONOSC" REAL, "BOP" REAL, "ULTOSC" REAL, "MFI" REAL, "PPO" REAL, "TRIX" REAL, "OBV" REAL, "AD" REAL, "ADOSC" REAL, "VOLUME_SMA_10" REAL, "VOLUME_SMA_20" REAL, "VOLUME_SMA_50" REAL, "ATR_7" REAL, "ATR_14" REAL, "ATR_21" REAL, "NATR_14" REAL, "STDDEV_10" REAL, "STDDEV_20" REAL, "CDL_DOJI" INTEGER, "CDL_HAMMER" INTEGER, "CDL_SHOOTINGSTAR" INTEGER, "CDL_ENGULFING" INTEGER, "CDL_MORNINGSTAR" INTEGER, "CDL_EVENINGSTAR" INTEGER)
```

### Table: lt_1d_ohlc

```sql
CREATE TABLE "lt_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: m_m_1d_ohlc

```sql
CREATE TABLE "m_m_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: maruti_1d_ohlc

```sql
CREATE TABLE "maruti_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: ntpc_1d_ohlc

```sql
CREATE TABLE "ntpc_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: nestleind_1d_ohlc

```sql
CREATE TABLE "nestleind_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: ongc_1d_ohlc

```sql
CREATE TABLE "ongc_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: powergrid_1d_ohlc

```sql
CREATE TABLE "powergrid_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: reliance_1d_ohlc

```sql
CREATE TABLE "reliance_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
, "SMA_5" REAL, "SMA_10" REAL, "SMA_50" REAL, "SMA_100" REAL, "SMA_200" REAL, "EMA_9" REAL, "EMA_12" REAL, "EMA_20" REAL, "EMA_26" REAL, "EMA_50" REAL, "EMA_200" REAL, "WMA_20" REAL, "WMA_50" REAL, "DEMA_20" REAL, "TEMA_20" REAL, "TRIMA_20" REAL, "KAMA_20" REAL, "MAMA" REAL, "FAMA" REAL, "T3_20" REAL, "BB_UPPER" REAL, "BB_MIDDLE" REAL, "BB_LOWER" REAL, "SAR" REAL, "HT_TRENDLINE" REAL, "RSI_7" REAL, "RSI_21" REAL, "MACD" REAL, "MACD_SIGNAL" REAL, "MACD_HIST" REAL, "STOCH_K" REAL, "STOCH_D" REAL, "STOCHRSI_K" REAL, "STOCHRSI_D" REAL, "WILLR_14" REAL, "CCI_14" REAL, "CCI_20" REAL, "ROC_10" REAL, "ROC_20" REAL, "MOM_10" REAL, "ADX_14" REAL, "PLUS_DI" REAL, "MINUS_DI" REAL, "AROON_DOWN" REAL, "AROON_UP" REAL, "AROONOSC" REAL, "BOP" REAL, "ULTOSC" REAL, "MFI" REAL, "PPO" REAL, "TRIX" REAL, "OBV" REAL, "AD" REAL, "ADOSC" REAL, "VOLUME_SMA_10" REAL, "VOLUME_SMA_20" REAL, "VOLUME_SMA_50" REAL, "ATR_7" REAL, "ATR_14" REAL, "ATR_21" REAL, "NATR_14" REAL, "STDDEV_10" REAL, "STDDEV_20" REAL, "CDL_DOJI" INTEGER, "CDL_HAMMER" INTEGER, "CDL_SHOOTINGSTAR" INTEGER, "CDL_ENGULFING" INTEGER, "CDL_MORNINGSTAR" INTEGER, "CDL_EVENINGSTAR" INTEGER)
```

### Table: sbilife_1d_ohlc

```sql
CREATE TABLE "sbilife_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: shriramfin_1d_ohlc

```sql
CREATE TABLE "shriramfin_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: sbin_1d_ohlc

```sql
CREATE TABLE "sbin_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
, "SMA_5" REAL, "SMA_10" REAL, "SMA_50" REAL, "SMA_100" REAL, "SMA_200" REAL, "EMA_9" REAL, "EMA_12" REAL, "EMA_20" REAL, "EMA_26" REAL, "EMA_50" REAL, "EMA_200" REAL, "WMA_20" REAL, "WMA_50" REAL, "DEMA_20" REAL, "TEMA_20" REAL, "TRIMA_20" REAL, "KAMA_20" REAL, "MAMA" REAL, "FAMA" REAL, "T3_20" REAL, "BB_UPPER" REAL, "BB_MIDDLE" REAL, "BB_LOWER" REAL, "SAR" REAL, "HT_TRENDLINE" REAL, "RSI_7" REAL, "RSI_21" REAL, "MACD" REAL, "MACD_SIGNAL" REAL, "MACD_HIST" REAL, "STOCH_K" REAL, "STOCH_D" REAL, "STOCHRSI_K" REAL, "STOCHRSI_D" REAL, "WILLR_14" REAL, "CCI_14" REAL, "CCI_20" REAL, "ROC_10" REAL, "ROC_20" REAL, "MOM_10" REAL, "ADX_14" REAL, "PLUS_DI" REAL, "MINUS_DI" REAL, "AROON_DOWN" REAL, "AROON_UP" REAL, "AROONOSC" REAL, "BOP" REAL, "ULTOSC" REAL, "MFI" REAL, "PPO" REAL, "TRIX" REAL, "OBV" REAL, "AD" REAL, "ADOSC" REAL, "VOLUME_SMA_10" REAL, "VOLUME_SMA_20" REAL, "VOLUME_SMA_50" REAL, "ATR_7" REAL, "ATR_14" REAL, "ATR_21" REAL, "NATR_14" REAL, "STDDEV_10" REAL, "STDDEV_20" REAL, "CDL_DOJI" INTEGER, "CDL_HAMMER" INTEGER, "CDL_SHOOTINGSTAR" INTEGER, "CDL_ENGULFING" INTEGER, "CDL_MORNINGSTAR" INTEGER, "CDL_EVENINGSTAR" INTEGER)
```

### Table: sunpharma_1d_ohlc

```sql
CREATE TABLE "sunpharma_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: tcs_1d_ohlc

```sql
CREATE TABLE "tcs_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
, "SMA_5" REAL, "SMA_10" REAL, "SMA_50" REAL, "SMA_100" REAL, "SMA_200" REAL, "EMA_9" REAL, "EMA_12" REAL, "EMA_20" REAL, "EMA_26" REAL, "EMA_50" REAL, "EMA_200" REAL, "WMA_20" REAL, "WMA_50" REAL, "DEMA_20" REAL, "TEMA_20" REAL, "TRIMA_20" REAL, "KAMA_20" REAL, "MAMA" REAL, "FAMA" REAL, "T3_20" REAL, "BB_UPPER" REAL, "BB_MIDDLE" REAL, "BB_LOWER" REAL, "SAR" REAL, "HT_TRENDLINE" REAL, "RSI_7" REAL, "RSI_21" REAL, "MACD" REAL, "MACD_SIGNAL" REAL, "MACD_HIST" REAL, "STOCH_K" REAL, "STOCH_D" REAL, "STOCHRSI_K" REAL, "STOCHRSI_D" REAL, "WILLR_14" REAL, "CCI_14" REAL, "CCI_20" REAL, "ROC_10" REAL, "ROC_20" REAL, "MOM_10" REAL, "ADX_14" REAL, "PLUS_DI" REAL, "MINUS_DI" REAL, "AROON_DOWN" REAL, "AROON_UP" REAL, "AROONOSC" REAL, "BOP" REAL, "ULTOSC" REAL, "MFI" REAL, "PPO" REAL, "TRIX" REAL, "OBV" REAL, "AD" REAL, "ADOSC" REAL, "VOLUME_SMA_10" REAL, "VOLUME_SMA_20" REAL, "VOLUME_SMA_50" REAL, "ATR_7" REAL, "ATR_14" REAL, "ATR_21" REAL, "NATR_14" REAL, "STDDEV_10" REAL, "STDDEV_20" REAL, "CDL_DOJI" INTEGER, "CDL_HAMMER" INTEGER, "CDL_SHOOTINGSTAR" INTEGER, "CDL_ENGULFING" INTEGER, "CDL_MORNINGSTAR" INTEGER, "CDL_EVENINGSTAR" INTEGER)
```

### Table: tataconsum_1d_ohlc

```sql
CREATE TABLE "tataconsum_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: tatamotors_1d_ohlc

```sql
CREATE TABLE "tatamotors_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: tatasteel_1d_ohlc

```sql
CREATE TABLE "tatasteel_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: techm_1d_ohlc

```sql
CREATE TABLE "techm_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: titan_1d_ohlc

```sql
CREATE TABLE "titan_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: trent_1d_ohlc

```sql
CREATE TABLE "trent_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: ultracemco_1d_ohlc

```sql
CREATE TABLE "ultracemco_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: wipro_1d_ohlc

```sql
CREATE TABLE "wipro_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: tcs_30m_ohlc

```sql
CREATE TABLE "tcs_30m_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: jio_1m_ohlc

```sql
CREATE TABLE "jio_1m_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: wipro_5m_ohlc

```sql
CREATE TABLE "wipro_5m_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: eil_1d_ohlc

```sql
CREATE TABLE "eil_1d_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: eil_10m_ohlc

```sql
CREATE TABLE "eil_10m_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: jio_1h_ohlc

```sql
CREATE TABLE "jio_1h_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: tcs_1m_ohlc

```sql
CREATE TABLE "tcs_1m_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: tcs_5m_ohlc

```sql
CREATE TABLE "tcs_5m_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: tcs_10m_ohlc

```sql
CREATE TABLE "tcs_10m_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
)
```

### Table: tcs_1h_ohlc

```sql
CREATE TABLE "tcs_1h_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_20" REAL,
  "RSI_14" REAL
, "SMA_5" REAL, "SMA_10" REAL, "SMA_50" REAL, "SMA_100" REAL, "SMA_200" REAL, "EMA_9" REAL, "EMA_12" REAL, "EMA_20" REAL, "EMA_26" REAL, "EMA_50" REAL, "EMA_200" REAL, "WMA_20" REAL, "WMA_50" REAL, "DEMA_20" REAL, "TEMA_20" REAL, "TRIMA_20" REAL, "KAMA_20" REAL, "MAMA" REAL, "FAMA" REAL, "T3_20" REAL, "BB_UPPER" REAL, "BB_MIDDLE" REAL, "BB_LOWER" REAL, "SAR" REAL, "HT_TRENDLINE" REAL, "RSI_7" REAL, "RSI_21" REAL, "MACD" REAL, "MACD_SIGNAL" REAL, "MACD_HIST" REAL, "STOCH_K" REAL, "STOCH_D" REAL, "STOCHRSI_K" REAL, "STOCHRSI_D" REAL, "WILLR_14" REAL, "CCI_14" REAL, "CCI_20" REAL, "ROC_10" REAL, "ROC_20" REAL, "MOM_10" REAL, "ADX_14" REAL, "PLUS_DI" REAL, "MINUS_DI" REAL, "AROON_DOWN" REAL, "AROON_UP" REAL, "AROONOSC" REAL, "BOP" REAL, "ULTOSC" REAL, "MFI" REAL, "PPO" REAL, "TRIX" REAL, "OBV" REAL, "AD" REAL, "ADOSC" REAL, "VOLUME_SMA_10" REAL, "VOLUME_SMA_20" REAL, "VOLUME_SMA_50" REAL, "ATR_7" REAL, "ATR_14" REAL, "ATR_21" REAL, "NATR_14" REAL, "STDDEV_10" REAL, "STDDEV_20" REAL, "CDL_DOJI" INTEGER, "CDL_HAMMER" INTEGER, "CDL_SHOOTINGSTAR" INTEGER, "CDL_ENGULFING" INTEGER, "CDL_MORNINGSTAR" INTEGER, "CDL_EVENINGSTAR" INTEGER)
```

### Table: market_fii_dii

```sql
CREATE TABLE "market_fii_dii" (
"category" TEXT,
  "date" TEXT,
  "buyValue" TEXT,
  "sellValue" TEXT,
  "netValue" TEXT
)
```

### Table: market_insider_trading

```sql
CREATE TABLE "market_insider_trading" (
"symbol" TEXT,
  "company" TEXT,
  "anex" TEXT,
  "acqName" TEXT,
  "date" TEXT,
  "pid" TEXT,
  "tkdAcqm" TEXT,
  "buyValue" TEXT,
  "sellValue" TEXT,
  "buyQuantity" TEXT,
  "sellquantity" TEXT,
  "secType" TEXT,
  "secAcq" TEXT,
  "did" TEXT,
  "tdpTransactionType" TEXT,
  "tdpDerivativeContractType" TEXT,
  "xbrl" TEXT,
  "personCategory" TEXT,
  "befAcqSharesNo" TEXT,
  "befAcqSharesPer" TEXT,
  "secVal" TEXT,
  "securitiesTypePost" TEXT,
  "afterAcqSharesNo" TEXT,
  "afterAcqSharesPer" TEXT,
  "acqfromDt" TEXT,
  "acqtoDt" TEXT,
  "intimDt" TEXT,
  "acqMode" TEXT,
  "derivativeType" TEXT,
  "exchange" TEXT,
  "remarks" TEXT
)
```

### Table: market_upcoming_results

```sql
CREATE TABLE "market_upcoming_results" (
"symbol" TEXT,
  "company" TEXT,
  "purpose" TEXT,
  "bm_desc" TEXT,
  "date" TEXT
)
```

### Table: market_bulk_deals

```sql
CREATE TABLE "market_bulk_deals" (
"BD_DT_DATE" TEXT,
  "BD_DT_ORDER" TEXT,
  "BD_SYMBOL" TEXT,
  "BD_SCRIP_NAME" TEXT,
  "BD_CLIENT_NAME" TEXT,
  "BD_BUY_SELL" TEXT,
  "BD_QTY_TRD" INTEGER,
  "BD_TP_WATP" REAL,
  "BD_REMARKS" TEXT
)
```

### Table: market_block_deals

```sql
CREATE TABLE "market_block_deals" (
"BD_DT_DATE" TEXT,
  "BD_DT_ORDER" TEXT,
  "BD_SYMBOL" TEXT,
  "BD_SCRIP_NAME" TEXT,
  "BD_CLIENT_NAME" TEXT,
  "BD_BUY_SELL" TEXT,
  "BD_QTY_TRD" INTEGER,
  "BD_TP_WATP" REAL,
  "BD_REMARKS" TEXT
)
```

### Table: market_corp_actions

```sql
CREATE TABLE "market_corp_actions" (
"symbol" TEXT,
  "series" TEXT,
  "ind" TEXT,
  "faceVal" TEXT,
  "subject" TEXT,
  "exDate" TEXT,
  "recDate" TEXT,
  "bcStartDate" TEXT,
  "bcEndDate" TEXT,
  "ndStartDate" TEXT,
  "comp" TEXT,
  "isin" TEXT,
  "ndEndDate" TEXT,
  "caBroadcastDate" TEXT
)
```

### Table: market_short_selling

```sql
CREATE TABLE "market_short_selling" (
"SS_DATE" TEXT,
  "SS_DATE_ORDER" TEXT,
  "SS_SYMBOL" TEXT,
  "SS_NAME" TEXT,
  "SS_QTY" INTEGER
)
```

### Table: ohlcv_metadata

```sql
CREATE TABLE ohlcv_metadata (
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    first_date TEXT,
                    last_date TEXT,
                    record_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, timeframe)
                )
```

### Table: tcs_1w_ohlc

```sql
CREATE TABLE "tcs_1w_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_5" REAL,
  "SMA_10" REAL,
  "SMA_20" REAL,
  "SMA_50" REAL,
  "SMA_100" REAL,
  "SMA_200" REAL,
  "EMA_9" REAL,
  "EMA_12" REAL,
  "EMA_20" REAL,
  "EMA_26" REAL,
  "EMA_50" REAL,
  "EMA_200" REAL,
  "WMA_20" REAL,
  "WMA_50" REAL,
  "DEMA_20" REAL,
  "TEMA_20" REAL,
  "TRIMA_20" REAL,
  "KAMA_20" REAL,
  "MAMA" REAL,
  "FAMA" REAL,
  "T3_20" REAL,
  "BB_UPPER" REAL,
  "BB_MIDDLE" REAL,
  "BB_LOWER" REAL,
  "SAR" REAL,
  "HT_TRENDLINE" REAL,
  "RSI_7" REAL,
  "RSI_14" REAL,
  "RSI_21" REAL,
  "MACD" REAL,
  "MACD_SIGNAL" REAL,
  "MACD_HIST" REAL,
  "STOCH_K" REAL,
  "STOCH_D" REAL,
  "STOCHRSI_K" REAL,
  "STOCHRSI_D" REAL,
  "WILLR_14" REAL,
  "CCI_14" REAL,
  "CCI_20" REAL,
  "ROC_10" REAL,
  "ROC_20" REAL,
  "MOM_10" REAL,
  "ADX_14" REAL,
  "PLUS_DI" REAL,
  "MINUS_DI" REAL,
  "AROON_DOWN" REAL,
  "AROON_UP" REAL,
  "AROONOSC" REAL,
  "BOP" REAL,
  "ULTOSC" REAL,
  "MFI" REAL,
  "PPO" REAL,
  "TRIX" REAL,
  "OBV" REAL,
  "AD" REAL,
  "ADOSC" REAL,
  "VOLUME_SMA_10" REAL,
  "VOLUME_SMA_20" REAL,
  "VOLUME_SMA_50" REAL,
  "ATR_7" REAL,
  "ATR_14" REAL,
  "ATR_21" REAL,
  "NATR_14" REAL,
  "STDDEV_10" REAL,
  "STDDEV_20" REAL,
  "CDL_DOJI" INTEGER,
  "CDL_HAMMER" INTEGER,
  "CDL_SHOOTINGSTAR" INTEGER,
  "CDL_ENGULFING" INTEGER,
  "CDL_MORNINGSTAR" INTEGER,
  "CDL_EVENINGSTAR" INTEGER
)
```

### Table: jiofin_1w_ohlc

```sql
CREATE TABLE "jiofin_1w_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_5" REAL,
  "SMA_10" REAL,
  "SMA_20" REAL,
  "SMA_50" REAL,
  "SMA_100" REAL,
  "SMA_200" REAL,
  "EMA_9" REAL,
  "EMA_12" REAL,
  "EMA_20" REAL,
  "EMA_26" REAL,
  "EMA_50" REAL,
  "EMA_200" REAL,
  "WMA_20" REAL,
  "WMA_50" REAL,
  "DEMA_20" REAL,
  "TEMA_20" REAL,
  "TRIMA_20" REAL,
  "KAMA_20" REAL,
  "MAMA" REAL,
  "FAMA" REAL,
  "T3_20" REAL,
  "BB_UPPER" REAL,
  "BB_MIDDLE" REAL,
  "BB_LOWER" REAL,
  "SAR" REAL,
  "HT_TRENDLINE" REAL,
  "RSI_7" REAL,
  "RSI_14" REAL,
  "RSI_21" REAL,
  "MACD" REAL,
  "MACD_SIGNAL" REAL,
  "MACD_HIST" REAL,
  "STOCH_K" REAL,
  "STOCH_D" REAL,
  "STOCHRSI_K" REAL,
  "STOCHRSI_D" REAL,
  "WILLR_14" REAL,
  "CCI_14" REAL,
  "CCI_20" REAL,
  "ROC_10" REAL,
  "ROC_20" REAL,
  "MOM_10" REAL,
  "ADX_14" REAL,
  "PLUS_DI" REAL,
  "MINUS_DI" REAL,
  "AROON_DOWN" REAL,
  "AROON_UP" REAL,
  "AROONOSC" REAL,
  "BOP" REAL,
  "ULTOSC" REAL,
  "MFI" REAL,
  "PPO" REAL,
  "TRIX" REAL,
  "OBV" REAL,
  "AD" REAL,
  "ADOSC" REAL,
  "VOLUME_SMA_10" REAL,
  "VOLUME_SMA_20" REAL,
  "VOLUME_SMA_50" REAL,
  "ATR_7" REAL,
  "ATR_14" REAL,
  "ATR_21" REAL,
  "NATR_14" REAL,
  "STDDEV_10" REAL,
  "STDDEV_20" REAL,
  "CDL_DOJI" INTEGER,
  "CDL_HAMMER" INTEGER,
  "CDL_SHOOTINGSTAR" INTEGER,
  "CDL_ENGULFING" INTEGER,
  "CDL_MORNINGSTAR" INTEGER,
  "CDL_EVENINGSTAR" INTEGER
)
```

### Table: jiofin_1h_ohlc

```sql
CREATE TABLE "jiofin_1h_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_5" REAL,
  "SMA_10" REAL,
  "SMA_20" REAL,
  "SMA_50" REAL,
  "SMA_100" REAL,
  "SMA_200" REAL,
  "EMA_9" REAL,
  "EMA_12" REAL,
  "EMA_20" REAL,
  "EMA_26" REAL,
  "EMA_50" REAL,
  "EMA_200" REAL,
  "WMA_20" REAL,
  "WMA_50" REAL,
  "DEMA_20" REAL,
  "TEMA_20" REAL,
  "TRIMA_20" REAL,
  "KAMA_20" REAL,
  "MAMA" REAL,
  "FAMA" REAL,
  "T3_20" REAL,
  "BB_UPPER" REAL,
  "BB_MIDDLE" REAL,
  "BB_LOWER" REAL,
  "SAR" REAL,
  "HT_TRENDLINE" REAL,
  "RSI_7" REAL,
  "RSI_14" REAL,
  "RSI_21" REAL,
  "MACD" REAL,
  "MACD_SIGNAL" REAL,
  "MACD_HIST" REAL,
  "STOCH_K" REAL,
  "STOCH_D" REAL,
  "STOCHRSI_K" REAL,
  "STOCHRSI_D" REAL,
  "WILLR_14" REAL,
  "CCI_14" REAL,
  "CCI_20" REAL,
  "ROC_10" REAL,
  "ROC_20" REAL,
  "MOM_10" REAL,
  "ADX_14" REAL,
  "PLUS_DI" REAL,
  "MINUS_DI" REAL,
  "AROON_DOWN" REAL,
  "AROON_UP" REAL,
  "AROONOSC" REAL,
  "BOP" REAL,
  "ULTOSC" REAL,
  "MFI" REAL,
  "PPO" REAL,
  "TRIX" REAL,
  "OBV" REAL,
  "AD" REAL,
  "ADOSC" REAL,
  "VOLUME_SMA_10" REAL,
  "VOLUME_SMA_20" REAL,
  "VOLUME_SMA_50" REAL,
  "ATR_7" REAL,
  "ATR_14" REAL,
  "ATR_21" REAL,
  "NATR_14" REAL,
  "STDDEV_10" REAL,
  "STDDEV_20" REAL,
  "CDL_DOJI" INTEGER,
  "CDL_HAMMER" INTEGER,
  "CDL_SHOOTINGSTAR" INTEGER,
  "CDL_ENGULFING" INTEGER,
  "CDL_MORNINGSTAR" INTEGER,
  "CDL_EVENINGSTAR" INTEGER
)
```

### Table: tcs_15m_ohlc

```sql
CREATE TABLE "tcs_15m_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_5" REAL,
  "SMA_10" REAL,
  "SMA_20" REAL,
  "SMA_50" REAL,
  "SMA_100" REAL,
  "SMA_200" REAL,
  "EMA_9" REAL,
  "EMA_12" REAL,
  "EMA_20" REAL,
  "EMA_26" REAL,
  "EMA_50" REAL,
  "EMA_200" REAL,
  "WMA_20" REAL,
  "WMA_50" REAL,
  "DEMA_20" REAL,
  "TEMA_20" REAL,
  "TRIMA_20" REAL,
  "KAMA_20" REAL,
  "MAMA" REAL,
  "FAMA" REAL,
  "T3_20" REAL,
  "BB_UPPER" REAL,
  "BB_MIDDLE" REAL,
  "BB_LOWER" REAL,
  "SAR" REAL,
  "HT_TRENDLINE" REAL,
  "RSI_7" REAL,
  "RSI_14" REAL,
  "RSI_21" REAL,
  "MACD" REAL,
  "MACD_SIGNAL" REAL,
  "MACD_HIST" REAL,
  "STOCH_K" REAL,
  "STOCH_D" REAL,
  "STOCHRSI_K" REAL,
  "STOCHRSI_D" REAL,
  "WILLR_14" REAL,
  "CCI_14" REAL,
  "CCI_20" REAL,
  "ROC_10" REAL,
  "ROC_20" REAL,
  "MOM_10" REAL,
  "ADX_14" REAL,
  "PLUS_DI" REAL,
  "MINUS_DI" REAL,
  "AROON_DOWN" REAL,
  "AROON_UP" REAL,
  "AROONOSC" REAL,
  "BOP" REAL,
  "ULTOSC" REAL,
  "MFI" REAL,
  "PPO" REAL,
  "TRIX" REAL,
  "OBV" REAL,
  "AD" REAL,
  "ADOSC" REAL,
  "VOLUME_SMA_10" REAL,
  "VOLUME_SMA_20" REAL,
  "VOLUME_SMA_50" REAL,
  "ATR_7" REAL,
  "ATR_14" REAL,
  "ATR_21" REAL,
  "NATR_14" REAL,
  "STDDEV_10" REAL,
  "STDDEV_20" REAL,
  "CDL_DOJI" INTEGER,
  "CDL_HAMMER" INTEGER,
  "CDL_SHOOTINGSTAR" INTEGER,
  "CDL_ENGULFING" INTEGER,
  "CDL_MORNINGSTAR" INTEGER,
  "CDL_EVENINGSTAR" INTEGER
)
```

### Table: jiofin_15m_ohlc

```sql
CREATE TABLE "jiofin_15m_ohlc" (
"datetime" TIMESTAMP,
  "Open" REAL,
  "High" REAL,
  "Low" REAL,
  "Close" REAL,
  "Volume" INTEGER,
  "SMA_5" REAL,
  "SMA_10" REAL,
  "SMA_20" REAL,
  "SMA_50" REAL,
  "SMA_100" REAL,
  "SMA_200" REAL,
  "EMA_9" REAL,
  "EMA_12" REAL,
  "EMA_20" REAL,
  "EMA_26" REAL,
  "EMA_50" REAL,
  "EMA_200" REAL,
  "WMA_20" REAL,
  "WMA_50" REAL,
  "DEMA_20" REAL,
  "TEMA_20" REAL,
  "TRIMA_20" REAL,
  "KAMA_20" REAL,
  "MAMA" REAL,
  "FAMA" REAL,
  "T3_20" REAL,
  "BB_UPPER" REAL,
  "BB_MIDDLE" REAL,
  "BB_LOWER" REAL,
  "SAR" REAL,
  "HT_TRENDLINE" REAL,
  "RSI_7" REAL,
  "RSI_14" REAL,
  "RSI_21" REAL,
  "MACD" REAL,
  "MACD_SIGNAL" REAL,
  "MACD_HIST" REAL,
  "STOCH_K" REAL,
  "STOCH_D" REAL,
  "STOCHRSI_K" REAL,
  "STOCHRSI_D" REAL,
  "WILLR_14" REAL,
  "CCI_14" REAL,
  "CCI_20" REAL,
  "ROC_10" REAL,
  "ROC_20" REAL,
  "MOM_10" REAL,
  "ADX_14" REAL,
  "PLUS_DI" REAL,
  "MINUS_DI" REAL,
  "AROON_DOWN" REAL,
  "AROON_UP" REAL,
  "AROONOSC" REAL,
  "BOP" REAL,
  "ULTOSC" REAL,
  "MFI" REAL,
  "PPO" REAL,
  "TRIX" REAL,
  "OBV" REAL,
  "AD" REAL,
  "ADOSC" REAL,
  "VOLUME_SMA_10" REAL,
  "VOLUME_SMA_20" REAL,
  "VOLUME_SMA_50" REAL,
  "ATR_7" REAL,
  "ATR_14" REAL,
  "ATR_21" REAL,
  "NATR_14" REAL,
  "STDDEV_10" REAL,
  "STDDEV_20" REAL,
  "CDL_DOJI" INTEGER,
  "CDL_HAMMER" INTEGER,
  "CDL_SHOOTINGSTAR" INTEGER,
  "CDL_ENGULFING" INTEGER,
  "CDL_MORNINGSTAR" INTEGER,
  "CDL_EVENINGSTAR" INTEGER
)
```

### Table: ml_predictions

```sql
CREATE TABLE ml_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    prediction_date TEXT NOT NULL,
                    predicted_class INTEGER NOT NULL,
                    confidence_down REAL,
                    confidence_neutral REAL,
                    confidence_up REAL,
                    actual_class INTEGER,
                    actual_return REAL,
                    is_correct INTEGER,
                    model_version TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timeframe, prediction_date)
                )
```

### Table: sqlite_sequence

```sql
CREATE TABLE sqlite_sequence(name,seq)
```

### Table: ml_model_performance

```sql
CREATE TABLE ml_model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    accuracy REAL,
                    precision_down REAL,
                    precision_neutral REAL,
                    precision_up REAL,
                    total_predictions INTEGER,
                    correct_predictions INTEGER,
                    evaluation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timeframe, model_version, evaluation_date)
                )
```

## Database: market.db

*No tables found.*

