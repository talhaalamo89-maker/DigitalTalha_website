(() => {
  const menu = document.querySelector('[data-menu]');
  const nav = document.querySelector('#primary-nav');
  const closeMenu = () => { if (!menu) return; menu.setAttribute('aria-expanded', 'false'); nav.classList.remove('is-open'); };
  menu?.addEventListener('click', () => { const open = menu.getAttribute('aria-expanded') !== 'true'; menu.setAttribute('aria-expanded', String(open)); nav.classList.toggle('is-open', open); });
  document.addEventListener('keydown', event => { if(event.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') { closeMenu(); menu.focus(); } });
  nav?.addEventListener('click', event => { if(event.target.closest('a')) closeMenu(); });
  window.matchMedia('(min-width: 861px)').addEventListener('change', closeMenu);
  document.querySelectorAll('.faq details').forEach(detail => detail.addEventListener('toggle', () => { if(detail.open) document.querySelectorAll('.faq details').forEach(other => { if(other!==detail) other.open=false; }); }));
  const search = document.querySelector('[data-project-search]');
  const result = document.querySelector('[data-search-result]');
  search?.addEventListener('input', () => { const query=search.value.trim().toLowerCase(); let count=0; document.querySelectorAll('[data-project]').forEach(card => { const match=card.textContent.toLowerCase().includes(query); card.hidden=!match; count+=Number(match); }); result.textContent = count ? `${count} project${count===1?'':'s'} found` : 'No projects match your search. Try “Meta” or “campaign”.'; });
  document.querySelectorAll('[data-copy-email]').forEach(button => button.addEventListener('click', async () => { try { await navigator.clipboard.writeText('talhaalamo89@gmail.com'); button.textContent='Copied!'; } catch { button.textContent='talhaalamo89@gmail.com'; } }));
  document.querySelectorAll('[data-enquiry]').forEach(form => {
    const status=form.querySelector('[role="status"]');
    const submit=form.querySelector('[type="submit"]');
    form.addEventListener('submit', async event => {
      event.preventDefault(); if(!form.reportValidity()) return;
      submit.disabled=true; submit.textContent='Sending…'; status.textContent=''; status.classList.remove('error');
      try {
        const response=await fetch('/api/enquiry.php', {method:'POST',body:new FormData(form),headers:{Accept:'application/json'}});
        const type=response.headers.get('content-type')||'';
        if(!type.includes('application/json')) throw new Error('Enquiry delivery is unavailable here. Please use WhatsApp or email below.');
        const data=await response.json();
        if(!response.ok || !data.ok) throw new Error(data.message||'Your enquiry could not be sent. Please try WhatsApp or email.');
        status.textContent='Enquiry sent successfully. Thanks for reaching out. I’ll review your details and get back to you.';
        form.reset();
        window.dataLayer=window.dataLayer||[]; window.dataLayer.push({event:'generate_lead',form_id:form.id,service:form.dataset.service||'general'});
      } catch(error) { status.classList.add('error'); status.textContent=error.message || 'Could not send. Please use WhatsApp or email.'; }
      finally { submit.disabled=false; submit.textContent=submit.dataset.label; }
    });
  });
  document.querySelector('[data-back-top]')?.addEventListener('click', () => window.scrollTo({top:0,behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'}));
  if('IntersectionObserver' in window) {
    const reveal=new IntersectionObserver(entries => entries.forEach(entry => { if(entry.isIntersecting) {entry.target.classList.add('is-visible'); reveal.unobserve(entry.target);} }),{threshold:.08});
    document.querySelectorAll('[data-reveal]').forEach(el => reveal.observe(el));
  }
})();
