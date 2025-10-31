// 测试用户画像保存功能
const axios = require('axios');

// 从登录获取token
async function getToken() {
  try {
    const response = await axios.post('http://localhost:8000/api/v1/auth/token', {
      username: 'jxw123',
      password: '123456'
    });
    return response.data.access_token;
  } catch (error) {
    console.error('获取token失败:', error.response?.data || error.message);
    throw error;
  }
}

// 测试保存用户画像
async function testSaveUserProfile() {
  try {
    // 获取token
    const token = await getToken();
    console.log('获取token成功');
    
    // 准备测试数据 - 模拟前端发送的数据格式
    const testData = {
      basic_info: {
        age: '30-40岁',
        gender: '男',
        marital_status: '已婚',
        name: 'jxw123'
      },
      health_history: [
        { type: 'chronic_diseases', value: '没有' }
      ],
      lifestyle: {
        exercise: '每周1-2次',
        smoking: '不吸烟',
        drinking: '偶尔饮酒'
      },
      symptoms: [
        { 
          symptom: '头痛', 
          description: '经常头痛，尤其是在工作压力大的时候',
          details: {
            frequency: '经常',
            duration: '持续数小时',
            severity: '中等'
          }
        }
      ],
      medical_reports: [
        { type: 'last_check_date', value: '2023-10-15' }
      ],
      focus_areas: [
        { type: 'main_concern', value: '工作压力导致的健康问题' }
      ]
    };
    
    // 发送请求
    const response = await axios.post('http://localhost:8000/api/v1/user-profile/', testData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('保存用户画像成功:', response.data);
    return response.data;
  } catch (error) {
    console.error('保存用户画像失败:', error.response?.data || error.message);
    throw error;
  }
}

// 执行测试
testSaveUserProfile()
  .then(() => {
    console.log('测试完成');
    process.exit(0);
  })
  .catch((error) => {
    console.error('测试失败:', error);
    process.exit(1);
  });