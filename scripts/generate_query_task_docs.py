#!/usr/bin/env python3
"""
自动化生成和管理 query-task 文档
功能：
1. 扫描 docs/api 目录下所有模型
2. 为每个模型的每个格式目录生成 query-task.mdx（如果不存在）
3. 自动从路径提取模型名称并设置 title
4. 将 query-task 页面添加到 docs.json 导航
5. 所有文档都引用共享的 snippet
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

# ========== 配置 ==========
QUERY_TASK_TEMPLATE = """---
title: '{model_name} (query task)'
sidebarTitle: 'Query Task'
api: 'GET /api/v3/predictions/${{requestId}}/result'
description: 'Query Task'
mode: 'wide'
---

import QueryTaskContent from '/snippets/query-task-content.mdx';

<QueryTaskContent />
"""

SNIPPET_CONTENT = """Gptproto's GPTProto format for the query task API.




<CodeGroup>

```bash cURL
curl -X GET "https://gptproto.com/api/v3/predictions/{task_id}/result" \\
  -H "Authorization: sk-***********" \\
  -H "Content-Type: application/json"
```

```python Python
import requests
import json

url = "https://gptproto.com/api/v3/predictions/{task_id}/result"
headers = {
    "Authorization": "sk-***********",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
result = response.json()
print(json.dumps(result, indent=2))
```

```javascript JavaScript
const url = "https://gptproto.com/api/v3/predictions/{task_id}/result";
const headers = {
  "Authorization": "sk-***********",
  "Content-Type": "application/json"
};

fetch(url, {
  method: "GET",
  headers: headers
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error("Error:", error));
```

```go Go
package main

import (
    "encoding/json"
    "fmt"
    "io/ioutil"
    "net/http"
)

func main() {
    url := "https://gptproto.com/api/v3/predictions/{task_id}/result"

    req, _ := http.NewRequest("GET", url, nil)
    req.Header.Set("Authorization", "sk-***********")
    req.Header.Set("Content-Type", "application/json")

    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()

    body, _ := ioutil.ReadAll(resp.Body)
    fmt.Println(string(body))
}
```
</CodeGroup>

<CodeGroup>

```json 200 - Success
{
  "status": "success",
  "result": {}
}
```

```json 401 - Invalid signature
{
  "error": {
    "message": "Invalid signature",
    "type": "401"
  }
}
```



```json 403 - Insufficient balance
{
  "error": {
    "message": "Insufficient balance",
    "type": "403"
  }
}
```

```json 500 - Internal server error
{
  "error": {
    "message": "Internal server error",
    "type": "500"
  }
}
```

```json 503 - Content policy violation
{
  "error": {
    "message": "Input may not meet the guidelines. Please adjust and try again.",
    "type": "503"
  }
}
```
</CodeGroup>

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `Authorization` (Header) | string | ✅ Yes | - | Your API key in the format: `sk-***********` |
| `task_id` (Path) | string | ✅ Yes | - | The task ID returned from the generation request |
"""

# ========== 工具函数 ==========

def extract_model_name_from_path(file_path: Path) -> str:
    """
    从文件路径提取模型名称
    例如: docs/api/Google/veo3/gptproto-format -> veo3
    """
    parts = file_path.parts
    try:
        api_index = parts.index('api')
        # 模型名称在 api/{Provider}/{ModelName}/{Format}
        if len(parts) > api_index + 2:
            return parts[api_index + 2]
    except (ValueError, IndexError):
        pass
    return "model"

def ensure_snippet_exists(snippets_dir: Path) -> bool:
    """确保 snippet 文件存在"""
    snippet_file = snippets_dir / "query-task-content.mdx"

    if snippet_file.exists():
        print(f"  ✓ Snippet 已存在: {snippet_file}")
        return True

    # 创建 snippets 目录
    snippets_dir.mkdir(parents=True, exist_ok=True)

    # 创建 snippet 文件
    with open(snippet_file, 'w', encoding='utf-8') as f:
        f.write(SNIPPET_CONTENT)

    print(f"  ✓ 已创建 snippet: {snippet_file}")
    return True

def find_format_directories(docs_api_dir: Path) -> List[Path]:
    """
    查找所有格式目录（gptproto-format, official-format 等）
    返回所有包含其他 .mdx 文件的格式目录
    """
    format_dirs = []

    # 常见的格式目录名称
    format_patterns = [
        '*-format',
        '*-format(*)',
        'gptproto-format',
        'official-format',
        'openai-format',
    ]

    for pattern in format_patterns:
        for format_dir in docs_api_dir.glob(f'**/{pattern}'):
            if format_dir.is_dir():
                # 检查是否已有其他 .mdx 文件（排除 query-task.mdx）
                mdx_files = [f for f in format_dir.glob('*.mdx')
                            if f.name != 'query-task.mdx']
                if mdx_files:
                    format_dirs.append(format_dir)

    return sorted(set(format_dirs))

def create_query_task_file(format_dir: Path, model_name: str) -> Tuple[bool, str]:
    """在指定的格式目录中创建 query-task.mdx 文件"""
    query_task_file = format_dir / "query-task.mdx"

    # 如果文件已存在，检查是否需要更新 title
    if query_task_file.exists():
        with open(query_task_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查 title 是否正确
        title_match = re.search(r"^title:\s*['\"]([^'\"]+)['\"]", content, re.MULTILINE)
        expected_title = f"{model_name} (query task)"

        if title_match and title_match.group(1) != expected_title:
            # 更新 title
            content = re.sub(
                r"^title:\s*['\"]([^'\"]+)['\"]",
                f"title: '{expected_title}'",
                content,
                count=1,
                flags=re.MULTILINE
            )
            with open(query_task_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "updated_title"

        return True, "exists"

    # 创建新文件
    content = QUERY_TASK_TEMPLATE.format(model_name=model_name)
    with open(query_task_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return True, "created"

def get_parent_path(file_path: str) -> str:
    """获取文件的父目录路径"""
    parts = file_path.split('/')
    return '/'.join(parts[:-1])

def add_to_docs_json_navigation(docs_config: Dict[str, Any], query_task_path: str) -> bool:
    """将 query-task 页面添加到 docs.json 的导航中"""
    parent_path = get_parent_path(query_task_path)

    def process_group(group: Dict[str, Any]) -> bool:
        """递归处理 group"""
        if 'pages' not in group or not isinstance(group['pages'], list):
            return False

        # 检查这个 group 是否包含同目录的其他页面
        has_same_dir = False
        already_has_query_task = False

        for page in group['pages']:
            if isinstance(page, str):
                if get_parent_path(page) == parent_path:
                    if 'query-task' in page:
                        already_has_query_task = True
                    else:
                        has_same_dir = True
            elif isinstance(page, dict) and 'group' in page:
                if process_group(page):
                    return True

        # 如果有同目录页面且还没有 query-task，则添加
        if has_same_dir and not already_has_query_task:
            group['pages'].append(query_task_path)
            return True

        return False

    # 遍历所有 tabs 和 groups
    if 'navigation' in docs_config and 'tabs' in docs_config['navigation']:
        for tab in docs_config['navigation']['tabs']:
            if 'groups' in tab:
                for group in tab['groups']:
                    if process_group(group):
                        return True

    return False

def update_docs_json(docs_json_path: Path, query_task_files: List[str]) -> Tuple[int, int]:
    """更新 docs.json，添加所有 query-task 页面"""

    # 读取 docs.json
    with open(docs_json_path, 'r', encoding='utf-8') as f:
        docs_config = json.load(f)

    # 备份
    backup_path = docs_json_path.with_suffix('.json.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(docs_config, f, indent=4, ensure_ascii=False)

    added_count = 0
    skipped_count = 0

    for query_task_path in query_task_files:
        if add_to_docs_json_navigation(docs_config, query_task_path):
            added_count += 1
        else:
            skipped_count += 1

    # 写回 docs.json
    with open(docs_json_path, 'w', encoding='utf-8') as f:
        json.dump(docs_config, f, indent=4, ensure_ascii=False)

    return added_count, skipped_count

# ========== 主函数 ==========

def main():
    # 获取项目路径
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_api_dir = project_root / "docs" / "api"
    snippets_dir = project_root / "snippets"
    docs_json_path = project_root / "docs.json"

    print("=" * 70)
    print("自动化生成和管理 Query Task 文档")
    print("=" * 70)

    # 1. 确保 snippet 存在
    print("\n📝 步骤 1: 检查/创建共享 snippet")
    ensure_snippet_exists(snippets_dir)

    # 2. 扫描所有格式目录
    print("\n🔍 步骤 2: 扫描模型格式目录")
    format_dirs = find_format_directories(docs_api_dir)
    print(f"  找到 {len(format_dirs)} 个格式目录")

    # 3. 为每个目录生成/更新 query-task.mdx
    print("\n📄 步骤 3: 生成/更新 query-task.mdx 文件")
    created_count = 0
    updated_count = 0
    skipped_count = 0
    query_task_files = []

    for format_dir in format_dirs:
        model_name = extract_model_name_from_path(format_dir)
        rel_path = format_dir.relative_to(project_root)

        success, status = create_query_task_file(format_dir, model_name)

        if success:
            query_task_file = format_dir / "query-task.mdx"
            # 转换为相对于项目根目录的路径，不带 .mdx
            doc_path = str(query_task_file.relative_to(project_root)).replace('.mdx', '')
            query_task_files.append(doc_path)

            if status == "created":
                print(f"  ✓ 已创建: {rel_path}/query-task.mdx (模型: {model_name})")
                created_count += 1
            elif status == "updated_title":
                print(f"  ✓ 已更新标题: {rel_path}/query-task.mdx (模型: {model_name})")
                updated_count += 1
            else:
                skipped_count += 1

    print(f"\n  创建: {created_count} 个")
    print(f"  更新: {updated_count} 个")
    print(f"  跳过: {skipped_count} 个（已存在且正确）")

    # 4. 更新 docs.json
    print("\n📋 步骤 4: 更新 docs.json 导航配置")
    if docs_json_path.exists():
        added, skipped = update_docs_json(docs_json_path, query_task_files)
        print(f"  添加到导航: {added} 个")
        print(f"  已存在: {skipped} 个")
        print(f"  备份已保存: docs.json.backup")
    else:
        print(f"  ⚠️  警告: docs.json 不存在")

    # 5. 总结
    print("\n" + "=" * 70)
    print("✅ 完成！")
    print("=" * 70)
    print(f"\n总计:")
    print(f"  • 找到 {len(format_dirs)} 个格式目录")
    print(f"  • 创建 {created_count} 个新文档")
    print(f"  • 更新 {updated_count} 个文档标题")
    print(f"  • 所有文档都引用共享 snippet: snippets/query-task-content.mdx")
    print(f"\n💡 提示: 运行 'mintlify dev' 查看效果")
    print("=" * 70)

if __name__ == "__main__":
    main()
