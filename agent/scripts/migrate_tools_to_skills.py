#!/usr/bin/env python3
"""Migrate tool_description modules to skill format."""

import importlib
import os
import sys
import textwrap

# Ensure we can import biomni
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import yaml

# --- Configuration ---

MODULE_MAP = {
    'database': 'biodata_query',
    'genetics': 'genetics_analysis',
    'literature': 'literature_search',
}

# Modules to migrate (exclude support_tools, genomics)
MODULES = [
    'database', 'genetics', 'literature',
    'cell_biology', 'molecular_biology', 'immunology', 'pharmacology',
    'cancer_biology', 'biochemistry', 'bioengineering', 'bioimaging',
    'biophysics', 'glycoengineering', 'microbiology', 'pathology',
    'physiology', 'lab_automation', 'protocols', 'synthetic_biology',
    'systems_biology',
]

# Functions already in sgrna_design skill — skip these from genetics
SGRNA_FUNCTIONS = {'analyze_cas9_mutation_outcomes', 'analyze_crispr_genome_editing'}

SKILLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'skills')

# Category display names for descriptions
CATEGORY_DISPLAY = {
    'database': '生物数据库查询',
    'genetics': '遗传学分析',
    'literature': '文献检索',
    'cell_biology': '细胞生物学',
    'molecular_biology': '分子生物学',
    'immunology': '免疫学',
    'pharmacology': '药理学',
    'cancer_biology': '肿瘤生物学',
    'biochemistry': '生物化学',
    'bioengineering': '生物工程',
    'bioimaging': '生物成像',
    'biophysics': '生物物理学',
    'glycoengineering': '糖工程',
    'microbiology': '微生物学',
    'pathology': '病理学',
    'physiology': '生理学',
    'lab_automation': '实验室自动化',
    'protocols': '实验方案',
    'synthetic_biology': '合成生物学',
    'systems_biology': '系统生物学',
}


def make_display_name(skill_name):
    """Generate display name from skill name."""
    return skill_name.replace('_', ' ').title()


def make_triggers(module_name, tools):
    """Generate trigger keywords from module name and tool descriptions."""
    triggers = []
    cn = CATEGORY_DISPLAY.get(module_name, module_name)
    en = module_name.replace('_', ' ')

    triggers.append(cn)
    triggers.append(en)

    # Extract key terms from tool descriptions (first 3-5 words)
    seen = set()
    for t in tools:
        desc = t['description']
        # Take meaningful keywords from description
        words = desc.split()[:6]
        keyword = ' '.join(words).rstrip('.,;:')
        if keyword not in seen and len(keyword) > 10:
            seen.add(keyword)
            triggers.append(keyword)
        if len(triggers) >= 10:
            break

    return triggers


def make_skill_description(module_name, tools):
    """Generate skill description from tools."""
    cn = CATEGORY_DISPLAY.get(module_name, module_name)
    tool_names = [t['name'] for t in tools]
    brief_list = ', '.join(tool_names[:5])
    suffix = f' 等 {len(tool_names)} 个工具' if len(tool_names) > 5 else ''
    return f"{cn}工具集。提供 {brief_list}{suffix}。"


def build_tool_yaml(tool_desc, module_name):
    """Build tool YAML dict from a description dict."""
    data = {
        'name': tool_desc['name'],
        'display_name': tool_desc['name'].replace('_', ' ').title(),
        'description': tool_desc['description'],
        'parameters': {},
        'implementation': {
            'type': 'module_ref',
            'module': f'biomni.tool.{module_name}',
            'function': tool_desc['name'],
        },
    }

    if tool_desc.get('required_parameters'):
        data['parameters']['required'] = []
        for p in tool_desc['required_parameters']:
            param = {
                'name': p['name'],
                'type': p.get('type', 'str'),
                'description': p.get('description', ''),
            }
            data['parameters']['required'].append(param)

    if tool_desc.get('optional_parameters'):
        data['parameters']['optional'] = []
        for p in tool_desc['optional_parameters']:
            param = {
                'name': p['name'],
                'type': p.get('type', 'str'),
                'description': p.get('description', ''),
                'default': p.get('default'),
            }
            data['parameters']['optional'].append(param)

    # Add returns if present
    if tool_desc.get('returns'):
        data['returns'] = tool_desc['returns']
    else:
        data['returns'] = {'type': 'str', 'description': '工具执行结果'}

    return data


def build_skill_yaml(skill_name, module_name, tools):
    """Build skill.yaml dict."""
    return {
        'name': skill_name,
        'display_name': make_display_name(skill_name),
        'version': '1.0.0',
        'category': module_name,
        'description': make_skill_description(module_name, tools),
        'authors': [{'name': 'Biomni Team', 'role': 'maintainer'}],
        'license': 'CC BY 4.0',
        'commercial_use': True,
        'tools': [t['name'] for t in tools],
        'triggers': make_triggers(module_name, tools),
        'enabled': True,
        'dependencies': {
            'python_packages': [],
        },
        'implementation': {
            'type': 'module_ref',
            'module': f'biomni.tool.{module_name}',
        },
    }


def build_how_to(skill_name, module_name, tools):
    """Build how_to.md content."""
    cn = CATEGORY_DISPLAY.get(module_name, module_name)
    lines = [
        f'# {make_display_name(skill_name)}',
        '',
        f'{cn}工具集。',
        '',
        '## 可用工具',
        '',
    ]
    for t in tools:
        desc_short = t['description'][:80].rstrip('.,;: ')
        lines.append(f'- **{t["name"]}**: {desc_short}')

    lines.append('')
    lines.append('## 使用示例')
    lines.append('')
    if tools:
        first = tools[0]
        lines.append(f'调用 `{first["name"]}` 进行{cn}相关分析。')
    lines.append('')
    return '\n'.join(lines)


def migrate_module(module_name):
    """Migrate a single module to skill format."""
    skill_name = MODULE_MAP.get(module_name, module_name)
    skill_dir = os.path.join(SKILLS_DIR, skill_name)

    # Skip if already exists
    if os.path.exists(skill_dir):
        print(f'  SKIP {skill_name} (already exists)')
        return 0

    # Import descriptions
    mod = importlib.import_module(f'biomni.tool.tool_description.{module_name}')
    tools = list(mod.description)

    # For genetics, filter out sgrna functions
    if module_name == 'genetics':
        original_count = len(tools)
        tools = [t for t in tools if t['name'] not in SGRNA_FUNCTIONS]
        skipped = original_count - len(tools)
        if skipped:
            print(f'  Filtered {skipped} sgRNA functions from genetics')

    if not tools:
        print(f'  SKIP {skill_name} (no tools after filtering)')
        return 0

    # Create directories
    tools_dir = os.path.join(skill_dir, 'tools')
    os.makedirs(tools_dir, exist_ok=True)

    # Write skill.yaml
    skill_data = build_skill_yaml(skill_name, module_name, tools)
    with open(os.path.join(skill_dir, 'skill.yaml'), 'w') as f:
        yaml.dump(skill_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # Write how_to.md
    with open(os.path.join(skill_dir, 'how_to.md'), 'w') as f:
        f.write(build_how_to(skill_name, module_name, tools))

    # Write individual tool YAMLs
    for t in tools:
        tool_data = build_tool_yaml(t, module_name)
        tool_path = os.path.join(tools_dir, f'{t["name"]}.yaml')
        with open(tool_path, 'w') as f:
            yaml.dump(tool_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f'  OK {skill_name}: {len(tools)} tools')
    return len(tools)


def main():
    print(f'Skills directory: {os.path.abspath(SKILLS_DIR)}')
    print(f'Migrating {len(MODULES)} modules...\n')

    total_tools = 0
    total_skills = 0

    for module_name in MODULES:
        print(f'[{module_name}]')
        try:
            count = migrate_module(module_name)
            if count > 0:
                total_skills += 1
                total_tools += count
        except Exception as e:
            print(f'  ERROR: {e}')

    print(f'\n=== Done ===')
    print(f'Skills created: {total_skills}')
    print(f'Total tools: {total_tools}')


if __name__ == '__main__':
    main()
