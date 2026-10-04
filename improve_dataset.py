import pandas as pd

# Original dataset
input_file = "database/IntelliVision_500_Complaints_Dataset.csv"

# New improved dataset
output_file = "database/IntelliVision_Improved_Complaints_Dataset.csv"

# Load original dataset
df = pd.read_csv(input_file)

# Additional clear Vehicle Theft examples
vehicle_theft = [
    "My motorcycle was stolen from outside my house.",
    "Someone stole my scooter from the parking area.",
    "My car was stolen while it was parked outside the shopping mall.",
    "My bike was stolen from the college parking lot.",
    "Someone took my motorcycle without my permission.",
    "I parked my scooter near the railway station and it was missing when I returned.",
    "My vehicle was stolen from outside my residence.",
    "Someone stole my car from the parking area during the night.",
    "My motorcycle is missing from the place where I parked it.",
    "A person stole my scooter from outside my office.",
    "My bicycle was stolen from the apartment parking area.",
    "Someone took my bike while it was parked near the market.",
    "My motorcycle disappeared from the parking lot.",
    "My scooter was stolen from in front of my house.",
    "Someone stole my vehicle while I was inside a shop."
]

new_rows = []

for complaint in vehicle_theft:
    new_rows.append({
        "Complaint_ID": "VT_NEW",
        "Complaint_Text": complaint,
        "Crime_Type": "Vehicle Theft",
        "Location": "Unknown",
        "Complaint_Date": "",
        "Victim_Age": "",
        "Gender": "",
        "Description": complaint,
        "BNS_Section": "BNS 303",
        "Severity": "High",
        "Extracted_Entities": "Vehicle",
        "Status": "Pending"
    })

# Add new examples
new_df = pd.DataFrame(new_rows)

improved_df = pd.concat(
    [df, new_df],
    ignore_index=True
)

# Save new dataset
improved_df.to_csv(output_file, index=False)

print("===================================")
print("IMPROVED DATASET CREATED")
print("===================================")
print("Original records:", len(df))
print("New Vehicle Theft records:", len(new_df))
print("Total records:", len(improved_df))
print()
print("Saved as:")
print(output_file)