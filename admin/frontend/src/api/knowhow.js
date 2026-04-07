import { request } from '@/utils'

export default {
  // Know-How 列表
  getKnowHowList: (params = {}) => request.get('/knowhow', { params }),
  // Know-How 详情
  getKnowHowDetail: (id) => request.get(`/knowhow/${id}`),
  // 创建 Know-How
  createKnowHow: (data = {}) => request.post('/knowhow', data),
  // 更新 Know-How
  updateKnowHow: (id, data = {}) => request.put(`/knowhow/${id}`, data),
  // 删除 Know-How
  deleteKnowHow: (id) => request.delete(`/knowhow/${id}`),
}
