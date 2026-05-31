/* ============================================
   LOGISTORIA — MAIN JAVASCRIPT
   ============================================ */

// ============================================
// PARTICLE CANVAS (Hero)
// ============================================
(function() {
  const canvas = document.getElementById('particleCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  let w, h, dpr;
  let particles = [];
  let mouse = { x: -9999, y: -9999 };
  let frames = 0;
  let animId;

  function resize() {
    const parent = canvas.parentElement;
    w = parent.offsetWidth;
    h = parent.offsetHeight;
    dpr = window.devicePixelRatio || 1;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function createParticles() {
    particles = [];
    const count = w < 768 ? 50 : 80;
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.8,
        vy: (Math.random() - 0.5) * 0.8,
        r: 2 + Math.random() * 2,
        ph: Math.random() * Math.PI * 2
      });
    }
  }

  function animate() {
    ctx.clearRect(0, 0, w, h);
    frames++;
    const t = frames / 60;
    const ga = Math.min(1, frames / 120);
    ctx.globalAlpha = ga;

    // Update positions
    for (const p of particles) {
      p.x += p.vx + Math.sin(p.ph + t * 0.5) * 0.3;
      p.y += p.vy + Math.cos(p.ph + t * 0.3) * 0.2;
      if (p.x < -40) p.x = w + 40;
      if (p.x > w + 40) p.x = -40;
      if (p.y < -40) p.y = h + 40;
      if (p.y > h + 40) p.y = -40;

      // Mouse repel
      const dx = p.x - mouse.x;
      const dy = p.y - mouse.y;
      const dist = Math.hypot(dx, dy);
      if (dist < 150 && dist > 0) {
        const force = (1 - dist / 150) * 0.5;
        p.x += (dx / dist) * force;
        p.y += (dy / dist) * force;
      }
    }

    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const ddx = particles[i].x - particles[j].x;
        const ddy = particles[i].y - particles[j].y;
        const dist = Math.hypot(ddx, ddy);
        if (dist < 120) {
          const opacity = (1 - dist / 120) * 0.3;
          if (opacity > 0.05) {
            ctx.beginPath();
            ctx.strokeStyle = `rgba(255,200,100,${opacity})`;
            ctx.lineWidth = 0.5;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }
    }

    // Draw particles
    for (const p of particles) {
      const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 2);
      g.addColorStop(0, 'rgba(255,255,255,0.9)');
      g.addColorStop(1, 'rgba(255,200,100,0.8)');
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = g;
      ctx.shadowBlur = 10;
      ctx.shadowColor = 'rgba(255,160,0,0.6)';
      ctx.fill();
      ctx.shadowBlur = 0;
    }

    ctx.globalAlpha = 1;
    animId = requestAnimationFrame(animate);
  }

  // Mouse tracking
  canvas.addEventListener('mousemove', function(e) {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  });
  canvas.addEventListener('mouseleave', function() {
    mouse.x = -9999;
    mouse.y = -9999;
  });

  // Init
  resize();
  createParticles();
  animate();

  window.addEventListener('resize', function() {
    resize();
    createParticles();
  });
})();

// ============================================
// MOBILE MENU
// ============================================
(function() {
  const toggle = document.getElementById('navToggle');
  const close = document.getElementById('mobileClose');
  const menu = document.getElementById('mobileMenu');
  const overlay = document.getElementById('mobileOverlay');
  const links = menu.querySelectorAll('.mobile-link');

  function open() { menu.classList.add('open'); overlay.classList.add('open'); document.body.style.overflow = 'hidden'; }
  function closeMenu() { menu.classList.remove('open'); overlay.classList.remove('open'); document.body.style.overflow = ''; }

  if (toggle) toggle.addEventListener('click', open);
  if (close) close.addEventListener('click', closeMenu);
  if (overlay) overlay.addEventListener('click', closeMenu);
  links.forEach(l => l.addEventListener('click', closeMenu));
})();

// ============================================
// NAV SCROLL EFFECT
// ============================================
(function() {
  const nav = document.getElementById('nav');
  if (!nav) return;
  window.addEventListener('scroll', function() {
    nav.classList.toggle('scrolled', window.scrollY > 100);
  }, { passive: true });
})();

// ============================================
// SMOOTH ANCHOR SCROLLING
// ============================================
(function() {
  document.querySelectorAll('a[href^="#"]').forEach(function(a) {
    a.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        const top = target.getBoundingClientRect().top + window.scrollY - 72;
        window.scrollTo({ top: top, behavior: 'smooth' });
      }
    });
  });
})();

// ============================================
// SCROLL REVEAL ANIMATIONS
// ============================================
(function() {
  const reveals = document.querySelectorAll('.stat-card, .game-card, .audience-card, .pricing-card, .partner-logo, .gallery-item, .blog-card, .faq-item');

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry, index) {
      if (entry.isIntersecting) {
        const el = entry.target;
        const siblings = Array.from(el.parentElement.children);
        const i = siblings.indexOf(el);
        setTimeout(function() {
          el.classList.add('visible');
        }, i * 100);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -80px 0px' });

  reveals.forEach(function(el) {
    if (el.classList.contains('stat-card')) {
      el.style.transitionDelay = '0s';
    }
    observer.observe(el);
  });
})();

// ============================================
// GAME FILTER
// ============================================
(function() {
  const tabs = document.querySelectorAll('.filter-tab');
  const cards = document.querySelectorAll('.game-card');
  if (!tabs.length || !cards.length) return;

  tabs.forEach(function(tab) {
    tab.addEventListener('click', function() {
      const filter = this.dataset.filter;

      // Update active tab
      tabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');

      // Filter cards
      cards.forEach(function(card) {
        const cats = (card.dataset.category || '').split(' ');
        if (filter === 'all' || cats.includes(filter)) {
          card.style.display = '';
          setTimeout(function() {
            card.style.opacity = '1';
            card.style.transform = 'scale(1)';
          }, 50);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'scale(0.95)';
          setTimeout(function() {
            card.style.display = 'none';
          }, 200);
        }
      });
    });
  });
})();

// ============================================
// FAQ ACCORDION
// ============================================
(function() {
  const items = document.querySelectorAll('.faq-item');
  if (!items.length) return;

  items.forEach(function(item) {
    const question = item.querySelector('.faq-question');
    if (!question) return;

    question.addEventListener('click', function() {
      const isActive = item.classList.contains('active');

      // Close all
      items.forEach(function(i) { i.classList.remove('active'); });

      // Open clicked if wasn't active
      if (!isActive) {
        item.classList.add('active');
      }
    });
  });
})();

// ============================================
// HERO SCROLL INDICATOR FADE
// ============================================
(function() {
  const indicator = document.querySelector('.hero-scroll');
  if (!indicator) return;
  window.addEventListener('scroll', function() {
    const vh = window.innerHeight * 0.5;
    indicator.style.opacity = Math.max(0, 1 - window.scrollY / vh);
  }, { passive: true });
})();

// ============================================
// DEMO REQUEST MODAL
// ============================================
(function() {
  const modal = document.getElementById('demoModal');
  if (!modal) return;

  window.openDemoModal = function() {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  };
  window.closeDemoModal = function() {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  };

  modal.addEventListener('click', function(e) {
    if (e.target === modal) closeDemoModal();
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modal.classList.contains('open')) closeDemoModal();
  });

  if (window.location.search.includes('demo=thanks')) {
    setTimeout(function() {
      alert('Спасибо! Ваш запрос отправлен. Мы свяжемся с вами в течение дня.');
      window.history.replaceState({}, document.title, window.location.pathname);
    }, 500);
  }

  window.handleDemoSubmit = function(e) {
    // Let the form submit natively to FormSubmit.co
    return true;
  };
})();

// ============================================
// SUBMIT GAME MODAL
// ============================================
(function() {
  const modal = document.getElementById('submitGameModal');
  if (!modal) return;

  window.openSubmitGameModal = function() {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  };
  window.closeSubmitGameModal = function() {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  };

  modal.addEventListener('click', function(e) {
    if (e.target === modal) closeSubmitGameModal();
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modal.classList.contains('open')) closeSubmitGameModal();
  });

  window.handleSubmitGame = function(e) {
    // Let the form submit natively to FormSubmit.co
    return true;
  };
})();

// ============================================
// SUBSCRIBE MODAL
// ============================================
(function() {
  const modal = document.getElementById('subscribeModal');
  if (!modal) return;

  window.openSubscribeModal = function() {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  };
  window.closeSubscribeModal = function() {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  };

  modal.addEventListener('click', function(e) {
    if (e.target === modal) closeSubscribeModal();
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modal.classList.contains('open')) closeSubscribeModal();
  });

  window.handleSubscribe = function(e) {
    e.preventDefault();
    const name = document.getElementById('subName').value;
    const email = document.getElementById('subEmail').value;
    const company = document.getElementById('subCompany').value;
    const plan = document.getElementById('subPlan').value;
    const planText = plan === 'pro' ? 'ПРО — ₽280 тыс/год' : 'БАЗОВЫЙ — ₽100 тыс/год';
    const subject = 'Заявка на подписку — ' + planText;
    const body = 'Имя: ' + name + '\nEmail: ' + email + '\nКомпания: ' + company + '\nТариф: ' + planText;
    window.location.href = 'mailto:project@logistoria.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    closeSubscribeModal();
    setTimeout(function() {
      alert('Спасибо! Открылся почтовый клиент с готовым письмом. Просто нажмите «Отправить».');
    }, 300);
    return false;
  };
})();
