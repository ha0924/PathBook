/**
 * 小路书 - API 封装层
 * 与后端 FastAPI 服务通信
 */

const API_BASE = 'http://127.0.0.1:8000/api/v1';

class ApiClient {
  constructor() {
    this._token = localStorage.getItem('pathbook_token') || null;
  }

  get token() {
    return this._token;
  }

  set token(value) {
    this._token = value;
    if (value) {
      localStorage.setItem('pathbook_token', value);
    } else {
      localStorage.removeItem('pathbook_token');
    }
  }

  get isLoggedIn() {
    return Boolean(this._token);
  }

  /**
   * 通用请求方法
   */
  async request(method, path, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (this._token) {
      headers['Authorization'] = `Bearer ${this._token}`;
    }

    const options = { method, headers };
    if (body && (method === 'POST' || method === 'PATCH' || method === 'PUT')) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${path}`, options);
    const data = await response.json();

    if (!response.ok) {
      const message = data?.detail || data?.message || `请求失败 (${response.status})`;
      throw new Error(message);
    }

    return data;
  }

  // ===== Auth =====

  async register(username, password) {
    const res = await this.request('POST', '/auth/register', { username, password });
    return res.data;
  }

  async login(username, password) {
    const res = await this.request('POST', '/auth/login', { username, password });
    this.token = res.data.access_token;
    return res.data;
  }

  async getMe() {
    const res = await this.request('GET', '/auth/me');
    return res.data;
  }

  logout() {
    this.token = null;
  }

  // ===== Profile =====

  async initProfile(profileData) {
    const res = await this.request('POST', '/user/profile/init', profileData);
    return res.data;
  }

  async getProfile() {
    const res = await this.request('GET', '/user/profile');
    return res.data;
  }

  async updateProfile(profileData) {
    const res = await this.request('PATCH', '/user/profile', profileData);
    return res.data;
  }
}

// 全局实例
const api = new ApiClient();
