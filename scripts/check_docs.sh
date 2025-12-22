#!/bin/bash

# 脚本说明: 从 docs.json 中提取所有 docs/ 开头的路径，检查对应的 .mdx 文件是否存在

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# docs.json 文件路径
DOCS_JSON="$SCRIPT_DIR/docs.json"

# 检查 docs.json 是否存在
if [ ! -f "$DOCS_JSON" ]; then
    echo "错误: 找不到 docs.json 文件"
    exit 1
fi

echo "开始检查文档文件..."
echo "================================"

# 使用 grep 提取所有 "docs/ 开头的路径，然后用 sed 清理
# 1. grep 查找包含 "docs/ 的行
# 2. grep -o 提取 "docs/......" 格式的内容
# 3. sed 移除引号和逗号
# 4. sort -u 去重并排序

missing_count=0
found_count=0

# 将结果存储到临时数组中以便统计
grep -o '"docs/[^"]*"' "$DOCS_JSON" | sed 's/"//g' | sed 's/,$//' | sort -u | while IFS= read -r doc_path; do
    # 添加 .mdx 扩展名
    mdx_file="$SCRIPT_DIR/${doc_path}.mdx"
    
    # 检查文件是否存在
    if [ ! -f "$mdx_file" ]; then
        echo "❌ 缺失: ${doc_path}.mdx"
        ((missing_count++))
    else
        ((found_count++))
    fi
done

echo "================================"
echo "📊 检查汇总"
echo "================================"
echo "总文件数: $((found_count + missing_count))"
echo "✅ 存在: ${found_count} 个"
echo "❌ 缺失: ${missing_count} 个"
if [ $missing_count -eq 0 ]; then
    echo ""
    echo "🎉 所有文档文件都存在！"
fi
echo "================================"
