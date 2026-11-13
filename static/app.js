const messages = document.getElementById('messages');
const input = document.getElementById('input');
const form = document.getElementById('form');

function addMsg(text, role) {
  const el = document.createElement('div');
  el.className = 'msg ' + role;
  el.textContent = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
  return el;
}

function clock() {
  document.getElementById('clock').textContent = new Date().toLocaleTimeString('zh-CN', {hour12:false});
}
setInterval(clock, 1000); clock();

async function loadQuotes() {
  try {
    const r = await fetch('/api/quotes');
    const data = await r.json();
    const box = document.getElementById('quotes');
    box.innerHTML = '';
    for (const [code, raw] of Object.entries(data)) {
      const div = document.createElement('div');
      div.className = 'q';
      div.textContent = code + '  ' + String(raw).slice(0, 90);
      box.appendChild(div);
    }
  } catch (e) {
    document.getElementById('quotes').innerHTML = '<p class="muted">行情暂不可用（网络或配置问题）</p>';
  }
}
loadQuotes();

document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    input.value = chip.dataset.q;
    input.focus();
  });
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;
  input.value = '';
  addMsg(q, 'user');
  const typing = addMsg('', 'assistant');
  typing.classList.add('typing');
  try {
    const r = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question: q})
    });
    const data = await r.json();
    typing.classList.remove('typing');
    typing.textContent = data.answer || '（无回答）';
  } catch (err) {
    typing.classList.remove('typing');
    typing.textContent = '请求失败：' + err;
  }
  messages.scrollTop = messages.scrollHeight;
});
