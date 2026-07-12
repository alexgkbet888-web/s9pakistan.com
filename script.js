const root=window.SITE_ROOT||"";
fetch(root+"data/updates.json").catch(()=>{});
(function(){
  const id="G-Y6WS71WJ22";
  if(!id||window.__s9Ga4Loaded)return;
  window.__s9Ga4Loaded=true;
  window.dataLayer=window.dataLayer||[];
  window.gtag=window.gtag||function(){dataLayer.push(arguments);};
  if(!document.querySelector('script[src*="googletagmanager.com/gtag/js?id="+id]')){
    const s=document.createElement("script");
    s.async=true;
    s.src="https://www.googletagmanager.com/gtag/js?id="+id;
    document.head.appendChild(s);
  }
  gtag("js",new Date());
  gtag("config",id);
})();