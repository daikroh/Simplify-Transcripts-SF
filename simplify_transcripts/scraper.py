from datetime import datetime

view_ids = {
    10: "Board of Supervisors",
    207: "Board of Supervisors Budget and Appropriations Committee",
    7: "Board of Supervisors Budget & Finance Committee",
    11: "Board of Supervisors Government Audit and Oversight Committee",
    225: "BOS Homelessness and Behavioral Health Select Committee",
    177: "Board of Supervisors Land Use and Transportation Committee",
    178: "BOS Public Safety and Neighborhood Services Committee",
    13: "Board of Supervisors Rules Committee",
    190: "Board of Supervisors Budget & Finance Federal Select Committee",
    189: "Board of Supervisors Budget & Finance Sub-Committee",
    8: "Board of Supervisors City Operations & Neighborhood Services Committee",
    # Finish list at some point
}

# Parse from website that has data stored as "07/29/25"
# Append the 2025
date_obj = datetime(2025, 7, 29)
print(date_obj)
