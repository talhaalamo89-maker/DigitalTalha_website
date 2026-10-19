(() => {
  const all = (selector, root=document) => [...root.querySelectorAll(selector)];
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = false;
  try { paused = window.localStorage.getItem('digitaltalha-motion') === 'paused'; } catch {}
  const controls = all('[data-motion-toggle]');
  const applyMotion = () => {
    const stopped = paused || reduced.matches;
    document.documentElement.dataset.motion = stopped ? 'paused' : 'playing';
    controls.forEach(button => { button.textContent = reduced.matches ? 'Motion reduced' : paused ? 'Play motion' : 'Pause motion'; button.setAttribute('aria-pressed', String(stopped)); button.disabled = reduced.matches; });
  };
  controls.forEach(button => button.addEventListener('click', () => { paused=!paused; try { window.localStorage.setItem('digitaltalha-motion',paused?'paused':'playing'); } catch {} applyMotion(); }));
  reduced.addEventListener('change', applyMotion);
  applyMotion();
  document.addEventListener('visibilitychange', () => { document.documentElement.dataset.documentHidden=String(document.visibilityState==='hidden'); });

  all('[data-scene-switcher]').forEach(root => {
    const buttons=all('[data-scene-choice]',root), panels=all('[data-scene-panel]',root);
    buttons.forEach(button => button.addEventListener('click', () => {
      const choice=button.dataset.sceneChoice;
      if(!panels.some(panel=>panel.dataset.scenePanel===choice))return;
      buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
      panels.forEach(panel=>panel.hidden=panel.dataset.scenePanel!==choice);
    }));
  });

  const recommendations={
    website:{title:'Website Creation',description:'Build a clear home for your services and an easy route to enquiries.',url:'/website-creation/'},
    search:{title:'Google Ads',description:'Explore search campaigns for people already looking for what you offer.',url:'/google-ads/'},
    social:{title:'Meta Ads',description:'Introduce your offer to relevant people with a clear message and creative.',url:'/meta-ads/'}
  };
  all('[data-goal-picker]').forEach(root=>{
    const buttons=all('[data-goal]',root),pictures=all('[data-goal-picture]',root);
    buttons.forEach(button=>button.addEventListener('click',()=>{
      const key=button.dataset.goal,choice=recommendations[key];if(!choice)return;
      buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
      pictures.forEach(p=>p.hidden=p.dataset.goalPicture!==key);
      root.querySelector('[data-goal-title]').textContent=choice.title;
      root.querySelector('[data-goal-description]').textContent=choice.description;
      const link=root.querySelector('[data-goal-link]');link.textContent='Explore '+choice.title+' ↗';link.setAttribute('href',choice.url);
    }));
  });

  all('[data-journey]').forEach(root=>{
    const buttons=all('[data-journey-choice]',root),panels=all('[data-journey-panel]',root);
    buttons.forEach(button=>button.addEventListener('click',()=>{
      const key=button.dataset.journeyChoice;if(!panels.some(p=>p.dataset.journeyPanel===key))return;
      buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
      panels.forEach(panel=>panel.hidden=panel.dataset.journeyPanel!==key);
    }));
  });

  if('IntersectionObserver' in window){
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>entry.target.classList.toggle('is-scene-visible',entry.isIntersecting)),{threshold:.12});
    all('.motion-stage').forEach(scene=>observer.observe(scene));
  }
})();
