# review_mcp/test.py

from review_mcp.tools.review_project import review_project

result = review_project(
    r"D:\BMS_related_testing_data\bmsAlgo\soe"
)

print(result.keys())
print(result["run_id"])
print(result["module_name"])
print(result["report"]["summary"])