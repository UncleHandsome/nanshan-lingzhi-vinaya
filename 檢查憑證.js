// 檢查憑證.js — 一鍵檢查 www.lionccm.org 的 SSL 憑證狀態
// 用法：node 檢查憑證.js
const tls = require('tls');

const TARGETS = [
  { host: 'www.lionccm.org', label: '主站 (www)' },
  { host: 'lionccm.org',     label: '裸域 (lionccm.org)' },
];

const now = new Date();
console.log('');
console.log('========================================');
console.log('  lionccm.org 網站憑證檢查');
console.log('  檢查時間：' + now.toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' }));
console.log('========================================');

let idx = 0;
function next() {
  if (idx >= TARGETS.length) {
    console.log('');
    console.log('檢查結束。');
    return;
  }
  const t = TARGETS[idx++];
  console.log('');
  console.log('【' + t.label + '】 ' + t.host);
  console.log('----------------------------------------');

  const sock = tls.connect({
    host: t.host, servername: t.host, port: 443,
    rejectUnauthorized: false, timeout: 15000,
  }, () => {
    const p = sock.getPeerCertificate(true);
    const exp = new Date(p.valid_to);
    const ok  = now <= exp;
    const nameOk = (p.subjectaltname || '').split(',').map(s => s.trim().replace(/^DNS:/, '')).includes(t.host);
    const days = ((now - exp) / 86400000);

    console.log('  憑證對象 : ' + (p.subject && p.subject.CN));
    console.log('  發證機構 : ' + (p.issuer && p.issuer.O) + ' / ' + (p.issuer && p.issuer.CN));
    console.log('  到期時間 : ' + exp.toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' }));
    console.log('  涵蓋網域 : ' + p.subjectaltname);
    console.log('');
    if (!ok) {
      console.log('  ✗ 憑證已過期 ' + days.toFixed(1) + ' 天 — 這就是打不開的原因');
    } else {
      console.log('  ✓ 憑證有效，還有 ' + (-days).toFixed(0) + ' 天到期');
    }
    if (!nameOk) {
      console.log('  ✗ 此憑證不涵蓋 ' + t.host + '（網域不符）');
    }
    console.log('');
    console.log('  瀏覽器判定 : ' + (sock.authorized ? '✓ 正常' : '✗ ' + sock.authorizationError));
    sock.end();
    setTimeout(next, 200);
  });

  sock.on('error', (e) => {
    console.log('  ✗ 連線失敗：' + (e.code || '') + ' ' + e.message);
    setTimeout(next, 200);
  });
}
next();