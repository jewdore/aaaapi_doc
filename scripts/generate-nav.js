const fs = require('fs');
const path = require('path');

const API_DOCS_PATH = path.join(__dirname, '../docs/api');

// 读取所有厂商目录
function getVendors() {
  const vendors = [];
  const items = fs.readdirSync(API_DOCS_PATH, { withFileTypes: true });

  for (const item of items) {
    if (item.isDirectory() && item.name !== 'quickstart') {
      vendors.push(item.name);
    }
  }

  return vendors;
}

// 读取某个厂商下的所有模型目录
function getModels(vendor) {
  const vendorPath = path.join(API_DOCS_PATH, vendor);
  const models = [];
  const items = fs.readdirSync(vendorPath, { withFileTypes: true });

  for (const item of items) {
    if (item.isDirectory()) {
      models.push(item.name);
    }
  }

  return models;
}

// 读取某个模型下的所有格式目录
function getFormats(vendor, model) {
  const modelPath = path.join(API_DOCS_PATH, vendor, model);
  const formats = [];
  const items = fs.readdirSync(modelPath, { withFileTypes: true });

  for (const item of items) {
    if (item.isDirectory()) {
      formats.push(item.name);
    }
  }

  return formats;
}

// 读取某个格式目录下的所有 MDX 文件
function getPages(vendor, model, format) {
  const formatPath = path.join(API_DOCS_PATH, vendor, model, format);
  const pages = [];

  try {
    const items = fs.readdirSync(formatPath, { withFileTypes: true });

    for (const item of items) {
      if (item.isFile() && item.name.endsWith('.mdx')) {
        const pageName = item.name.replace('.mdx', '');
        pages.push(`docs/api/${vendor}/${model}/${format}/${pageName}`);
      }
    }
  } catch (error) {
    // 忽略错误
  }

  return pages;
}

// 格式化目录名称为显示名称
function formatGroupName(name) {
  // 将 kebab-case 转换为 Title Case
  return name
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// 定义厂商顺序和显示名称映射（按照原 docs.json 的顺序）
const VENDOR_CONFIG = [
  { dir: 'OpenAI', display: 'OpenAI' },
  { dir: 'Google', display: 'Gemini' },
  { dir: 'Claude', display: 'Claude' },
  { dir: 'DeepSeek', display: 'DeepSeek' },
  { dir: 'Doubao', display: 'BytePlus' },
  { dir: 'Flux', display: 'Flux' },
  { dir: 'Gptproto', display: 'Gptproto' },
  { dir: 'Grok', display: 'Grok' },
  { dir: 'Ideogram', display: 'Ideogram' },
  { dir: 'Kling', display: 'Kling' },
  { dir: 'Midjourney', display: 'Midjourney' },
  { dir: 'MiniMax', display: 'MiniMax' },
  { dir: 'Runway', display: 'Runway' },
  { dir: 'Suno', display: 'Suno' },
  { dir: 'Higgsfield', display: 'Higgsfield' },
  { dir: 'Alibaba', display: 'Qwen' },
  { dir: 'Tripo3d', display: 'Tripo3d' }
];

// 生成导航配置
function generateNavigation() {
  const allVendors = getVendors();
  const navigation = [];

  // 按照定义的顺序处理厂商
  for (const vendorConfig of VENDOR_CONFIG) {
    const vendor = vendorConfig.dir;
    const displayName = vendorConfig.display;

    // 跳过不存在的厂商
    if (!allVendors.includes(vendor)) {
      continue;
    }
    const models = getModels(vendor);
    const vendorGroup = {
      group: displayName,
      pages: [],
      icon: getVendorIcon(displayName)
    };

    for (const model of models) {
      const formats = getFormats(vendor, model);

      if (formats.length === 0) {
        // 如果没有格式目录，直接列出文件
        const pages = getPages(vendor, model, '');
        if (pages.length > 0) {
          vendorGroup.pages.push({
            group: model,
            pages: pages
          });
        }
      } else {
        const modelGroup = {
          group: model,
          pages: []
        };

        for (const format of formats) {
          const pages = getPages(vendor, model, format);

          if (pages.length > 0) {
            modelGroup.pages.push({
              group: formatGroupName(format),
              pages: pages
            });
          }
        }

        if (modelGroup.pages.length > 0) {
          vendorGroup.pages.push(modelGroup);
        }
      }
    }

    if (vendorGroup.pages.length > 0) {
      navigation.push(vendorGroup);
    }
  }

  return navigation;
}

// 获取厂商图标
function getVendorIcon(displayName) {
  const icons = {
    'OpenAI': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-draw/AiIcon/GPT.png',
    'Gemini': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-draw/AiIcon/Gemini.png',
    'Claude': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-draw/AiIcon/Claude.png',
    'DeepSeek': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-content/1755520099039-20250818-202809.png',
    'BytePlus': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-draw/AiIcon/doubao.png',
    'Flux': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/2025/05/30/a0ffa3b5d65f4f23a40698c445048c67.png',
    'Gptproto': 'https://oss.heyoos.com/2025/10/23/2df4295950b8433998e058f6539d9e1c.png?x-oss-process=image/format,webp/quality,q_100/resize,w_160,h_160,m_fill',
    'Grok': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-draw/AiIcon/Grok.png',
    'Ideogram': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-draw/AiIcon/Ideogram.png',
    'Kling': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-draw/AiIcon/Kling.png',
    'Midjourney': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-draw/AiIcon/Midjourney.png',
    'MiniMax': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-content/1757932596487-20250915-183623.png',
    'Runway': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-draw/AiIcon/Runway.png',
    'Suno': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-draw/AiIcon/Suno.png',
    'Higgsfield': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-content/1754623057482-20250808-111710.png',
    'Qwen': 'https://heyoo.oss-ap-southeast-1.aliyuncs.com/ai-content/1755663073115-111.png'
  };

  return icons[displayName] || '';
}

// 主函数
function main() {
  const navigation = generateNavigation();

  // 读取现有的 docs.json
  const docsJsonPath = path.join(__dirname, '../docs.json');
  const docsJson = JSON.parse(fs.readFileSync(docsJsonPath, 'utf8'));

  // 更新 API Reference 组
  const apiRefTab = docsJson.navigation.tabs.find(tab => tab.tab === 'API Reference');
  if (apiRefTab) {
    const apiRefGroup = apiRefTab.groups.find(group => group.group === 'API Reference');
    if (apiRefGroup) {
      // 保留 Quick Start
      const quickStart = apiRefGroup.pages.find(page => page.group === 'Quick Start');

      // 更新导航
      apiRefGroup.pages = navigation;

      // 重新添加 Quick Start 到最后
      if (quickStart) {
        apiRefGroup.pages.push(quickStart);
      }
    }
  }

  // 写回文件
  fs.writeFileSync(docsJsonPath, JSON.stringify(docsJson, null, 4));

  console.log('导航配置已更新！');
  console.log(`共处理了 ${navigation.length} 个厂商`);
}

main();
