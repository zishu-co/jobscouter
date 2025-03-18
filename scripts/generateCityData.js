const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');

async function fetchCityData() {
  try {
    const response = await axios.get('https://www.zhipin.com/wapi/zpCommon/data/cityGroup.json', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('获取城市数据失败:', error);
    return require('./cityData.backup.json');
  }
}

function transformCityData(data) {
  const cityGroups = {
    'ABCDE': { A: [], B: [], C: [], D: [], E: [] },
    'FGHJ': { F: [], G: [], H: [], J: [] },
    'KLMN': { K: [], L: [], M: [], N: [] },
    'PQRST': { P: [], Q: [], R: [], S: [], T: [] },
    'UVWXYZ': { W: [], X: [], Y: [], Z: [] }
  };

  // 处理城市分组数据
  data.zpData.cityGroup.forEach(group => {
    const firstChar = group.firstChar;
    const cities = group.cityList.map(city => ({
      value: city.code.toString(),
      label: city.name
    }));

    // 找到对应的分组并添加城市
    for (const [key, value] of Object.entries(cityGroups)) {
      if (key.includes(firstChar)) {
        value[firstChar] = cities;
        break;
      }
    }
  });

  return cityGroups;
}

async function generateCityDataFile() {
  try {
    const cityData = await fetchCityData();
    const cityGroups = transformCityData(cityData);
    
    // 热门城市
    const hotCities = [
      { value: '100010000', label: '全国' },
      ...cityData.zpData.hotCityList.map(city => ({
        value: city.code.toString(),
        label: city.name
      }))
    ];

    const fileContent = `// 从 https://www.zhipin.com/wapi/zpCommon/data/cityGroup.json 提取的城市数据
export const cityGroups = ${JSON.stringify(cityGroups, null, 2)}

// 热门城市
export const hotCities = ${JSON.stringify(hotCities, null, 2)}

// 所有城市的扁平数组，用于查找城市信息
export const cityOptions = [
  ...hotCities,
  ...Object.values(cityGroups).flatMap(group => 
    Object.values(group).flat()
  )
]`;

    await fs.writeFile(
      path.join(__dirname, '../frontend/src/api/cityData.js'),
      fileContent,
      'utf8'
    );

    console.log('城市数据文件生成成功');
  } catch (error) {
    console.error('生成城市数据文件失败:', error);
    process.exit(1);
  }
}

generateCityDataFile(); 