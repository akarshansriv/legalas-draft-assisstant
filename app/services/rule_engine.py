import yaml


def get_required_sections(case_type):
    with open(f"rules/{case_type}.yaml") as f:
        rule_data = yaml.safe_load(f)
    return rule_data.get("required_sections", [])
