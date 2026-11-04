const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const {JSDOM} = require('jsdom');
const asset = name => readFileSync(join(__dirname, '../src/assets', name), 'utf8');
const tick = () => new Promise(resolve => setImmediate(resolve));
const config = {
  shop:'https://namastebookshop.com', shopName:'namastebookshop.com', brand:'Namaste Great Finds',
  domain:'namastegreatfinds.com', attr:'?attributes%5BStorefront%5D=Namaste%20Great%20Finds',
  ref:'namastegreatfinds', street:'2 West 14th Street'
};
const key = 'ni_cart_v1:'+config.domain;
function setup(t, html='', path='/') {
  const dom = new JSDOM(html, {url:'https://namastegreatfinds.com'+path, runScripts:'outside-only'});
  t.after(async () => {await tick(); dom.window.close()});
  const w = dom.window;
  w.NI_CART = {...config};
  w.CSS = {escape: x => String(x)};
  w.HTMLElement.prototype.scrollIntoView = function() {};
  const errors=[];
  w.addEventListener('error',e=>errors.push(e.error));
  t.after(()=>assert.deepEqual(errors,[], 'No browser script errors'));
  w.events=[];
  w.gtag=(...args)=>w.events.push(args);
  w.fetch=async url => {
    if(url==='/data/catalog.json') return {json:async()=>[]};
    throw new Error('Network deliberately blocked in tests');
  };
  // No navigation, analytics request, real Shopify cart or purchase is performed.
  w.document.addEventListener('click', e => {if(e.target.closest('a')) e.preventDefault()});
  return w;
}
const cartHTML = '<p class="cmsg"></p><div data-cart-page><div data-cart-body></div></div>';
const item = extra => ({v:'101',h:'fixture-crystal',t:'Fixture Crystal',vt:'Small',p:15,q:1,ts:Date.now(),...extra});
function click(w, selector) {w.document.querySelector(selector).dispatchEvent(new w.MouseEvent('click',{bubbles:true,cancelable:true}))}
function run(w, name) {w.eval(asset(name))}

test('checkout keeps variant quantities and order attributes, adds referral markers, and emits only a click', t=>{
  const w=setup(t,cartHTML,'/cart/');
  w.localStorage.setItem(key,JSON.stringify([item({q:2}),item({v:'102',p:30,q:3,out:true}),item({v:'104',h:'fixture-candle',p:5,q:1})]));
  run(w,'cart.js');
  const u=new URL(w.NI_CART_URL());
  assert.equal(u.origin,'https://namastebookshop.com');
  assert.equal(u.pathname,'/cart/101:2,104:1');
  assert.equal(u.searchParams.get('attributes[Storefront]'),'Namaste Great Finds');
  assert.equal(u.searchParams.get('attributes[Site]'),'namastegreatfinds.com');
  assert.equal(u.searchParams.get('note'),'Ordered on Namaste Great Finds (namastegreatfinds.com)');
  assert.equal(u.searchParams.get('ref'),'namastegreatfinds');
  assert.equal(u.searchParams.get('utm_source'),'namastegreatfinds.com');
  assert.equal(u.searchParams.get('utm_medium'),'referral');
  assert.equal(u.searchParams.get('utm_campaign'),'namaste_storefront');
  assert.equal(u.searchParams.get('utm_content'),'checkout');
  click(w,'[data-checkout]');
  assert.equal(w.events.length,1);
  assert.equal(w.events[0][1],'checkout_click');
  assert.equal(w.events[0][2].value,35);
  assert.equal(w.events[0][2].items.length,2);
});

test('empty and entirely sold-out carts have no checkout link', t=>{
  for(const items of [[],[item({out:true})]]){
    const w=setup(t,cartHTML,'/cart/');
    w.localStorage.setItem(key,JSON.stringify(items));
    run(w,'cart.js');
    assert.equal(w.NI_CART_URL(),'');
    assert.equal(w.document.querySelector('[data-checkout]'),null);
    assert.equal(w.events.length,0);
  }
});

test('quantity, removal, and storage persistence preserve the shopper basket', t=>{
  const w=setup(t,cartHTML,'/cart/');
  w.localStorage.setItem(key,JSON.stringify([item({q:1,max:3}),item({v:'104',h:'fixture-candle',p:5})]));
  run(w,'cart.js');
  click(w,'[data-v="101"] [data-inc]');
  assert.match(w.NI_CART_URL(),/101:2,104:1/);
  click(w,'[data-v="101"] [data-dec]');
  assert.equal(JSON.parse(w.localStorage.getItem(key))[0].q,1);
  click(w,'[data-v="104"] [data-rm]');
  assert.match(w.NI_CART_URL(),/\/cart\/101:1\?/);
  assert.equal(JSON.parse(w.localStorage.getItem(key)).length,1);
});

test('add_to_cart measures only the quantity actually added below the limit', async t=>{
  const w=setup(t,cartHTML+'<button id="add" data-atc data-v="101" data-h="fixture-crystal" data-t="Fixture Crystal" data-p="15" data-q="5">Add</button>');
  w.localStorage.setItem(key,JSON.stringify([item({q:1,max:2})]));
  w.fetch=async url=>({ok:true,json:async()=>url==='/data/catalog.json'?[]:{variants:[{id:101,price:1500,available:true,quantity_rule:{max:2}}]}});
  run(w,'cart.js');
  click(w,'#add');
  await tick();
  assert.equal(w.events[0][1],'add_to_cart');
  assert.equal(w.events[0][2].items[0].quantity,1);
  assert.equal(w.events[0][2].value,15);
  click(w,'#add');
  assert.equal(w.events.length,1);
  assert.equal(JSON.parse(w.localStorage.getItem(key))[0].q,2);
});

test('analytics missing or throwing cannot block cart and checkout', t=>{
  for(const ga of [undefined,()=>{throw new Error('Blocked')}]){
    const w=setup(t,cartHTML+'<button data-atc data-v="101" data-h="fixture-crystal" data-t="Fixture Crystal" data-p="15">Add</button>');
    w.gtag=ga;
    run(w,'cart.js');
    click(w,'[data-atc]');
    assert.match(w.NI_CART_URL(),/\/cart\/101:1\?/);
    click(w,'[data-checkout]');
    assert.match(w.document.querySelector('[data-checkout]').href,/utm_content=checkout/);
  }
});

test('a live sold-out response excludes an item from checkout', async t=>{
  const w=setup(t,cartHTML,'/cart/');
  w.localStorage.setItem(key,JSON.stringify([item({ts:0})]));
  w.fetch=async url=>({ok:true,json:async()=>url==='/data/catalog.json'?[]:{variants:[{id:101,price:1500,available:false}]}});
  run(w,'cart.js');
  await tick();
  assert.equal(w.NI_CART_URL(),'');
  assert.equal(w.document.querySelector('[data-checkout]'),null);
});

test('contact, booking, directions and bookshop events are clicks without query personal data', t=>{
  const w=setup(t,`
    <a id="phone" href="tel:+12126450141">Call</a>
    <a id="email" href="mailto:info@namastebookshop.com?body=private-message">Email</a>
    <a id="book" href="https://namastebookshop.com/pages/book-a-reading?email=private@example.test">Book</a>
    <a id="map" href="https://www.google.com/maps/dir/?api=1&destination=store">Directions</a>
    <a id="product" href="https://namastebookshop.com/products/fixture?email=private@example.test#secret">Details</a>
    <a id="spoof" href="https://example.test/?next=book.squareup.com">Book now</a>
    <a id="local" href="/shop/">Shop</a>`);
  run(w,'ga.js');
  for(const id of ['phone','email','book','map','product','spoof','local'])click(w,'#'+id);
  assert.deepEqual(w.events.map(e=>e[1]),['contact_click','contact_click','booking_click','directions_click','bookshop_click']);
  const payload=JSON.stringify(w.events);
  for(const word of ['generate_lead','purchase','private','secret','?'])assert.equal(payload.includes(word),false);
});

const productHTML = `<span id="price">$15.00</span><s id="cmp" hidden></s><p id="stock"><span></span></p>
  <select id="variant"><option value="101" selected>Small</option><option value="102">Large</option><option value="103" disabled>Sold out</option></select>
  <button id="buy" data-atc data-v="101" data-h="fixture-crystal" data-t="Fixture Crystal" data-p="15" data-vt="Small">Add to cart</button>`;
const snapshots=[
  {id:101,title:'Small',price:'15.00',compare_at_price:null,available:true},
  {id:102,title:'Large',price:'75.00',compare_at_price:'90.00',available:true},
  {id:103,title:'Sold out',price:'5.00',compare_at_price:null,available:false}
];
function product(w) {w.NI_PRODUCT={handle:'fixture-crystal',shop:config.shop,variants:snapshots}}
function choose(w,id) {const s=w.document.querySelector('#variant');s.value=id;s.dispatchEvent(new w.Event('change',{bubbles:true}))}

test('changing variant while live lookup is pending or fails keeps the exact selected price and ID', async t=>{
  const w=setup(t,productHTML,'/products/fixture-crystal/');product(w);
  let reject;
  w.fetch=()=>new Promise((_,r)=>{reject=r});
  run(w,'site.js');
  choose(w,'102');
  assert.equal(w.document.querySelector('#price').textContent,'$75.00');
  assert.equal(w.document.querySelector('#buy').dataset.p,'75.00');
  assert.equal(w.document.querySelector('#cmp').textContent,'$90.00');
  reject(new Error('Offline'));await tick();
  assert.match(w.document.querySelector('#stock').textContent,/could not be checked/);
  assert.doesNotMatch(w.document.querySelector('#stock').textContent,/In stock/);
  run(w,'cart.js');click(w,'#buy');
  const selected=JSON.parse(w.localStorage.getItem(key))[0];
  assert.equal(selected.v,'102');assert.equal(selected.p,75);assert.equal(selected.vt,'Large');
});

test('live updates replace price, compare price, availability and variant order limits', async t=>{
  const w=setup(t,productHTML,'/products/fixture-crystal/');product(w);
  w.fetch=async()=>({ok:true,json:async()=>({variants:[{id:101,title:'Small',price:1750,compare_at_price:2000,available:true,quantity_rule:{max:2}},{id:102,title:'Large',price:7500,available:false}]})});
  run(w,'site.js');await tick();
  assert.equal(w.document.querySelector('#price').textContent,'$17.50');
  assert.equal(w.document.querySelector('#buy').dataset.max,'2');
  assert.equal(w.document.querySelector('#cmp').textContent,'$20.00');
  assert.equal(w.document.querySelector('#variant option[value="103"]').disabled,true);
  choose(w,'102');
  assert.equal(w.document.querySelector('#buy').disabled,true);
  assert.match(w.document.querySelector('#stock').textContent,/Sold out/);
});

test('a product removed from the store cannot be added using a stale page', async t=>{
  const w=setup(t,productHTML,'/products/fixture-crystal/');product(w);
  w.fetch=async()=>({ok:false,status:404});
  run(w,'site.js');await tick();
  assert.equal(w.document.querySelector('#buy').disabled,true);
  assert.equal(w.document.querySelector('#buy').textContent,'Unavailable');
  assert.match(w.document.querySelector('#stock').textContent,/no longer available/);
});
