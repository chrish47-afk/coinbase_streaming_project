# Real-Time Streaming Pipeline:
## Kafka → parsedDF → parsedDFwithTimestamp → withWatermark → windowedAgg → Delta Table → Power BI

## Overview
This document outlines a real-time cryptocurrency streaming pipeline built using Coinbase's WebSocket API, Apache Kafka (via Azure Event Hubs), Azure Databricks, Delta Lake, and Power BI.

---

## Architecture Workflow

```
           +------------------+
           |  Coinbase WS API |
           +------------------+
                    ↓
         +---------------------+
         | Python Kafka Producer|
         +---------------------+
                    ↓
      +----------------------------+
      | Azure Event Hub / Kafka    |
      +----------------------------+
                    ↓
      +-----------------------------+
      | Azure Databricks readStream |
      | + Parse + Watermark + Agg   |
      +-----------------------------+
                    ↓
      +-----------------------+
      | Delta Lake Table      |
      +-----------------------+
                    ↓
      +-----------------------+
      | Power BI Dashboard    |
      +-----------------------+
```

---

## Components

### 1. **Data Source: Coinbase WebSocket API**
- Subscribes to live `ticker` updates for: `BTC-USD`, `ETH-USD`, `ADA-USD`
- Real-time JSON payload with fields like `price`, `product_id`, `time`

### 2. **Python Kafka Producer**
- Sends each WebSocket message to Azure Kafka (Event Hub)
- Topic: `chrish47`

### 3. **Azure Databricks: Structured Streaming**
- Reads from Kafka via `readStream`
- Parses JSON and converts `time` to `TimestampType`
- Applies watermark and windowed aggregations (as needed)
- Writes stream to a Delta Lake table (e.g., `coinbase_ticker_table`)

### 4. **Delta Table**
- Persistent store of real-time stream
- Format: Delta Lake (can be queried by SQL engines and Power BI)

### 5. **Power BI**
- Connects to Databricks SQL Endpoint or Synapse to read Delta tables
- Displays real-time or near-real-time dashboards

---

## Streaming vs. Batch

| Component                              | Mode                                               |
|----------------------------------------|----------------------------------------------------|
| WebSocket → Kafka                      | Streaming                                          |
| Kafka → Databricks via readStream      | Streaming                                          |
| Databricks → Delta Table (writeStream) | Streaming                                          |
| Power BI → Delta Table                 | Pseudo-real-time (DirectQuery or scheduled refresh)|

---

## Real-Time Behavior

### Data is Real-Time If:
- Python producer is running
- Databricks `writeStream` is running
- Power BI uses **DirectQuery** or **frequent refresh**

### Power BI Notes:
| Mode         | Behavior                                       |
|--------------|------------------------------------------------|
| Import       | Refreshes manually/scheduled                   |
| DirectQuery  | Queries SQL Warehouse live (1–5 min intervals) |

---

## Tips & Best Practices

### Watermarking & Windowing in Databricks
```scala
val parsedDF = rawDF
  .withColumn("event_time", to_timestamp($"time", "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"))
  .withWatermark("event_time", "10 minutes")
  .groupBy(window($"event_time", "1 minute"), $"product_id")
  .agg(avg($"price".cast("double")).alias("avg_price"))
```

### Suggested Power BI Visuals
- Line Chart: BTC/ETH/ADA price over time
- KPI Cards: Current price, 24h volume
- Table: Timestamped feed of recent updates

---

## Summary
I have built a fully functioning **real-time data pipeline** that:
- Streams from Coinbase → Kafka → Databricks
- Stores & transforms with Delta Lake
- Visualizes in Power BI in near real time

It’s scalable, modular, and production-grade with the ability to add more coins, windowed aggregations, alerting, or historical analysis.

---

Let us know if you'd like to:
- Add alerting (price spikes, volatility)
- Store historical Delta snapshots
- Connect multiple exchanges (Binance, etc.)


<details>
<summary><strong>Power BI Integration: Databricks SQL Endpoint</strong></summary>

# Step-by-Step: Databricks SQL Endpoint + Power BI

## Step 1: Start or Create a SQL Warehouse in Databricks
1. Go to your Databricks Workspace
2. In the left menu, click **SQL**
3. Click on **SQL Warehouses**
4. Either:
   - Start an existing warehouse, **OR**
   - Click **Create SQL Warehouse**:
     - Give it a name (e.g., `PowerBI Warehouse`)
     - Choose the smallest size to start
     - Set auto-stop to ~10–30 min (to avoid charges)
     - Click **Create**
5. Once it starts, **copy the JDBC/ODBC connection details** (you’ll need this for Power BI)

## Step 2: Create a Personal Access Token (if you don’t have one)
1. Click your profile icon (top right) → **User Settings**
2. Go to **Access Tokens**
3. Click **Generate New Token**
4. Name it `powerbi-access` (or whatever), click **Generate**
5. **Copy and save it** — you won’t see it again

## Step 3: Open Power BI → Get Data → Azure Databricks
1. Open **Power BI Desktop**
2. Click **Home → Get Data**
3. Search for and choose **Azure Databricks**
4. Click **Connect**
5. Paste your workspace URL:  
   Example: `https://<your-instance>.databricks.azure.com`
6. When prompted for authentication:
   - Choose **Personal Access Token**
   - Paste the token you copied earlier

## Step 4: Choose Catalog, Schema, and Table
1. After connecting, you’ll see a navigator window:
   - Choose the **Catalog** (e.g., `hive_metastore` or `your-org-catalog`)
   - Then the **Schema** (e.g., `default`)
   - Find and check the box for your Delta table: `coinbase_ticker_table`
2. Click **Load** (or **Transform Data** if you want to model it first)

</details>


---

## References
- [Coinbase WebSocket Authentication Documentation](https://docs.cdp.coinbase.com/exchange/docs/websocket-auth)
