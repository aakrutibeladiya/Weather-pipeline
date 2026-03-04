## 🌦️ Weather Data Pipeline — Project Overview

### What You'll Build
An end-to-end pipeline that ingests live weather data, streams it through Kafka, orchestrates with Airflow, stores on AWS, and transforms with dbt — all running in Docker containers.

---

## 🏗️ Architecture

```
[Open-Meteo API] → [Kafka Producer] → [Kafka Topic: weather-raw]
                                              ↓
                                    [Kafka Consumer]
                                              ↓
                                         [AWS S3]  ← raw JSON files
                                              ↓
                                    [Redshift Serverless]
                                              ↓
                                           [dbt]
                                              ↓
                               [daily_weather_summary table] ✅

All orchestrated by → Apache Airflow (running in Docker)
```

---

## 🧱 Tech Stack

| Layer | Tool | AWS Free Tier? |
|---|---|---|
| Data Source | Open-Meteo API | ✅ Free, no key needed |
| Streaming | Apache Kafka + Zookeeper | ✅ Local in Docker |
| Orchestration | Apache Airflow | ✅ Local in Docker |
| Raw Storage | AWS S3 | ✅ 5GB free |
| Data Warehouse | AWS Redshift Serverless | ✅ 300 RPU-hrs trial |
| Transformation | dbt Core | ✅ Open source |
| Containers | Docker Compose | ✅ Free |

---

## 📁 Project Structure

```
weather-pipeline/
├── docker-compose.yml         # Kafka + Zookeeper + Airflow
├── airflow/
│   └── dags/
│       └── weather_pipeline_dag.py
├── kafka/
│   ├── producer.py            # API → Kafka
│   └── consumer.py            # Kafka → S3
├── dbt/
│   └── models/
│       ├── staging/stg_weather_raw.sql
│       └── marts/daily_weather_summary.sql
├── scripts/
│   └── create_redshift_tables.sql
└── .env                       # AWS credentials (never commit!)
```

---

## 🚀 4-Week Build Plan

### Week 1 — Infrastructure
- Create AWS account, S3 bucket (`weather-pipeline-raw`), and Redshift Serverless workgroup
- Set up Docker Compose with Kafka, Zookeeper, and Airflow
- Verify Airflow UI loads at `http://localhost:8080`

### Week 2 — Kafka Streaming
**Producer** fetches weather for 3 cities (London, NYC, Tokyo) from Open-Meteo every 15 mins and publishes JSON to a `weather-raw` Kafka topic.

**Consumer** reads that topic and writes partitioned JSON files to S3:
```
s3://weather-pipeline-raw/raw/city=london/date=2025-03-04/1234567.json
```

### Week 3 — Airflow Orchestration
A DAG with 3 tasks running every 15 minutes:
```
fetch_and_stream → consume_to_s3 → run_dbt
```
You'll learn: DAG definition, BashOperator, scheduling, monitoring task logs.

### Week 4 — dbt Transformations
Two models:

**Staging** (`stg_weather_raw`) — cleans raw data, decodes weather codes into readable descriptions (e.g. `weathercode=61` → `"Rainy"`).

**Mart** (`daily_weather_summary`) — aggregates per city per day:
```sql
SELECT city, DATE(event_time), AVG(temperature_c), MAX(temperature_c), COUNT(*) ...
```
Run `dbt run` → `dbt test` → `dbt docs serve` to see auto-generated docs.

---

## ✅ Key Learning Milestones

- [ ] Docker Compose starts all services cleanly
- [ ] Messages flow from API → Kafka → S3 (check the S3 console!)
- [ ] Airflow DAG shows all green tasks
- [ ] dbt models appear as tables in Redshift
- [ ] You can write a SQL query against `daily_weather_summary`

---

## 💡 Stretch Goals (Once Core is Done)

1. **Add dbt tests** (`not_null`, `unique`) — learn data quality
2. **Kafka Schema Registry + Avro** — learn schema evolution
3. **AWS QuickSight dashboard** — visualise your data (free tier)
4. **GitHub Actions CI/CD** — auto-run `dbt test` on every push
5. **Dead-letter queue** — handle malformed Kafka messages gracefully

---

## 🐛 Top Beginner Gotchas to Watch For

1. **Kafka "connection refused"** → Zookeeper must be healthy before Kafka starts — use Docker health checks
2. **S3 Access Denied** → IAM policy must be *attached* to your user, not just created
3. **Redshift can't connect** → Open port `5439` in your VPC security group for your IP
4. **dbt run fails** → Check `profiles.yml` — Redshift host, database, and schema must match exactly
5. **Airflow task fails silently** → Always read the task log in the Airflow UI, not just the terminal

---

## 📚 Free Resources to Get Started

- **Open-Meteo API docs**: open-meteo.com (no signup needed)
- **Kafka Quickstart**: kafka.apache.org/quickstart
- **dbt Introduction**: docs.getdbt.com
- **Airflow Tutorial**: airflow.apache.org/docs/apache-airflow/stable/tutorial

---

**Estimated cost: $0** within AWS Free Tier limits | **Time: ~2–3 hrs/day for 4 weeks**

Want me to generate the actual **code files** (docker-compose, producer, consumer, DAG, dbt models) ready to clone and run?