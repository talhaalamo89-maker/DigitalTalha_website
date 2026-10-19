import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const code=fs.readFileSync(new URL('../assets/motion.js',import.meta.url),'utf8');
class Node {
  constructor(dataset={}){this.dataset=dataset;this.events={};this.attrs={};this.hidden=false;this.textContent='';this.disabled=false;this.children={};this.groups={};this.classes=new Set();this.classList={toggle:(key,value)=>value?this.classes.add(key):this.classes.delete(key)};}
  addEventListener(name,fn){this.events[name]=fn;}
  querySelector(selector){return this.children[selector]||null;}
  querySelectorAll(selector){return this.groups[selector]||[];}
  setAttribute(name,value){this.attrs[name]=value;}
}

function boot({reduce=false,saved='playing'}={}){
  const control=new Node(),scene=new Node(),goal=new Node(),journey=new Node(),doc=new Node();
  const scenes=['search','social','website'];
  scene.groups['[data-scene-choice]']=scenes.map(k=>new Node({sceneChoice:k}));
  scene.groups['[data-scene-panel]']=scenes.map(k=>new Node({scenePanel:k}));
  goal.groups['[data-goal]']=scenes.map(k=>new Node({goal:k}));
  goal.groups['[data-goal-picture]']=scenes.map(k=>new Node({goalPicture:k}));
  for(const selector of ['[data-goal-title]','[data-goal-description]','[data-goal-link]'])goal.children[selector]=new Node();
  journey.groups['[data-journey-choice]']=['0','1','2'].map(k=>new Node({journeyChoice:k}));
  journey.groups['[data-journey-panel]']=['0','1','2'].map(k=>new Node({journeyPanel:k}));
  const art=new Node();
  doc.groups={'[data-motion-toggle]':[control],'[data-scene-switcher]':[scene],'[data-goal-picker]':[goal],'[data-journey]':[journey],'.motion-stage':[art]};
  doc.documentElement=new Node();doc.visibilityState='visible';
  let observerCallback;
  const preference={matches:reduce,addEventListener:(name,fn)=>{preference.change=fn}};
  const storage=new Map([['digitaltalha-motion',saved]]);
  const window={matchMedia:()=>preference,localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},IntersectionObserver:true};
  class IntersectionObserver{constructor(callback){observerCallback=callback}observe(){}}
  vm.runInNewContext(code,{document:doc,window,IntersectionObserver});
  return {control,scene,goal,journey,doc,art,preference,storage,intersect:visible=>observerCallback([{target:art,isIntersecting:visible}])};
}

let app=boot();
app.scene.groups['[data-scene-choice]'][0].events.click();
assert.equal(app.scene.groups['[data-scene-panel]'][0].hidden,false);
assert.equal(app.scene.groups['[data-scene-panel]'][1].hidden,true);
assert.equal(app.scene.groups['[data-scene-choice]'][0].attrs['aria-pressed'],'true');
for(const [index,title,url] of [[0,'Google Ads','/google-ads/'],[1,'Meta Ads','/meta-ads/'],[2,'Website Creation','/website-creation/']]){
  app.goal.groups['[data-goal]'][index].events.click();
  assert.equal(app.goal.children['[data-goal-title]'].textContent,title);
  assert.equal(app.goal.children['[data-goal-link]'].attrs.href,url);
  assert.equal(app.goal.groups['[data-goal-picture]'][index].hidden,false);
  assert.equal(app.goal.groups['[data-goal-picture]'].filter(p=>!p.hidden).length,1);
}
app.journey.groups['[data-journey-choice]'][2].events.click();
assert.equal(app.journey.groups['[data-journey-panel]'][2].hidden,false);
assert.equal(app.journey.groups['[data-journey-panel]'].filter(p=>!p.hidden).length,1);
app.control.events.click();assert.equal(app.doc.documentElement.dataset.motion,'paused');assert.equal(app.storage.get('digitaltalha-motion'),'paused');
app.control.events.click();assert.equal(app.doc.documentElement.dataset.motion,'playing');
app.intersect(true);assert(app.art.classes.has('is-scene-visible'));
app.intersect(false);assert(!app.art.classes.has('is-scene-visible'));
app.doc.visibilityState='hidden';app.doc.events.visibilitychange();assert.equal(app.doc.documentElement.dataset.documentHidden,'true');
app=boot({reduce:true});assert.equal(app.doc.documentElement.dataset.motion,'paused');assert.equal(app.control.disabled,true);assert.equal(app.control.textContent,'Motion reduced');
app=boot({saved:'paused'});assert.equal(app.doc.documentElement.dataset.motion,'paused');assert.equal(app.control.textContent,'Play motion');
console.log('PASS: service scenes, all goal recommendations, process switching, pause persistence, reduced motion, offscreen animation state and background-tab pausing.');
