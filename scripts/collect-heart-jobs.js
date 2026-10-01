// Run with playwright-cli run-code --filename scripts/collect-heart-jobs.js against a local HTTP server.
async (page) => {
 const all=new Set();const pages=[];
 for(const path of ['', 'Actividad%202-julio-2026/Actividad.html']){
  await page.goto('http://127.0.0.1:8765/'+path);
  const data=await page.evaluate(()=>({texts:window.IFR_HEART_TEXTS,buttons:document.querySelectorAll('.audio-btn').length,unknown:document.querySelectorAll('.audio-btn:not([data-heart-text])').length}));
  if(!data.texts?.length||data.unknown)throw Error('Unmapped audio on '+path);
  data.texts.forEach(t=>all.add(t));pages.push({path,buttons:data.buttons,texts:data.texts.length});
 }
 return {pages,texts:[...all].sort()};
}
