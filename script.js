const root=window.SITE_ROOT||"";

(function(){
  const id="G-Y6WS71WJ22";
  let started=false;

  function loadDeferredResources(){
    if(started)return;
    started=true;

    fetch(root+"data/updates.json").catch(()=>{});
    window.dataLayer=window.dataLayer||[];
    window.gtag=window.gtag||function(){dataLayer.push(arguments);};

    const script=document.createElement("script");
    script.async=true;
    script.src="https://www.googletagmanager.com/gtag/js?id="+id;
    document.head.appendChild(script);
    gtag("js",new Date());
    gtag("config",id);
  }

  ["pointerdown","keydown","touchstart"].forEach((eventName)=>{
    window.addEventListener(eventName,loadDeferredResources,{once:true,passive:true});
  });
  window.setTimeout(loadDeferredResources,6000);
})();
