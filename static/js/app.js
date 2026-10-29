const app = document.querySelector('#app');
const notice = document.querySelector('#notice');
const nav = document.querySelector('#nav');
const menu = document.querySelector('.menu-button');

// 복귀 대상은 앱이 제공하는 내부 화면만 허용한다.
function safeNext(value) {
  const uuid = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}';
  const allowed = new RegExp(`^/#(?:products|cart|account|orders|product/${uuid}|payment/${uuid})$`);
  return typeof value === 'string' && allowed.test(value) ? value : '/#products';
}
function currentNext() { return safeNext('/' + (location.hash || '#products')); }
function loginNext() {
  const query = location.hash.split('?')[1] || '';
  return safeNext(new URLSearchParams(query).get('next'));
}
function redirectToLogin() {
  const next = currentNext();
  location.hash = `login?next=${encodeURIComponent(next)}`;
}
function handleError(error) {
  if (!error.redirected) showMessage(error.message, true);
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
const money = value => `${Number(value).toLocaleString('ko-KR')}원`;
function showMessage(message, error = false) {
  notice.className = `notice${error ? ' error' : ''}`;
  notice.textContent = message;
}
function clearMessage() { notice.className = ''; notice.textContent = ''; }
async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    method: options.method || 'GET', credentials: 'same-origin',
    headers: options.body ? {'Content-Type':'application/json'} : {},
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const result = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith('/auth/')) {
      redirectToLogin();
      const error = new Error('로그인이 필요합니다.');
      error.redirected = true;
      throw error;
    }
    const detail = typeof result?.detail === 'string' ? result.detail : '입력값을 확인해 주세요.';
    throw new Error(detail);
  }
  return result;
}
function picture(product) {
  try {
    const url = new URL(product.image_url, location.origin);
    if (product.image_url && ['http:', 'https:'].includes(url.protocol)) return `<img class="product-image" src="${escapeHtml(url.href)}" alt="${escapeHtml(product.name)}">`;
  } catch (_) { /* 이미지가 없으면 대체 영역을 표시한다. */ }
  return '<div class="placeholder">상품 이미지</div>';
}
function fields(form) { return Object.fromEntries(new FormData(form).entries()); }
function bindForm(id, handler) {
  document.querySelector(id).addEventListener('submit', async event => {
    event.preventDefault(); clearMessage();
    try { await handler(fields(event.currentTarget)); } catch (error) { handleError(error); }
  });
}
function go(hash) { location.hash = hash; }
function input(label, name, type = 'text', extra = '') { return `<label>${label}<input name="${name}" type="${type}" ${extra} required></label>`; }

async function productList() {
  const products = await api('/products');
  app.innerHTML = `<h1>상품 목록</h1><div class="grid">${products.map(p => `<article class="card">${picture(p)}<h2>${escapeHtml(p.name)}</h2><p class="price">${money(p.price)}</p><p class="muted">재고 ${p.stock}개</p><a class="button" href="#product/${encodeURIComponent(p.id)}">상세 보기</a></article>`).join('')}</div>${products.length ? '' : '<p>등록된 상품이 없습니다.</p>'}`;
}
async function productDetail(id) {
  const p = await api(`/products/${encodeURIComponent(id)}`);
  app.innerHTML = `<h1>${escapeHtml(p.name)}</h1><div class="panel">${picture(p)}<p>${escapeHtml(p.description)}</p><p class="price">${money(p.price)}</p><p>재고 ${p.stock}개</p><label>수량<input id="quantity" type="number" min="1" max="${Math.min(p.stock,10000)}" value="1" ${p.stock ? '' : 'disabled'}></label><div class="actions"><button id="add" ${p.stock ? '' : 'disabled'}>장바구니 담기</button><button id="direct" class="secondary" ${p.stock ? '' : 'disabled'}>바로 결제</button></div></div>`;
  const quantity = () => { const n = Number(document.querySelector('#quantity').value); if (!Number.isInteger(n) || n < 1 || n > Math.min(p.stock, 10000)) throw new Error('수량을 확인해 주세요.'); return n; };
  document.querySelector('#add').onclick = async () => { try { await api('/cart/items', {method:'POST',body:{product_id:id,quantity:quantity()}}); go('cart'); } catch(e) { handleError(e); } };
  document.querySelector('#direct').onclick = async () => { try { const n = quantity(); const order = await api('/orders/direct',{method:'POST',body:{product_id:id,quantity:n}}); sessionStorage.setItem(`order-${order.order_id}`, JSON.stringify({name:p.name,quantity:n,total:p.price*n})); go(`payment/${order.order_id}`); } catch(e) { handleError(e); } };
}
function login() {
  app.innerHTML = `<h1>로그인</h1><form id="login-form" class="panel form">${input('이메일','email','email','autocomplete="email"')}${input('비밀번호','password','password','autocomplete="current-password"')}<button>로그인</button><a href="#register?next=${encodeURIComponent(loginNext())}">회원가입</a></form>`;
  bindForm('#login-form', async data => { await api('/auth/login',{method:'POST',body:data}); location.replace(loginNext()); });
}
function register() {
  app.innerHTML = `<h1>회원가입</h1><form id="register-form" class="panel form">${input('이메일','email','email','autocomplete="email"')}${input('비밀번호 (8자 이상)','password','password','minlength="8" autocomplete="new-password"')}${input('이름','name')}${input('연락처','phone','tel')}${input('주소','address')}<button>가입하기</button><a href="#login?next=${encodeURIComponent(loginNext())}">로그인</a></form>`;
  bindForm('#register-form', async data => { const next = loginNext(); await api('/auth/register',{method:'POST',body:data}); go(`login?next=${encodeURIComponent(next)}`); });
}
async function cartPage() {
  const cart = await api('/cart');
  app.innerHTML = `<h1>장바구니</h1><div class="stack">${cart.items.map(i => `<article class="panel"><h2>${escapeHtml(i.products.name)}</h2><p>현재 가격 ${money(i.products.price)} · 재고 ${i.products.stock}개</p><label>수량<input type="number" min="1" max="10000" value="${i.quantity}" id="q-${i.id}"></label><div class="actions"><button data-update="${i.id}" class="secondary">수량 변경</button><button data-delete="${i.id}" class="danger">삭제</button></div></article>`).join('') || '<p>장바구니가 비어 있습니다.</p>'}</div>${cart.items.length ? '<div class="actions"><button id="checkout">주문하기</button></div>' : ''}`;
  document.querySelectorAll('[data-update]').forEach(button => button.onclick = async () => { try { const n=Number(document.getElementById(`q-${button.dataset.update}`).value); if (!Number.isInteger(n) || n < 1 || n > 10000) throw new Error('수량을 확인해 주세요.'); await api(`/cart/items/${button.dataset.update}`,{method:'PATCH',body:{quantity:n}}); await cartPage(); showMessage('수량을 변경했습니다.'); } catch(e) { handleError(e); } });
  document.querySelectorAll('[data-delete]').forEach(button => button.onclick = async () => { try { await api(`/cart/items/${button.dataset.delete}`,{method:'DELETE'}); await cartPage(); showMessage('상품을 삭제했습니다.'); } catch(e) { handleError(e); } });
  const checkout = document.querySelector('#checkout');
  if (checkout) checkout.onclick = async () => { try { const order = await api('/orders',{method:'POST'}); sessionStorage.setItem(`order-${order.order_id}`, JSON.stringify({name:cart.items.map(i => i.products.name).join(', '),total:cart.items.reduce((sum,i) => sum+i.products.price*i.quantity,0)})); go(`payment/${order.order_id}`); } catch(e) { handleError(e); } };
}
function paymentPage(id) {
  let details = null;
  try { details = JSON.parse(sessionStorage.getItem(`order-${id}`)); } catch (_) {}
  app.innerHTML = `<h1>모의 결제</h1><div class="panel"><p>주문 번호: ${escapeHtml(id)}</p>${details ? `<p>상품: ${escapeHtml(details.name)}</p><p class="price">예상 금액: ${money(details.total)}</p><p class="muted">결제 금액은 주문 생성 시 확정된 단가를 기준으로 합니다.</p>` : '<p>주문 정보를 확인한 뒤 결제해 주세요.</p>'}<div class="actions"><button id="pay">결제하기</button><button id="fail" class="secondary">결제 실패 시험</button></div></div>`;
  async function pay(success) { try { await api(`/orders/${encodeURIComponent(id)}/payment`,{method:'POST',body:{success}}); if (success) { sessionStorage.removeItem(`order-${id}`); go('products'); showMessage('결제가 완료되었습니다.'); } else showMessage('모의 결제가 실패했습니다. 다시 시도할 수 있습니다.',true); } catch(e) { handleError(e); } }
  document.querySelector('#pay').onclick = () => pay(true);
  document.querySelector('#fail').onclick = () => pay(false);
}
async function accountPage() {
  const u = await api('/me');
  app.innerHTML = `<h1>회원정보</h1><div class="stack"><form id="profile-form" class="panel form"><h2>정보 수정</h2><p>${escapeHtml(u.email)}</p>${input('이름','name')}${input('연락처','phone','tel')}${input('주소','address')}<button>저장</button></form><form id="password-form" class="panel form"><h2>비밀번호 변경</h2>${input('현재 비밀번호','current_password','password','autocomplete="current-password"')}${input('새 비밀번호 (8자 이상)','new_password','password','minlength="8" autocomplete="new-password"')}<button>비밀번호 변경</button></form><form id="delete-form" class="panel form"><h2>회원 탈퇴</h2><p>탈퇴 후 로그인할 수 없으며 구매내역은 보존됩니다.</p>${input('현재 비밀번호','password','password','autocomplete="current-password"')}<button class="danger">탈퇴하기</button></form></div>`;
  const form = document.querySelector('#profile-form'); for (const key of ['name','phone','address']) form.elements[key].value = u[key];
  bindForm('#profile-form', async data => { await api('/me',{method:'PATCH',body:data}); showMessage('회원정보를 수정했습니다.'); });
  bindForm('#password-form', async data => { await api('/me/password',{method:'POST',body:data}); go('login'); showMessage('비밀번호가 변경되었습니다. 다시 로그인해 주세요.'); });
  bindForm('#delete-form', async data => { if (!confirm('정말 탈퇴하시겠습니까?')) return; await api('/me',{method:'DELETE',body:data}); go('products'); showMessage('회원 탈퇴가 완료되었습니다.'); });
}
async function ordersPage() {
  const orders = await api('/me/orders');
  app.innerHTML = `<h1>구매내역</h1><div class="stack">${orders.map(o => `<article class="panel"><h2>주문 ${escapeHtml(o.id)}</h2><p>${escapeHtml(new Date(o.created_at).toLocaleString('ko-KR'))}</p>${o.order_items.map(i => `<div class="order-item">${escapeHtml(i.products?.name || '상품')} · ${i.quantity}개 · 단가 ${money(i.unit_price)}</div>`).join('')}<p class="price">결제금액 ${money(Array.isArray(o.payments) ? o.payments[0]?.amount : o.payments?.amount)}</p></article>`).join('') || '<p>구매내역이 없습니다.</p>'}</div>`;
}
async function render() {
  clearMessage(); nav.classList.remove('open'); menu.setAttribute('aria-expanded','false');
  const [page, id] = (location.hash.slice(1).split('?')[0] || 'products').split('/');
  app.innerHTML = '<p>불러오는 중입니다.</p>';
  try {
    if (page === 'products') await productList();
    else if (page === 'product' && id) await productDetail(id);
    else if (page === 'login') login();
    else if (page === 'register') register();
    else if (page === 'cart') await cartPage();
    else if (page === 'payment' && id) { await api('/me'); paymentPage(id); }
    else if (page === 'account') await accountPage();
    else if (page === 'orders') await ordersPage();
    else app.innerHTML = '<p>페이지를 찾을 수 없습니다.</p>';
  } catch(e) { if (!e.redirected) { app.innerHTML = '<p>화면을 불러오지 못했습니다.</p>'; handleError(e); } }
}
menu.onclick = () => { const open = nav.classList.toggle('open'); menu.setAttribute('aria-expanded',String(open)); };
document.querySelector('#logout').onclick = async () => { try { await api('/auth/logout',{method:'POST'}); go('products'); showMessage('로그아웃했습니다.'); } catch(e) { handleError(e); } };
window.addEventListener('hashchange', render);
render();


