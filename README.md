# 🌾 FR Unclaimed Data Mapper & Abstract Generator

A Streamlit-based web application designed to merge FR (Unclaimed) data with Bheema data to maximize Aadhaar mapping, detect duplicates, and generate clean abstract reports.

Developed and maintained by **Sandeep Kumar**

---

## 📌 Overview

This application:

* Merges FR and Bheema Excel files
* Maps Aadhaar details using village + farmer identifiers
* Detects duplicate Aadhaar entries
* Aggregates PPBNO values
* Generates village-level and Aadhaar-level summaries
* Produces a clean downloadable Excel report

Designed specifically for agricultural administrative workflows.

---

## 🚀 Features

### ✅ File Validation

* Ensures equal number of FR and Bheema files
* Validates required Bheema columns
* Handles errors gracefully

### ✅ Intelligent Mapping

* Case-insensitive village + farmer name matching
* Trims whitespace before merge
* Preserves raw uploaded data

### ✅ Duplicate Detection

* Detects duplicate Bucket ID + Village LGD combinations
* Detects Aadhaar appearing in multiple villages
* Displays Aadhaar village distribution:

  * Appearing in 1 village
  * Appearing in 2 villages
  * Appearing in 3 villages
  * Appearing in 4+ villages

### ✅ Aadhaar-Level Aggregation

* Aggregated PPBNO values
* Village bucket summary
* Village count per Aadhaar

### ✅ Clean Output

* Structured downloadable Excel file
* Proper grouping logic
* Null-safe handling
* No column duplication

---

## 📊 Metrics Displayed in App

* Number of FR files uploaded
* Number of Bheema files uploaded
* Duplicate records found
* Aadhaar village distribution (1, 2, 3, 4+)

---

## 🗂 Required Columns (Bheema Files)

The Bheema Excel file must contain:

* `VillName`
* `PPBNO`
* `FarmerName_Tel`
* `FatherName_Tel`
* `AadharId`
* `MobileNo`
* `EnrollmenStatus`

---

## ⚠️ Import Guidelines

1. Ensure village names are spelled exactly the same in both FR and Bheema files.
2. Upload original (raw) Excel files only.
3. Accurate and complete data improves Aadhaar mapping results.
4. Upload FR and Bheema files covering all villages of the Mandal for maximum mapping coverage.

---

## 🛠 Tech Stack

* Python
* Streamlit
* Pandas
* XlsxWriter

---

## 📦 Installation

Clone the repository:

```
git clone https://github.com/yourusername/fr-unclaimed-mapper.git
cd fr-unclaimed-mapper
```

Create a virtual environment (recommended):

**Windows**

```
python -m venv venv
venv\Scripts\activate
```

**Mac / Linux**

```
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## ▶️ Run the Application

```
streamlit run app.py
```

---

## 📁 Project Structure

```
.
├── app.py
├── requirements.txt
├── README.md
```

---

## 📈 Future Enhancements

* Mandal-level analytics dashboard
* Village mismatch detailed report
* Duplicate Aadhaar export sheet
* Performance optimization for large datasets
* Database integration
* Role-based access control

---

## 👨‍💻 Author

**Sandeep Kumar**
Agriculture Extension Officer
Government of Telangana

🌐 Portfolio:
[https://apkanisandeep01.github.io/my-portfolio/](https://apkanisandeep01.github.io/my-portfolio/)

---
