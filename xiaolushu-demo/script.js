const mockData = {
  selected: {
    food: null,
    fun: null,
  },
  profile: {
    budget: "100-200",
    queue: "15 分钟内",
  },
  verificationReady: false,
  routeSaved: false,
  candidates: {
    food: [
      {
        id: "food-1",
        short: "炙",
        name: "炙京烤肉 · 国贸店",
        distance: "2.8km",
        commute: "12m",
        price: "人均 148",
        rating: "4.7",
        reason: "预算贴合，离国贸近，晚餐口碑稳定。",
        tags: ["预算匹配", "需确认", "可能等位"],
      },
      {
        id: "food-2",
        short: "牛",
        name: "牛场边炉烤肉 · 大望路",
        distance: "3.6km",
        commute: "16m",
        price: "人均 132",
        rating: "4.5",
        reason: "更省预算，适合下班后两人快吃。",
        tags: ["更便宜", "顺路", "环境热闹"],
      },
      {
        id: "food-3",
        short: "焱",
        name: "焱选和牛烧肉 · 三里屯",
        distance: "5.1km",
        commute: "21m",
        price: "人均 198",
        rating: "4.8",
        reason: "品质更好，适合奖励自己，但通勤稍远。",
        tags: ["口碑强", "人均偏高", "距离稍远"],
      },
    ],
    fun: [
      {
        id: "fun-1",
        short: "K",
        name: "麦浪 KTV · 世贸天阶",
        distance: "1.4km",
        commute: "8m",
        price: "人均 88",
        rating: "4.4",
        reason: "从烤肉店过去近，适合 21:00 后续摊。",
        tags: ["通勤短", "需确认", "热门时段"],
      },
      {
        id: "fun-2",
        short: "唱",
        name: "好声音量贩 KTV · 朝阳门",
        distance: "3.2km",
        commute: "14m",
        price: "人均 72",
        rating: "4.2",
        reason: "价格更友好，包厢多，路线不绕。",
        tags: ["预算友好", "包厢多", "需确认"],
      },
      {
        id: "fun-3",
        short: "夜",
        name: "夜场声场 KTV · 三里屯",
        distance: "4.8km",
        commute: "18m",
        price: "人均 126",
        rating: "4.6",
        reason: "氛围更好，适合想把晚上拉满。",
        tags: ["氛围好", "人均偏高", "晚高峰风险"],
      },
    ],
    reselectFun: [
      {
        id: "fun-4",
        short: "星",
        name: "星格 KTV · 双井店",
        distance: "2.1km",
        commute: "10m",
        price: "人均 79",
        rating: "4.3",
        reason: "从烤肉店过去更顺，电话接通率高。",
        tags: ["更稳", "通勤短", "需确认"],
      },
      {
        id: "fun-5",
        short: "音",
        name: "音浪派对 KTV · 合生汇",
        distance: "2.9km",
        commute: "12m",
        price: "人均 96",
        rating: "4.5",
        reason: "商场内更好找，回家打车也方便。",
        tags: ["商场内", "返程方便", "预算适中"],
      },
      {
        id: "fun-6",
        short: "盒",
        name: "盒子唱吧 · 大望路",
        distance: "1.8km",
        commute: "9m",
        price: "人均 68",
        rating: "4.1",
        reason: "轻量续摊，适合不想唱太久。",
        tags: ["最省钱", "更近", "小包厢"],
      },
    ],
  },
};

const screenEls = [...document.querySelectorAll(".screen")];
const candidateGroups = document.getElementById("candidateGroups");
const selectionSummary = document.getElementById("selectionSummary");
const generateRouteBtn = document.getElementById("generateRouteBtn");
const timeline = document.getElementById("timeline");
const verificationList = document.getElementById("verificationList");
const toast = document.getElementById("toast");
const modal = document.getElementById("modal");
const modalTitle = document.getElementById("modalTitle");
const modalBody = document.getElementById("modalBody");
const modalEyebrow = document.getElementById("modalEyebrow");
const modalActions = document.getElementById("modalActions");

let activeScreen = "onboarding";
let toastTimer = 0;
let loadingTimer = 0;
let verificationTimer = 0;

function go(screen) {
  activeScreen = screen;
  screenEls.forEach((el) => el.classList.toggle("is-active", el.dataset.screen === screen));

  if (screen === "candidates") renderCandidates();
  if (screen === "route") renderRoute();
  if (screen === "reselect") renderReselect();
}

function showToast(message) {
  window.clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.add("is-visible");
  toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 2100);
}

function openModal({ eyebrow = "提示", title, body, actions = [] }) {
  modalEyebrow.textContent = eyebrow;
  modalTitle.textContent = title;
  modalBody.textContent = body;
  modalActions.innerHTML = "";
  actions.forEach((action) => {
    const button = document.createElement("button");
    button.className = action.variant === "primary" ? "primary-btn" : "secondary-btn";
    button.type = "button";
    button.textContent = action.label;
    button.addEventListener("click", () => {
      closeModal();
      action.onClick?.();
    });
    modalActions.appendChild(button);
  });
  modal.classList.add("is-open");
  modal.setAttribute("aria-hidden", "false");
}

function closeModal() {
  modal.classList.remove("is-open");
  modal.setAttribute("aria-hidden", "true");
}

function renderCandidates() {
  if (!candidateGroups) return;
  candidateGroups.innerHTML = "";
  renderCandidateGroup("food", "餐饮 · 烤肉", mockData.candidates.food);
  renderCandidateGroup("fun", "娱乐 · KTV", mockData.candidates.fun);
  updateSelectionSummary();
}

function renderCandidateGroup(type, title, items) {
  const group = document.createElement("section");
  group.className = "candidate-group";
  group.innerHTML = `
    <div class="candidate-group-head">
      <h3>${title}</h3>
      <button class="text-link" type="button" data-refresh="${type}">不喜欢，换一批</button>
    </div>
  `;

  items.forEach((item) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = `candidate-card ${mockData.selected[type]?.id === item.id ? "is-selected" : ""}`;
    card.dataset.selectType = type;
    card.dataset.selectId = item.id;
    card.innerHTML = `
      <div class="candidate-art">${item.short}</div>
      <div class="candidate-content">
        <h4>${item.name}</h4>
        <p class="candidate-meta">${item.distance} · 车程 ${item.commute} · ${item.price} · 评分 ${item.rating}</p>
        <p class="candidate-reason">${item.reason}</p>
        <div class="tag-row">
          ${item.tags.map((tag) => `<span class="tag ${tag.includes("确认") || tag.includes("风险") || tag.includes("等位") ? "warn" : ""}">${tag}</span>`).join("")}
        </div>
      </div>
    `;
    group.appendChild(card);
  });

  candidateGroups.appendChild(group);
}

function updateSelectionSummary() {
  const food = mockData.selected.food?.name ?? "未选烤肉";
  const fun = mockData.selected.fun?.name ?? "未选 KTV";
  const ready = Boolean(mockData.selected.food && mockData.selected.fun);
  selectionSummary.textContent = ready ? `已选：${food} + ${fun}` : `请先选择：${food} / ${fun}`;
  generateRouteBtn.disabled = !ready;
}

function startLoading() {
  go("loading");
  window.clearTimeout(loadingTimer);
  window.clearTimeout(verificationTimer);
  mockData.verificationReady = false;
  loadingTimer = window.setTimeout(() => {
    go("route");
    verificationTimer = window.setTimeout(() => {
      mockData.verificationReady = true;
      if (activeScreen === "route") renderRoute();
      showToast("电话核验已更新：KTV 未接通，请决定是否保留");
    }, 3000);
  }, 2000);
}

function renderRoute() {
  const food = mockData.selected.food || mockData.candidates.food[0];
  const fun = mockData.selected.fun || mockData.candidates.fun[0];
  document.getElementById("routeTitle").textContent = `国贸下班 ${food.name.split(" · ")[0]} + ${fun.name.split(" · ")[0]}`;
  document.getElementById("routeCommute").textContent = fun.id.startsWith("fun-4") || fun.id.startsWith("fun-6") ? "27m" : "31m";
  document.getElementById("routeBudget").textContent = fun.id === "fun-6" ? "约 135" : "约 150";
  document.getElementById("riskCount").textContent = mockData.verificationReady ? "1 项" : "确认中";
  document.getElementById("mapFoodPin").textContent = "烤肉";
  document.getElementById("mapFunPin").textContent = fun.id === "fun-6" ? "唱吧" : "KTV";
  document.getElementById("verificationHint").textContent = mockData.verificationReady ? "1 项未确认，等待用户决策" : "商家风险确认中";

  timeline.innerHTML = [
    timelineItem("18:30", "国贸出发", "打车前往餐厅，晚高峰预计 12 分钟。", "已定位", "success"),
    timelineItem("18:45", food.name, "停留 90 分钟。系统已根据预算和排队容忍度排序。", mockData.verificationReady ? "等位约 10 分钟" : "核验中", mockData.verificationReady ? "warn" : "checking"),
    timelineItem("20:25", fun.name, "从餐厅出发，预计车程 8-12 分钟，KTV 停留 120 分钟。", mockData.verificationReady ? "未接通" : "核验中", mockData.verificationReady ? "warn" : "checking"),
  ].join("");

  verificationList.innerHTML = verificationCard(food, "food") + verificationCard(fun, "fun");
}

function timelineItem(time, title, desc, status, statusType) {
  return `
    <article class="timeline-item">
      <div class="time-badge">${time}</div>
      <div class="timeline-card">
        <h4>${title}</h4>
        <p>${desc}</p>
        <div class="timeline-actions">
          <span class="status-pill ${statusType}">${status}</span>
          <button class="tiny-btn" type="button" data-nav>导航</button>
        </div>
      </div>
    </article>
  `;
}

function verificationCard(item, type) {
  if (!mockData.verificationReady) {
    return `
      <article class="verification-card">
        <strong>${item.name}</strong>
        <span>正在确认：是否营业、是否等位、预计等位多久。路线可先查看。</span>
        <div class="tag-row"><span class="status-pill checking">核验中</span></div>
      </article>
    `;
  }

  if (type === "food") {
    return `
      <article class="verification-card">
        <strong>${item.name}</strong>
        <span>已确认营业。2 人 18:45 到店预计等位 10 分钟，在你的 15 分钟容忍范围内。</span>
        <div class="tag-row"><span class="status-pill success">已确认</span><span class="status-pill warn">等位 10 分钟</span></div>
      </article>
    `;
  }

  return `
    <article class="verification-card">
      <strong>${item.name}</strong>
      <span>商家暂未接通，营业和包厢情况未确认。你可以保留，也可以换一家更稳的。</span>
      <div class="tag-row"><span class="status-pill warn">未接通</span><span class="status-pill">用户决定</span></div>
      <div class="verification-actions">
        <button type="button" data-keep-fun>保留此地点</button>
        <button type="button" data-replace-fun>换一家</button>
        <button type="button" data-later>稍后再确认</button>
      </div>
    </article>
  `;
}

function renderReselect() {
  const food = mockData.selected.food || mockData.candidates.food[0];
  document.getElementById("lockedRouteText").textContent = `国贸 → ${food.name}`;
  const list = document.getElementById("reselectList");
  list.innerHTML = "";
  mockData.candidates.reselectFun.forEach((item) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "candidate-card";
    card.dataset.reselectFun = item.id;
    card.innerHTML = `
      <div class="candidate-art">${item.short}</div>
      <div class="candidate-content">
        <h4>${item.name}</h4>
        <p class="candidate-meta">${item.distance} · 车程 ${item.commute} · ${item.price} · 评分 ${item.rating}</p>
        <p class="candidate-reason">${item.reason}</p>
        <div class="tag-row">${item.tags.map((tag) => `<span class="tag ${tag.includes("稳") || tag.includes("确认") ? "warn" : ""}">${tag}</span>`).join("")}</div>
      </div>
    `;
    list.appendChild(card);
  });
}

function askRefreshReason(type) {
  openModal({
    eyebrow: "换一批",
    title: "这批候选哪里不合适？",
    body: "原因会影响下一批候选的排序和筛选。Demo 中会模拟记录你的选择。",
    actions: ["太贵", "太远", "可能排队", "品类不对"].map((label) => ({
      label,
      onClick: () => showToast(`已记录原因：${label}，正在调整 ${type === "food" ? "餐饮" : "娱乐"} 候选`),
    })),
  });
}

document.addEventListener("click", (event) => {
  const target = event.target.closest("button, [data-go], .mini-route");
  if (!target) return;

  if (target.dataset.go) {
    go(target.dataset.go);
    return;
  }

  if (target.dataset.quick) {
    const intent = target.dataset.quick;
    document.getElementById("intentInput").value =
      intent === "唱歌"
        ? "今晚下班后想吃点东西，再找个地方唱歌放松一下。"
        : `今晚下班后想安排${intent}，顺路再找点别的放松一下。`;
    go("clarify");
    return;
  }

  if (target.id === "startPlanBtn") {
    go("clarify");
    return;
  }

  if (target.id === "nonLocalBtn") {
    openModal({
      eyebrow: "非本地生活需求",
      title: "这个问题不进入路线规划",
      body: "我现在主要帮你安排本地生活路线，比如吃饭、唱歌、逛展、足疗和周末半日安排。你可以试试：今晚下班后想吃点好的，再找个地方放松一下。",
      actions: [{ label: "知道了", variant: "primary" }],
    });
    return;
  }

  if (target.closest(".chip-row")) {
    const row = target.closest(".chip-row");
    if (row.classList.contains("single-choice")) {
      row.querySelectorAll(".chip").forEach((chip) => chip.classList.remove("is-selected"));
    }
    target.classList.toggle("is-selected");
    if (row.dataset.profile === "budget") {
      mockData.profile.budget = target.textContent.trim();
      const profileBudget = document.getElementById("profileBudget");
      if (profileBudget) profileBudget.textContent = mockData.profile.budget;
    }
    return;
  }

  if (target.id === "partyCard") {
    const value = document.getElementById("partyValue");
    value.textContent = value.textContent === "2 人" ? "4 人" : value.textContent === "4 人" ? "1 人" : "2 人";
    return;
  }

  if (target.id === "budgetCard") {
    const value = document.getElementById("budgetValue");
    value.textContent = value.textContent === "人均 150" ? "人均 200" : "人均 150";
    return;
  }

  if (target.id === "endTimeCard") {
    const value = document.getElementById("endTimeValue");
    value.textContent = value.textContent === "不限制" ? "23:00 前结束" : "不限制";
    return;
  }

  if (target.dataset.refresh) {
    askRefreshReason(target.dataset.refresh);
    return;
  }

  if (target.dataset.selectType) {
    const type = target.dataset.selectType;
    const item = mockData.candidates[type].find((candidate) => candidate.id === target.dataset.selectId);
    mockData.selected[type] = item;
    renderCandidates();
    return;
  }

  if (target.id === "generateRouteBtn") {
    startLoading();
    return;
  }

  if (target.dataset.nav !== undefined || target.id === "navBtn") {
    showToast("Demo 模式：这里会跳转高德/系统地图导航");
    return;
  }

  if (target.id === "saveRouteBtn") {
    mockData.routeSaved = true;
    showToast("路线已保存到历史记录");
    return;
  }

  if (target.id === "replaceLastBtn" || target.dataset.replaceFun !== undefined) {
    go("reselect");
    return;
  }

  if (target.dataset.keepFun !== undefined) {
    showToast("已保留未接通 KTV，路线风险保持提示");
    return;
  }

  if (target.dataset.later !== undefined) {
    showToast("稍后会再次尝试确认商家风险");
    return;
  }

  if (target.dataset.reselectFun) {
    const item = mockData.candidates.reselectFun.find((candidate) => candidate.id === target.dataset.reselectFun);
    mockData.selected.fun = item;
    mockData.verificationReady = false;
    showToast("已替换最后一个地点，前序路线保持固定");
    go("route");
    window.clearTimeout(verificationTimer);
    verificationTimer = window.setTimeout(() => {
      mockData.verificationReady = true;
      if (activeScreen === "route") renderRoute();
    }, 2000);
    return;
  }

  if (target.dataset.reuse !== undefined) {
    showToast("历史路线已复用，将重新计算并确认风险");
    go("route");
  }
});

document.getElementById("modalClose").addEventListener("click", closeModal);
modal.addEventListener("click", (event) => {
  if (event.target === modal) closeModal();
});

document.querySelectorAll("#reasonGrid button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("#reasonGrid button").forEach((item) => item.classList.remove("is-selected"));
    button.classList.add("is-selected");
  });
});
