# review_mcp/test.py

import json

from review_mcp.tools.review_project import review_project

result = review_project(
    r"D:\BMS_related_testing_data\bmsAlgo\soe"
)

print(json.dumps(result, indent=2))