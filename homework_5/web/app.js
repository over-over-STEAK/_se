const el = id => document.getElementById(id);
async function api(path, options) {
  const res = await fetch(path, options);
  if (!res.ok) throw new Error(`API 回傳 HTTP ${res.status}`);
  return res.json();
}
async function refresh() {
  const results = await Promise.allSettled([
    api('/api/node/health'), api('/api/python/health'),
    api('/api/node/messages'), api('/api/python/stats')
  ]);
  ['node','python'].forEach((id, i) => {
    el(id).textContent = results[i].status === 'fulfilled' ? '已連線 · 健康' : '無法連線';
  });
  el('db').textContent = results.slice(0,2).every(r => r.status === 'fulfilled') ? '兩個 API 皆可存取' : '連線檢查未全部通過';
  el('messages').replaceChildren();
  if (results[2].status === 'fulfilled') {
    for (const message of results[2].value) {
      const li=document.createElement('li'), p=document.createElement('p'), date=document.createElement('small');
      p.textContent=message.content;
      date.textContent=`#${message.id} · ${new Date(message.created_at).toLocaleString('zh-TW')}`;
      li.append(p,date); el('messages').append(li);
    }
    if (!results[2].value.length) el('messages').textContent='目前沒有留言';
  } else el('messages').textContent='留言載入失敗，請檢查容器狀態後重新整理。';
  el('count').textContent=results[3].status === 'fulfilled' ? results[3].value.total_messages : '—';
}
el('form').addEventListener('submit', async event => {
  event.preventDefault(); el('submit').disabled=true;
  try {
    await api('/api/node/messages', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({content:el('content').value})});
    el('content').value=''; el('notice').textContent='新增成功，資料已寫入 PostgreSQL。'; await refresh();
  } catch(err) { el('notice').textContent=`新增失敗：${err.message}`; }
  finally { el('submit').disabled=false; }
});
el('refresh').addEventListener('click',refresh);
refresh();
