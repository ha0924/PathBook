/**
 * 小路书 - 主应用逻辑
 */

// ===== DOM References =====
const screenEls = [...document.querySelectorAll('.screen')];
const toast = document.getElementById('toast');
const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modalTitle');
const modalBody = document.getElementById('modalBody');
const modalEyebrow = document.getElementById('modalEyebrow');
const modalActions = document.getElementById('modalActions');

let activeScreen = 'auth';
let toastTimer = 0;
let currentUser = null;
let currentProfile = null;
let isEditMode = false;

// ===== Screen Navigation =====
function go(screen) {
  activeScreen = screen;
  screenEls.forEach((el) => el.classList.toggle('is-active', el.dataset.screen === screen));
}

// ===== Toast =====
function showToast(message) {
  window.clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.add('is-visible');
  toastTimer = window.setTimeout(() => toast.classList.remove('is-visible'), 2400);
}

// ===== Modal =====
function openModal({ eyebrow = '提示', title, body, actions = [] }) {
  modalEyebrow.textContent = eyebrow;
  modalTitle.textContent = title;
  modalBody.textContent = body;
  modalActions.innerHTML = '';
  actions.forEach((action) => {
    const button = document.createElement('button');
    button.className = action.variant === 'primary' ? 'primary-btn' : 'secondary-btn';
    button.type = 'button';
    button.textContent = action.label;
    button.addEventListener('click', () => {
      closeModal();
      action.onClick?.();
    });
    modalActions.appendChild(button);
  });
  modal.classList.add('is-open');
}

function closeModal() {
  modal.classList.remove('is-open');
}

// ===== Auth =====
function initAuth() {
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const authTabs = document.querySelectorAll('.auth-tab');

  // Tab 切换
  authTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      authTabs.forEach((t) => t.classList.remove('is-active'));
      tab.classList.add('is-active');
      const target = tab.dataset.authTab;
      loginForm.classList.toggle('is-hidden', target !== 'login');
      registerForm.classList.toggle('is-hidden', target !== 'register');
    });
  });

  // 登录
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
      showToast('请填写用户名和密码');
      return;
    }

    try {
      await api.login(username, password);
      showToast('登录成功');
      await afterLogin();
    } catch (err) {
      showToast(err.message || '登录失败');
    }
  });

  // 注册
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('regUsername').value.trim();
    const password = document.getElementById('regPassword').value;
    const confirm = document.getElementById('regPasswordConfirm').value;

    if (!username || !password) {
      showToast('请填写用户名和密码');
      return;
    }

    if (password !== confirm) {
      showToast('两次密码不一致');
      return;
    }

    try {
      await api.register(username, password);
      showToast('注册成功，自动登录中…');
      // 注册成功后自动登录
      await api.login(username, password);
      await afterLogin();
    } catch (err) {
      showToast(err.message || '注册失败');
    }
  });
}

async function afterLogin() {
  try {
    currentUser = await api.getMe();
    updateUserUI();

    if (!currentUser.has_profile) {
      go('onboarding');
    } else {
      // 已有画像，加载并进入首页
      try {
        currentProfile = await api.getProfile();
      } catch (_) {
        // 画像获取失败不阻塞
      }
      enterHome();
    }
  } catch (err) {
    showToast('获取用户信息失败');
    api.logout();
    go('auth');
  }
}

function updateUserUI() {
  if (!currentUser) return;
  const initial = currentUser.username.charAt(0).toUpperCase();
  const avatarEls = document.querySelectorAll('#userAvatar, #meAvatar');
  avatarEls.forEach((el) => (el.textContent = initial));
  document.getElementById('meUsername').textContent = currentUser.username;
  const joinDate = new Date(currentUser.created_at).toLocaleDateString('zh-CN');
  document.getElementById('meJoinDate').textContent = `${joinDate} 加入小路书`;
}

// ===== Onboarding =====
function initOnboarding() {
  // Chip 选择逻辑
  document.addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    const row = chip.closest('.chip-row');
    if (!row) return;

    if (row.classList.contains('single-choice')) {
      row.querySelectorAll('.chip').forEach((c) => c.classList.remove('is-selected'));
      chip.classList.add('is-selected');
    } else {
      chip.classList.toggle('is-selected');
    }
  });

  // 保存画像（区分初始化 / 编辑模式）
  document.getElementById('saveProfileBtn').addEventListener('click', async () => {
    const profileData = collectProfileData();
    try {
      if (isEditMode) {
        currentProfile = await api.updateProfile(profileData);
        showToast('偏好已更新');
        exitEditMode();
        renderProfileTags();
        go('me');
      } else {
        currentProfile = await api.initProfile(profileData);
        showToast('偏好设置完成');
        currentUser.has_profile = true;
        enterHome();
      }
    } catch (err) {
      showToast(err.message || '保存失败');
    }
  });

  // 编辑模式 - 返回按钮
  document.getElementById('backFromEditBtn').addEventListener('click', () => {
    exitEditMode();
    go('me');
  });

  // 跳过
  document.getElementById('skipOnboardingBtn').addEventListener('click', async () => {
    try {
      currentProfile = await api.initProfile({});
      currentUser.has_profile = true;
      showToast('已跳过，使用默认偏好');
      enterHome();
    } catch (err) {
      showToast(err.message || '操作失败');
    }
  });
}

function collectProfileData() {
  const data = {};

  // 单选字段
  const singleFields = ['budget_level', 'queue_tolerance_minutes', 'walking_tolerance_meters'];
  singleFields.forEach((field) => {
    const row = document.querySelector(`.chip-row[data-profile="${field}"]`);
    if (!row) return;
    const selected = row.querySelector('.chip.is-selected');
    if (selected) {
      const val = selected.dataset.value;
      if (field === 'queue_tolerance_minutes' || field === 'walking_tolerance_meters') {
        data[field] = parseInt(val, 10);
      } else {
        data[field] = val;
      }
    }
  });

  // 多选字段
  const multiFields = ['transport_preferences', 'food_preferences', 'leisure_preferences'];
  multiFields.forEach((field) => {
    const row = document.querySelector(`.chip-row[data-profile="${field}"]`);
    if (!row) return;
    const selectedChips = row.querySelectorAll('.chip.is-selected');
    if (selectedChips.length > 0) {
      data[field] = [...selectedChips].map((c) => c.dataset.value);
    }
  });

  // home_cities
  const cityRow = document.querySelector('.chip-row[data-profile="home_cities"]');
  if (cityRow) {
    const selected = cityRow.querySelector('.chip.is-selected');
    if (selected) {
      data.home_cities = [selected.dataset.value];
    }
  }

  return data;
}

// ===== Home =====
function enterHome() {
  go('home');
  renderInsight();
}

function renderInsight() {
  if (!currentProfile) return;
  const strip = document.getElementById('insightStrip');
  const desc = document.getElementById('insightDesc');

  const parts = [];
  if (currentProfile.budget_level) {
    const budgetMap = { low: '50以下', medium: '50-100', high: '100-200', premium: '200+' };
    parts.push(`人均${budgetMap[currentProfile.budget_level] || currentProfile.budget_level}`);
  }
  if (currentProfile.transport_preferences?.length) {
    parts.push(currentProfile.transport_preferences.join('/'));
  }
  if (currentProfile.queue_tolerance_minutes !== undefined) {
    parts.push(`排队${currentProfile.queue_tolerance_minutes}分钟内`);
  }

  if (parts.length > 0) {
    desc.textContent = parts.join(' · ');
    strip.style.display = '';
  }
}

function initHome() {
  // 开始规划
  document.getElementById('startPlanBtn').addEventListener('click', () => {
    const input = document.getElementById('intentInput').value.trim();
    if (!input) {
      showToast('请描述你想去哪');
      return;
    }
    go('planning');
    // MVP 阶段暂不调用路线引擎
    showToast('路线引擎开发中，敬请期待');
  });

  // 规划页返回
  document.getElementById('backFromPlanningBtn').addEventListener('click', () => {
    go('home');
  });

  // 非本地生活
  document.getElementById('nonLocalBtn').addEventListener('click', () => {
    openModal({
      eyebrow: '非本地生活需求',
      title: '这个问题不进入路线规划',
      body: '我现在主要帮你安排本地生活路线，比如吃饭、唱歌、逛展、足疗和周末半日安排。',
      actions: [{ label: '知道了', variant: 'primary' }],
    });
  });

  // 快捷规划
  document.addEventListener('click', (e) => {
    const quickBtn = e.target.closest('[data-quick]');
    if (quickBtn) {
      const intent = quickBtn.dataset.quick;
      document.getElementById('intentInput').value =
        `今晚下班后想安排${intent}，顺路再找点别的放松一下。`;
      go('planning');
      showToast('路线引擎开发中，敬请期待');
    }
  });
}

// ===== Me Page =====
function initMePage() {
  document.getElementById('logoutBtn').addEventListener('click', () => {
    openModal({
      eyebrow: '确认',
      title: '退出登录？',
      body: '退出后需要重新登录才能使用。',
      actions: [
        { label: '取消', variant: 'secondary' },
        {
          label: '退出',
          variant: 'primary',
          onClick: () => {
            api.logout();
            currentUser = null;
            currentProfile = null;
            go('auth');
            showToast('已退出登录');
          },
        },
      ],
    });
  });

  document.getElementById('editProfileBtn').addEventListener('click', () => {
    isEditMode = true;
    document.getElementById('backFromEditBtn').style.display = '';
    document.getElementById('skipOnboardingBtn').style.display = 'none';
    document.getElementById('saveProfileBtn').textContent = '保存修改';
    go('onboarding');
    // 回填当前画像
    if (currentProfile) {
      prefillProfile(currentProfile);
    }
  });
}

function exitEditMode() {
  isEditMode = false;
  document.getElementById('backFromEditBtn').style.display = 'none';
  document.getElementById('skipOnboardingBtn').style.display = '';
  document.getElementById('saveProfileBtn').textContent = '开始使用';
}

function prefillProfile(profile) {
  // 单选回填
  if (profile.budget_level) {
    selectChip('budget_level', profile.budget_level);
  }
  if (profile.queue_tolerance_minutes !== undefined) {
    selectChip('queue_tolerance_minutes', String(profile.queue_tolerance_minutes));
  }
  if (profile.walking_tolerance_meters !== undefined) {
    selectChip('walking_tolerance_meters', String(profile.walking_tolerance_meters));
  }
  if (profile.home_cities?.length) {
    selectChip('home_cities', profile.home_cities[0]);
  }

  // 多选回填
  const multiFields = ['transport_preferences', 'food_preferences', 'leisure_preferences'];
  multiFields.forEach((field) => {
    const row = document.querySelector(`.chip-row[data-profile="${field}"]`);
    if (!row || !profile[field]) return;
    row.querySelectorAll('.chip').forEach((chip) => {
      chip.classList.toggle('is-selected', profile[field].includes(chip.dataset.value));
    });
  });
}

function selectChip(field, value) {
  const row = document.querySelector(`.chip-row[data-profile="${field}"]`);
  if (!row) return;
  row.querySelectorAll('.chip').forEach((chip) => {
    chip.classList.toggle('is-selected', chip.dataset.value === value);
  });
}

function renderProfileTags() {
  const container = document.getElementById('profileTagsView');
  if (!container || !currentProfile) return;

  const tags = [];
  if (currentProfile.home_cities?.length) {
    tags.push(...currentProfile.home_cities);
  }
  if (currentProfile.budget_level) {
    const budgetMap = { low: '50以下', medium: '50-100', high: '100-200', premium: '200+' };
    tags.push(`人均${budgetMap[currentProfile.budget_level] || currentProfile.budget_level}`);
  }
  if (currentProfile.transport_preferences?.length) {
    tags.push(...currentProfile.transport_preferences);
  }
  if (currentProfile.food_preferences?.length) {
    tags.push(...currentProfile.food_preferences);
  }
  if (currentProfile.leisure_preferences?.length) {
    tags.push(...currentProfile.leisure_preferences);
  }

  container.innerHTML = tags.map((t) => `<span class="tag">${t}</span>`).join('');
}

// ===== Tab Navigation =====
function initTabs() {
  document.addEventListener('click', (e) => {
    const tabBtn = e.target.closest('[data-tab]');
    if (!tabBtn) return;
    const target = tabBtn.dataset.tab;

    if (target === 'home') {
      go('home');
    } else if (target === 'history') {
      // MVP 暂无历史功能
      showToast('历史路线功能即将上线');
    } else if (target === 'me') {
      renderProfileTags();
      go('me');
    }
  });
}

// ===== Modal Close =====
function initModal() {
  document.getElementById('modalClose').addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });
}

// ===== App Init =====
async function initApp() {
  initAuth();
  initOnboarding();
  initHome();
  initMePage();
  initTabs();
  initModal();

  // 检查是否已登录
  if (api.isLoggedIn) {
    try {
      currentUser = await api.getMe();
      updateUserUI();

      if (!currentUser.has_profile) {
        go('onboarding');
      } else {
        try {
          currentProfile = await api.getProfile();
        } catch (_) {}
        enterHome();
      }
    } catch (err) {
      // Token 过期或无效
      api.logout();
      go('auth');
    }
  } else {
    go('auth');
  }
}

// 启动
initApp();
