import json
import os

# 定义文档根目录
docs_root = "/Users/wsh/code/gptproto_doc"
allapi_dir = os.path.join(docs_root, "docs", "allapi")
docs_json_path = os.path.join(docs_root, "docs.json")

# 读取当前的docs.json
with open(docs_json_path, "r", encoding="utf-8") as f:
    docs_data = json.load(f)

# 扫描docs/allapi目录结构，构建新的导航数据
new_navigation = {}

# 遍历厂商目录（第一级）
for vendor in os.listdir(allapi_dir):
    vendor_path = os.path.join(allapi_dir, vendor)
    if os.path.isdir(vendor_path):
        # 特殊处理：将Doubao映射为BytePlus
        vendor_name = "BytePlus" if vendor == "Doubao" else vendor
        vendor_name = "Qwen" if vendor == "Alibaba" else vendor
        vendor_data = {"group": vendor_name, "pages": []}
        
        # 遍历模型目录（第二级）
        for model in os.listdir(vendor_path):
            model_path = os.path.join(vendor_path, model)
            if os.path.isdir(model_path):
                model_data = {"group": model, "pages": []}
                
                # 遍历协议目录（第三级）
                for protocol in os.listdir(model_path):
                    protocol_path = os.path.join(model_path, protocol)
                    if os.path.isdir(protocol_path):
                        # 收集该协议下的所有文档文件
                        pages = []
                        for filename in os.listdir(protocol_path):
                            if filename.endswith(".mdx"):
                                # 构建文档路径，格式为：docs/allapi/厂商/模型/协议/文件名（不含扩展名）
                                # 使用实际目录名构建路径，而不是映射后的厂商名
                                page_path = f"docs/allapi/{vendor}/{model}/{protocol}/{filename[:-4]}"
                                pages.append(page_path)
                        
                        # 如果有文档，对页面进行字母排序并添加该协议到模型的pages中
                        if pages:
                            # 对页面进行字母排序
                            pages.sort()
                            protocol_data = {"group": protocol, "pages": pages}
                            model_data["pages"].append(protocol_data)
                
                # 如果模型有协议文档，对协议进行字母排序并添加到厂商的pages中
                if model_data["pages"]:
                    # 对协议进行字母排序
                    model_data["pages"].sort(key=lambda x: x["group"])
                    vendor_data["pages"].append(model_data)
        
        # 如果厂商有模型文档，添加该厂商到新的导航中
        if vendor_data["pages"]:
            # 对模型进行字母排序
            vendor_data["pages"].sort(key=lambda x: x["group"])
            # 使用映射后的厂商名称作为键
            new_navigation[vendor_name] = vendor_data

# 处理导航结构，替换现有的API Reference部分
updated = False
for tab in docs_data["navigation"]["tabs"]:
    if tab["tab"] == "API Reference":
        # 遍历API Reference下的所有组
        for group in tab["groups"]:
            if group["group"] == "API Reference":
                # 保存现有的导航项，并记录原有的厂商顺序
                existing_vendors = {}
                original_vendor_order = []
                vendor_icons = {}
                
                for page in group["pages"]:
                    if isinstance(page, dict) and "group" in page:
                        vendor_name = page["group"]
                        original_vendor_order.append(vendor_name)
                        # 保存厂商的所有原有属性
                        existing_vendors[vendor_name] = page
                        # 保存厂商的icon信息
                        if "icon" in page:
                            vendor_icons[vendor_name] = page["icon"]
                
                # 合并新导航和保留的旧导航，保持原有的厂商顺序
                merged_vendors = []
                
                # 先按照原有的顺序添加厂商
                for vendor_name in original_vendor_order:
                    if vendor_name in new_navigation:
                        # 合并原有厂商的属性和新的模型数据
                        merged_vendor = existing_vendors.get(vendor_name, {})
                        
                        # 获取原有的模型列表和新的模型列表
                        existing_models = {}
                        for model in existing_vendors.get(vendor_name, {}).get("pages", []):
                            if isinstance(model, dict) and "group" in model:
                                existing_models[model["group"]] = model
                        
                        new_models = {}
                        for model in new_navigation[vendor_name].get("pages", []):
                            if isinstance(model, dict) and "group" in model:
                                new_models[model["group"]] = model
                        
                        # 合并模型：保留原有模型，但用新模型替换同名的
                        merged_models = []
                        for model_group in existing_vendors.get(vendor_name, {}).get("pages", []):
                            if isinstance(model_group, dict) and "group" in model_group:
                                model_name = model_group["group"]
                                if model_name in new_models:
                                    # 用新模型替换原有模型
                                    merged_models.append(new_models[model_name])
                                else:
                                    # 保留原有模型
                                    merged_models.append(model_group)
                        
                        # 添加原厂商中没有的新模型
                        for model_name, new_model in new_models.items():
                            if model_name not in existing_models:
                                merged_models.append(new_model)
                        
                        # 对合并后的模型进行字母排序
                        merged_models.sort(key=lambda x: x["group"])
                        
                        # 更新厂商的pages
                        merged_vendor["pages"] = merged_models
                        merged_vendors.append(merged_vendor)
                    elif vendor_name in existing_vendors:
                        # 保留原有的厂商条目
                        merged_vendors.append(existing_vendors[vendor_name])
                
                # 添加原导航中没有的新厂商（保持文件系统中的顺序）
                for fs_vendor in os.listdir(allapi_dir):
                    vendor_path = os.path.join(allapi_dir, fs_vendor)
                    if os.path.isdir(vendor_path):
                        # 应用厂商名称映射
                        vendor_name = "BytePlus" if fs_vendor == "Doubao" else fs_vendor
                        if vendor_name not in original_vendor_order and vendor_name in new_navigation:
                            # 新厂商直接使用新导航中的数据
                            merged_vendors.append(new_navigation[vendor_name])
                
                # 更新pages
                group["pages"] = merged_vendors
                updated = True
                break
    if updated:
        break

# 写回更新后的docs.json
with open(docs_json_path, "w", encoding="utf-8") as f:
    json.dump(docs_data, f, ensure_ascii=False, indent=2)

print("导航结构更新完成！")


# 文档文件存在性检查
print("\n开始检查文档文件...")
print("===============================")

# 提取所有docs/开头的路径
import re

doc_paths = set()

# 使用正则表达式提取所有docs/开头的路径
with open(docs_json_path, "r", encoding="utf-8") as f:
    content = f.read()
    # 查找所有"docs/..."格式的字符串
    matches = re.findall(r'"(docs/[^\"]+)"', content)
    for match in matches:
        doc_paths.add(match)

# 检查每个文档路径是否存在对应的.mdx文件
missing_count = 0
found_count = 0

for doc_path in sorted(doc_paths):
    # 添加.mdx扩展名
    mdx_file = os.path.join(docs_root, f"{doc_path}.mdx")
    
    # 检查文件是否存在
    if os.path.exists(mdx_file):
        found_count += 1
    else:
        print(f"❌ 缺失: {doc_path}.mdx")
        missing_count += 1

print("===============================")
print("📊 检查汇总")
print("===============================")
print(f"总文件数: {found_count + missing_count}")
print(f"✅ 存在: {found_count} 个")
print(f"❌ 缺失: {missing_count} 个")
if missing_count == 0:
    print("")
    print("🎉 所有文档文件都存在！")
print("===============================")
