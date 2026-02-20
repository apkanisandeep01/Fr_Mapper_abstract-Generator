import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="FR Unclaimed excels Mapper and Abstract Generator",
    page_icon="🥬",
    layout="wide")

st.title("🥬 FR Unclaimed data Mapper and Abstract Generator")

st.info(
    """
    📌 **Import Guidelines**

    1️⃣ Ensure that village names are spelled exactly the same in both FR and Bheema files. Even small differences will prevent proper mapping.  

    2️⃣ Upload only original (raw) Excel files. Do not edit, filter, or modify the files before uploading.  

    3️⃣ Accurate and complete data helps achieve maximum Aadhaar mapping results.  

    4️⃣ For best results, upload FR and Bheema files covering all villages of the Mandal. This improves mapping across the entire Mandal.
    """
)

st.markdown("<h2 style='font-weight:800;'>📂 Upload FR Files</h2>", unsafe_allow_html=True)
fr_files = st.file_uploader("", type="xlsx", accept_multiple_files=True, key="fr")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<h2 style='font-weight:800;'>📂 Upload Bheema Files</h2>", unsafe_allow_html=True)
bh_files = st.file_uploader("", type="xlsx", accept_multiple_files=True, key="bh")

# ==================================================
# FILE COUNT METRICS
# ==================================================
if fr_files or bh_files:
    col1, col2 = st.columns(2)
    col1.metric("📂 FR Files Uploaded", len(fr_files) if fr_files else 0)
    col2.metric("📂 Bheema Files Uploaded", len(bh_files) if bh_files else 0)

# ==================================================
# SAFE READER
# ==================================================
def safe_read_excel(file, required_columns=None):
    df = pd.read_excel(file)
    if required_columns:
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
    return df


if fr_files and bh_files:

    if len(fr_files) != len(bh_files):
        st.error("⚠️ Number of FR and Bheema files must be equal.")
        st.stop()

    try:
        df_fr = pd.concat([safe_read_excel(f) for f in fr_files], ignore_index=True)

        df_bh = pd.concat([
            safe_read_excel(
                f,
                required_columns=["VillName","PPBNO","FarmerName_Tel","FatherName_Tel","AadharId",
                    "MobileNo","EnrollmenStatus"]
            )
            for f in bh_files
        ], ignore_index=True)

        # ---------------- MERGE ----------------
        left_on = ["Village Name", "Farmer Name", "Identifier Name"]
        right_on = ["VillName", "FarmerName_Tel", "FatherName_Tel"]

        df_fr_merge = df_fr.copy()
        df_bh_merge = df_bh.copy()

        df_fr_merge[left_on] = df_fr_merge[left_on].astype(str).apply(lambda c: c.str.strip().str.lower())
        df_bh_merge[right_on] = df_bh_merge[right_on].astype(str).apply(lambda c: c.str.strip().str.lower())

        merged = df_fr_merge.merge(
            df_bh_merge,
            left_on=left_on,
            right_on=right_on,
            how="left"
        )

        # ---------------- DUPLICATE METRIC ----------------
        duplicate_count = merged.duplicated(
            subset=["Bucket ID", "Village LGD Code"]
        ).sum()

        st.metric("📊 Duplicate Records Found", duplicate_count)

        # ---------------- NULL SPLIT ----------------
        null_df = merged[merged["AadharId"].isna()].copy()
        non_null_df = merged[merged["AadharId"].notna()].copy()

        # ---------------- GROUP MAIN DATA ----------------
        grouped = non_null_df.groupby(
            ["Bucket ID", "Village LGD Code"]
        ).agg({
            "Village Name": lambda x: ", ".join(pd.unique(x.astype(str))),
            "Farmer Name": "last",
            "Identifier Name": "last",
            "Farmer Mobile Number": "last",
            "AadharId": "last",
            "MobileNo": "last",
            "PPBNO": "last",
            "Survey Number": lambda x: ", ".join(pd.unique(x.astype(str))),
            "Sub Survey Number": lambda x: ", ".join(pd.unique(x.astype(str))),
            "EnrollmenStatus": "last"
        }).reset_index()

        null_df = null_df.reindex(columns=grouped.columns)

        processed_df = pd.concat([grouped, null_df], axis=0, ignore_index=True)

        # ==================================================
        # AADHAAR GROUPING LOGIC
        # ==================================================
        aadhar_group = processed_df[processed_df["AadharId"].notna()].groupby("AadharId").agg(
            aggregated_ppbno=("PPBNO", lambda x: ", ".join(pd.unique(x.astype(str)))),
            vill_count=("Village Name", "count"),
            vill_bucket=("Village Name", lambda x: ", ".join(pd.unique(x.astype(str))))
        ).reset_index()

        # ==================================================
        # 🔥 NEW VILLAGE DISTRIBUTION METRICS
        # ==================================================
        st.markdown("### 📊 Aadhaar Village Distribution")

        aadhar_group["vill_category"] = aadhar_group["vill_count"].apply(
            lambda x: "4+" if x >= 4 else str(x)
        )

        vill_distribution = aadhar_group["vill_category"].value_counts()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Vill Count = 1", vill_distribution.get("1", 0))
        col2.metric("Vill Count = 2", vill_distribution.get("2", 0))
        col3.metric("Vill Count = 3", vill_distribution.get("3", 0))
        col4.metric("Vill Count ≥ 4", vill_distribution.get("4+", 0))

        # --------------------------------------------------
        # MERGE BACK
        # --------------------------------------------------
        processed_df = processed_df.merge(
            aadhar_group.drop(columns=["vill_category"]),
            on="AadharId",
            how="left"
        )

        processed_df.drop(columns=["Village LGD Code"], inplace=True)
        processed_df['Village Name']= processed_df['Village Name'].str.upper()
        processed_df['Farmer Name']= processed_df['Farmer Name'].str.upper()
        processed_df['Identifier Name']= processed_df['Identifier Name'].str.upper()
        processed_df['vill_bucket']= processed_df['vill_bucket'].str.upper()

        st.success("✅ Files processed successfully")
        st.dataframe(processed_df.head(10), use_container_width=True)

        # ---------------- DOWNLOAD ----------------
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            processed_df.to_excel(writer, index=False, sheet_name="Farmer_Report")

        st.download_button(
            "⬇️ Download Merged File",
            data=buffer.getvalue(),
            file_name="FR_Merged_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    except Exception:
        st.error("⚠️ Error processing files. Please check format and upload raw files only.")

st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:gray; font-size:14px;">
        Developed and maintained by <b>Sandeep Kumar</b><br>
        <a href="https://apkanisandeep01.github.io/my-portfolio/"
           target="_blank"
           style="color:#4a90e2; text-decoration:none;">
            Visit my portfolio
        </a>
    </div>
    """,
    unsafe_allow_html=True
)