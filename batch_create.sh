#!/bin/bash

# 定义变量(g固定)
BASE_DIR="docs/allapi"

# 厂商数组
# Alibaba
# Claude
# DeepSeek
# Doubao
# Flux
# Google
# Gptproto
# Grok
# Higgsfield
# Ideogram
# Kling
# Midjourney
# MiniMax
# NovelAI
# OpenAI
# Runway
# Suno
# Tripo3d
VENDORS=("Alibaba" "Claude" )

# 模型数组
MODELS=("model-1" "model-2" "model-3")

# 格式数组
# official-format
# openai-format
# reverse-format
# gptproto-format
FORMATS=("json" "xml" "yaml" "mdx")

# 场景数组
# kv={
#   "text-to-text": "Text to Text",
#   "text-to-image": "Text to Image",
#   "image-to-image": "Image to Image",
#   "text-to-video": "Text to Video",
#   "text-to-audio": "Text to Audio",
#   "image-to-text": "Image To Text",
#   "image-edit": "Image Edit",
#   "image-to-video": "Image to Video",
#   "reference-to-video": "Reference to Video",
#   "video-to-video": "Video To Video",
#   "image-to-3d": "Image to 3d",
#   "start-end-framed": "Start End Frame",
#   "web-search": "Web Search",
#   "file-analysis": "File analysis"
# }
SCENARIOS=()

# 批量创建文件夹和文件
echo "开始批量创建文件夹和文件..."

for vendor in "${VENDORS[@]}"; do
    for model in "${MODELS[@]}"; do
        for format in "${FORMATS[@]}"; do
            # 创建文件夹路径
            dir_path="$BASE_DIR/$vendor/$model/$format"
            mkdir -p "$dir_path"
            echo "已创建文件夹: $dir_path"
            
            # 只有当SCENARIOS数组不为空时，才创建文件
            if [ ${#SCENARIOS[@]} -gt 0 ]; then
                for scenario in "${SCENARIOS[@]}"; do
                    # 创建文件
                    file_path="$dir_path/$scenario.mdx"
                    if [ ! -f "$file_path" ]; then
                        touch "$file_path"
                        echo "已创建文件: $file_path"
                    else
                        echo "文件已存在: $file_path"
                    fi
                done
            fi
        done
    done
done

echo "批量创建完成！"