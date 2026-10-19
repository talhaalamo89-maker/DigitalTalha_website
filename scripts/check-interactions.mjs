import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const code=fs.readFileSync(new URL('../assets/site.js',import.meta.url),'utf8');
class Element {
  constructor(){this.events={};this.dataset={};this.attrs={};this.textContent='';this.value='';this.hidden=false;this.disabled=false;this.classes=new Set();this.classList={add:x=>this.classes.add(x),remove:x=>this.classes.delete(x),toggle:(x,v)=>v?this.classes.add(x):this.classes.delete(x)};}
  addEventListener(event,fn){this.events[event]=fn;}
  setAttribute(k,v){this.attrs[k]=v;}
  getAttribute(k){return this.attrs[k];}
  focus(){this.focused=true;}
}
function setup(fetch){
  const menu=new Element(),nav=new Element(),form=new Element(),status=new Element(),submit=new Element(),search=new Element(),result=new Element(),card=new Element();
  card.textContent='Meta Lead Campaign — From Start to Finish';
  form.id='enquiry';form.dataset.service='Meta Ads';form.querySelector=s=>s==='[role="status"]'?status:submit;form.reportValidity=()=>true;form.reset=()=>{form.resetCalled=true};submit.dataset.label='Send My Enquiry';
  const nodes={'[data-menu]':menu,'#primary-nav':nav,'[data-project-search]':search,'[data-search-result]':result};
  const document={querySelector:s=>nodes[s]||null,querySelectorAll:s=>s==='[data-enquiry]'?[form]:s==='[data-project]'?[card]:[],addEventListener:(event,fn)=>{document[event]=fn}};
  const window={matchMedia:()=>({matches:false,addEventListener:()=>{}})};
  vm.runInNewContext(code,{document,window,navigator:{},fetch,FormData:class {constructor(form){this.form=form}},console});
  return {menu,nav,form,status,submit,search,result,card,document,window};
}
let p=setup(async()=>({ok:false,headers:{get:()=> 'application/json'},json:async()=>({ok:false,message:'Delivery failed.'})}));
await p.form.events.submit({preventDefault(){}});
assert.equal(p.status.textContent,'Delivery failed.');assert.equal(p.submit.disabled,false);assert.equal(p.window.dataLayer,undefined);assert.equal(p.form.resetCalled,undefined);
p.menu.events.click();assert.equal(p.menu.getAttribute('aria-expanded'),'true');assert(p.nav.classes.has('is-open'));
p.document.keydown({key:'Escape'});assert.equal(p.menu.getAttribute('aria-expanded'),'false');assert(p.menu.focused);
p.search.value='unmatched search';p.search.events.input();assert.equal(p.card.hidden,true);assert.match(p.result.textContent,/No projects/);
p.search.value='meta';p.search.events.input();assert.equal(p.card.hidden,false);assert.equal(p.result.textContent,'1 project found');
p=setup(async()=>({ok:true,headers:{get:()=> 'application/json'},json:async()=>({ok:true})}));
await p.form.events.submit({preventDefault(){}});
assert.equal(p.form.resetCalled,true);assert.equal(p.window.dataLayer[0].event,'generate_lead');assert.equal(p.submit.disabled,false);
p=setup(async()=>({ok:true,headers:{get:()=> 'text/html'}}));
await p.form.events.submit({preventDefault(){}});assert.equal(p.window.dataLayer,undefined);assert.match(p.status.textContent,/unavailable/);
console.log('PASS: enquiry success/failure paths, no false lead events, submission recovery, navigation Escape handling, and project search.');
