# IDEEZA Analytics API

Powerful analytics APIs for tracking blog views, top performers, and performance trends.

---
## Installation

1. **Clone the repository**
```bash
git clone https://github.com/Alazar42/IDEEZA_TEST.git
````

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Apply migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Populate test data**

```bash
python test_populate_data.py
```

5. **(Optional) Create superuser**

```bash
python manage.py createsuperuser
```

6. **Run development server**

```bash
python manage.py runserver
```

# API Endpoints

## 1. **Blog Views Analytics**

**GET** `/analytics/blog-views/`

### Parameters

* **object_type**: `country` | `user`
* **range**: `day` | `week` | `month` | `year`
* **start_date**: `YYYY-MM-DD`
* **end_date**: `YYYY-MM-DD`
* **filters**: JSON list of filter objects

### Example Filter

```json
[
  {
    "field": "viewer_country",
    "operator": "eq",
    "value": "USA"
  }
]
```

---

## 2. **Top Analytics**

**GET** `/analytics/top/`

### Parameters

* **top**: `user` | `country` | `blog`
* **start_date**: `YYYY-MM-DD`
* **end_date**: `YYYY-MM-DD`

---

## 3. **Performance Analytics**

**GET** `/analytics/performance/`

### Parameters

* **compare**: `day` | `week` | `month` | `year`
* **user_id**: *(optional)* Filter by user
* **start_date**: `YYYY-MM-DD`
* **end_date**: `YYYY-MM-DD`

---

# Features

* ✅ Dynamic AND/OR filtering
* ✅ Optimized Django ORM (no N+1 queries)
* ✅ Time-series aggregation
* ✅ Growth percentage calculation
* ✅ Grouping by user, country, blog
* ✅ Top-N rankings
* ✅ Window functions for ranking
* ✅ DB-level indexes for fast queries

---

# Database Optimization

* Indexes on frequently queried fields
* `select_related` + `prefetch_related` used where needed
* Window functions for ranking queries
* Efficient aggregation for time-series and top-N

---

# Example API Usage

### Blog views by country (monthly)

```bash
curl "http://localhost:8000/analytics/blog-views/?object_type=country&range=month"
```

### Blog views with filters

```bash
curl "http://localhost:8000/analytics/blog-views/?object_type=user&range=week&filters=[{\"field\":\"viewer_country\",\"operator\":\"eq\",\"value\":\"USA\"}]"
```

### Top blogs

```bash
curl "http://localhost:8000/analytics/top/?top=blog"
```

### Performance comparison (monthly)

```bash
curl "http://localhost:8000/analytics/performance/?compare=month"
```
