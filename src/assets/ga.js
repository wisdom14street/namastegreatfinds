/* Storefront engagement only. Link clicks are not leads, bookings, purchases or paid revenue.
   add_to_cart and checkout_click are sent from cart.js. Confirmed purchases belong to Shopify. */
(function(){
  function ga(n,p){try{var c=window.NI_CART||{};if(typeof window.gtag==='function')window.gtag('event',n,Object.assign({site_brand:c.brand,site_domain:c.domain},p||{}))}catch(_){}}
  window.niGA=ga;
  try{
    if(/^\/products\//.test(location.pathname)){
      var b=document.getElementById('buy'),it=null;
      if(b&&b.dataset&&b.dataset.v){var d=b.dataset;it={item_id:String(d.v),item_name:d.t+(d.vt&&d.vt!=='Default Title'?' - '+d.vt:''),price:+d.p||0,quantity:1};if(d.c)it.item_category=d.c}
      else{[].forEach.call(document.querySelectorAll('script[type="application/ld+json"]'),function(s){if(it)return;try{var j=JSON.parse(s.textContent);(Array.isArray(j)?j:[j]).forEach(function(o){if(!it&&o&&o['@type']==='Product'){var of=Array.isArray(o.offers)?o.offers[0]:(o.offers||{});it={item_id:String(o.sku||location.pathname.split('/')[2]),item_name:o.name,price:+of.price||0,quantity:1}}})}catch(_){}})}
      if(it)ga('view_item',{currency:'USD',value:it.price,items:[it]});
    }
  }catch(_){}
  var BOOK_HOSTS=['book.squareup.com','calendly.com','acuityscheduling.com','as.me','setmore.com'],
      MAP_HOSTS=['www.google.com','maps.google.com','maps.apple.com','maps.app.goo.gl','goo.gl'];
  function kind(a){
    var h=a.getAttribute('href')||'';
    if(/^tel:/i.test(h))return'phone';
    if(/^mailto:/i.test(h))return/^mailto:claim@/i.test(h)?'claim':'email';
    var u;try{u=new URL(h,location.href)}catch(_){return''}
    if(u.origin===location.origin&&/^\/claim(\/|$)/.test(u.pathname))return'claim';
    if(!/^https?:$/.test(u.protocol))return'';
    if(MAP_HOSTS.indexOf(u.hostname)!==-1&&(u.pathname.indexOf('/maps')===0||u.hostname==='maps.apple.com'||u.hostname==='maps.app.goo.gl'))return'directions';
    if(BOOK_HOSTS.indexOf(u.hostname)!==-1||(u.hostname==='namastebookshop.com'&&u.pathname.replace(/\/$/,'')==='/pages/book-a-reading'))return'booking';
    if(u.hostname==='namastebookshop.com'&&!/^\/cart(?:\/|$)/.test(u.pathname))return'bookshop';
    return'';
  }
  document.addEventListener('click',function(e){try{
    var a=e.target&&e.target.closest&&e.target.closest('a[href]');if(!a)return;var k=kind(a);if(!k)return;
    var u=new URL(a.getAttribute('href'),location.href),names={phone:'contact_click',email:'contact_click',claim:'contact_click',booking:'booking_click',directions:'directions_click',bookshop:'bookshop_click'};
    // Queries can contain email bodies or personal information; never send them in custom events.
    var destination=/^https?:$/.test(u.protocol)?u.origin+u.pathname:u.protocol;
    ga(names[k],{link_type:k,link_url:destination.slice(0,200),transport_type:'beacon'});
  }catch(_){}},true);
})();
