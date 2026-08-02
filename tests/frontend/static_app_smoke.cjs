const fs = require('fs');
const vm = require('vm');

const listeners = {};
const store = new Map();
const root = {
  html: '',
  set innerHTML(value) { this.html = value; },
  get innerHTML() { return this.html; },
  addEventListener(type, listener) { listeners[type] = listener; },
};

const context = {
  console,
  document: {
    documentElement: { lang: 'en' },
    getElementById(id) {
      if (id !== 'root') throw new Error(`Unexpected element id: ${id}`);
      return root;
    },
  },
  localStorage: {
    getItem: key => store.has(key) ? store.get(key) : null,
    setItem: (key, value) => store.set(key, String(value)),
    removeItem: key => store.delete(key),
  },
  location: {
    pathname: '/',
    origin: 'http://localhost:8000',
    href: 'http://localhost:8000/',
  },
  window: { scrollTo() {} },
  navigator: {},
  Headers,
  fetch: async () => { throw new Error('The landing page must not fetch during initial render.'); },
  alert() {},
  confirm() { return true; },
  setTimeout,
  clearTimeout,
};

vm.createContext(context);
vm.runInContext(
  fs.readFileSync('backend/app/static/assets/app.js', 'utf8'),
  context,
  { filename: 'app.js' },
);

if (!root.innerHTML.includes('Turn your space into')) {
  throw new Error('Landing-page hero did not render.');
}
for (const eventName of ['click', 'input', 'change', 'submit']) {
  if (!listeners[eventName]) throw new Error(`Missing ${eventName} event handler.`);
}

console.log('Static browser application smoke test passed.');
